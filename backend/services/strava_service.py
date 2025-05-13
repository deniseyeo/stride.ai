from datetime import datetime
from typing import Any, Dict, List, Optional

import requests


class StravaService:
    """Service for interacting with the Strava API"""

    BASE_URL = "https://www.strava.com/api/v3"
    AUTH_URL = "https://www.strava.com/oauth/token"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_authorization_url(self, redirect_uri: str) -> str:
        """Generate the Strava authorization URL for OAuth flow"""
        return (
            f"https://www.strava.com/oauth/authorize"
            f"?client_id={self.client_id}"
            f"&response_type=code"
            f"&redirect_uri={redirect_uri}"
            f"&approval_prompt=force"
            f"&scope=read,activity:read"
        )

    def exchange_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
        }

        response = requests.post(self.AUTH_URL, data=data)
        if response.status_code != 200:
            raise Exception(f"Failed to exchange token: {response.text}")

        return response.json()

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(self.AUTH_URL, data=data)
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")

        return response.json()

    def get_athlete_activities(
        self,
        access_token: str,
        after: Optional[datetime] = None,
        before: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 200,
    ) -> List[Dict[str, Any]]:
        """Get athlete activities with optional date filtering"""
        headers = {"Authorization": f"Bearer {access_token}"}

        params = {"page": page, "per_page": per_page}

        if after:
            params["after"] = int(after.timestamp())

        if before:
            params["before"] = int(before.timestamp())

        url = f"{self.BASE_URL}/athlete/activities"
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to get activities: {response.text}")

        return response.json()

    def get_activity_detail(
        self, access_token: str, activity_id: str
    ) -> Dict[str, Any]:
        """Get detailed information about a specific activity"""
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.BASE_URL}/activities/{activity_id}"

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to get activity detail: {response.text}")

        return response.json()

    def is_token_expired(self, expires_at: int) -> bool:
        """Check if a token is expired"""
        # Add a small buffer to ensure we refresh slightly before expiration
        buffer_seconds = 300  # 5 minutes
        return datetime.now().timestamp() >= (expires_at - buffer_seconds)
