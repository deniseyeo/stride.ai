import os
from datetime import datetime
from typing import List

from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from models.workout import Workout, WorkoutCreate
from services.strava_service import StravaService

router = APIRouter(tags=["strava"])


STRAVA_CLIENT_ID = os.environ.get("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.environ.get("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.environ.get("STRAVA_REDIRECT_URI")
FRONTEND_URL = os.environ.get("FRONTEND_URL")

if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET:
    raise ValueError("STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set")

strava_service = StravaService(STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET)


@router.get("/auth")
async def authorize_strava():
    """Redirect to Strava authorization page"""
    redirect_uri = STRAVA_REDIRECT_URI
    auth_url = strava_service.get_authorization_url(redirect_uri)
    return RedirectResponse(auth_url)


@router.get("/callback")
async def strava_callback(
    request: Request,
    code: str,
):
    try:
        token_data = strava_service.exchange_token(code)

        request.session["access_token"] = token_data["access_token"]
        request.session["refresh_token"] = token_data["refresh_token"]
        request.session["expires_at"] = token_data["expires_at"]

        athlete = token_data.get("athlete", {})
        user_id = f"strava_{athlete.get('id', 'default')}"
        request.session["user_id"] = user_id

        return RedirectResponse(
            f"{FRONTEND_URL}?strava_connected=true&view=history", status_code=303
        )

    except Exception as e:
        return RedirectResponse(
            f"{FRONTEND_URL}?strava_error={str(e)}", status_code=303
        )


@router.delete("/disconnect")
async def disconnect_strava(request: Request, db=Depends(get_db)):
    """Disconnect Strava integration"""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Delete Strava auth from database
    db.execute("DELETE FROM strava_auth WHERE user_id = :user_id", {"user_id": user_id})
    db.execute("DELETE FROM workouts")
    db.commit()

    return {"message": "Strava disconnected successfully"}


@router.get("/workouts", response_model=List[Workout])
async def get_workouts(
    request: Request,

    db=Depends(get_db),
):
    access_token = request.session.get("access_token")
    refresh_token = request.session.get("refresh_token")
    expires_at = request.session.get("expires_at")
    user_id = request.session.get("user_id")

    if not access_token or not refresh_token or not expires_at or not user_id:
        raise HTTPException(
            status_code=401, detail="Missing authentication session data"
        )

    if strava_service.is_token_expired(expires_at):
        token_data = strava_service.refresh_access_token(refresh_token)

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_at = token_data.get("expires_at")

        if not access_token or not refresh_token or not expires_at:
            raise HTTPException(
                status_code=500, detail="Invalid token refresh response"
            )

        request.session["access_token"] = access_token
        request.session["refresh_token"] = refresh_token
        request.session["expires_at"] = expires_at

        db.execute(
            """
            UPDATE strava_auth 
            SET access_token = :access_token, 
                refresh_token = :refresh_token, 
                expires_at = :expires_at
            WHERE user_id = :user_id
            """,
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "user_id": user_id,
            },
        )
        db.commit()

    all_activities = []
    page = 1
    per_page = 200  # Maximum allowed by Strava API

    while True:
        strava_activities = strava_service.get_athlete_activities(
            access_token=access_token, per_page=per_page, page=page
        )

        if not strava_activities:
            break

        all_activities.extend(strava_activities)
        page += 1

    workouts = []
    for activity in all_activities:
        workout_data = WorkoutCreate(
            strava_id=str(activity["id"]),
            user_id=user_id,
            name=activity["name"],
            distance=activity["distance"] / 1000,
            moving_time=activity["moving_time"] / 60,
            total_elevation_gain=activity["total_elevation_gain"],
            type=activity["type"],
            start_date=datetime.fromisoformat(
                activity["start_date"].replace("Z", "+00:00")
            ).date(),
            average_pace=(
                (activity["moving_time"] / 60) / (activity["distance"] / 1000)
                if activity["distance"]
                else 0
            ),
            average_heartrate=activity.get("average_heartrate"),
            max_heartrate=activity.get("max_heartrate"),
        )

        existing = db.execute(
            "SELECT id FROM workouts WHERE strava_id = :strava_id",
            {"strava_id": workout_data.strava_id},
        ).fetchone()

        if existing:
            workout_id = existing["id"]
            db.execute(
                "UPDATE workouts SET name = :name WHERE id = :id",
                {"name": workout_data.name, "id": workout_id},
            )
            workout = Workout(id=workout_id, **workout_data.dict())
        else:
            result = db.execute(
                """
                INSERT INTO workouts (
                    strava_id, user_id, name, distance, moving_time, 
                    total_elevation_gain, type, start_date,
                    average_pace, average_heartrate, max_heartrate
                ) VALUES (
                    :strava_id, :user_id, :name, :distance, :moving_time, 
                    :total_elevation_gain, :type, :start_date,
                    :average_pace, :average_heartrate, :max_heartrate
                ) RETURNING id
                """,
                workout_data.dict(),
            )
            workout_id = result.fetchone()["id"]
            workout = Workout(id=workout_id, **workout_data.dict())

        workouts.append(workout)

    db.commit()
    return workouts
