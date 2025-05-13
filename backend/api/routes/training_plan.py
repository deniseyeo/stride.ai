from fastapi import APIRouter, Request
from services.training_plan_service import create_plan

router = APIRouter()


@router.post("/createplan")
async def plan_endpoint(request: Request):
    data = await request.json()
    prompt = data.get("message", "")
    preferences = data.get("preferences", {})
    goals = data.get("goals", {})
    response = create_plan(prompt, preferences, goals)
    return {"response": response}
