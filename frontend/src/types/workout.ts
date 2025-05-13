export interface WorkoutData {
  id: string;
  name: string;
  distance: number;       // in meters
  moving_time: number;    // in seconds
  elapsed_time: number;   // in seconds
  total_elevation_gain: number;  // in meters
  type: string;           // e.g., "Run", "Ride"
  start_date: string;     // ISO date string
  average_pace: number;  // in meters/second
  max_speed: number;      // in meters/second
  start_latlng: [number, number] | null;
  end_latlng: [number, number] | null;
  average_heartrate?: number;
  max_heartrate?: number;
}

// You might also need this for the Strava API authentication
export interface StravaAuth {
  access_token: string;
  refresh_token: string;
  expires_at: number;
  athlete: {
    id: number;
    username: string;
    firstname: string;
    lastname: string;
  };
}