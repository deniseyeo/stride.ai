import React from 'react';
import { WorkoutData } from '../types/workout';
import { FaSpinner } from 'react-icons/fa';


interface WorkoutHistoryProps {
  workouts: WorkoutData[];
  isStravaConnected: boolean;
  isLoading: boolean;
  onConnectStrava: () => void;
  onDisconnectStrava: () => void;
  onRefreshData: () => void;
}

const WorkoutHistory: React.FC<WorkoutHistoryProps> = ({
  workouts,
  isStravaConnected,
  isLoading,
  onConnectStrava,
  onDisconnectStrava,
  onRefreshData
}) => {
  
  const formatDistance = (meters: number): string => {
    return (meters).toFixed(2) + ' km';
  };

  const formatPace = (minPerKm: number): string => {
    const minutes = Math.floor(minPerKm);
    const seconds = Math.round((minPerKm - minutes) * 60);
    const paddedSeconds = seconds.toString().padStart(2, '0');
    return `${minutes}:${paddedSeconds} min/km`;
  };
  

  const formatTime = (minutes: number): string => {
    const totalSeconds = Math.round(minutes * 60);
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    const secs = totalSeconds % 60;
  
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleConnectStrava = async () => {
    try {
      await onConnectStrava();
      await onRefreshData();
    } catch (error) {
      console.error("Error connecting to Strava:", error);

    }
  };
  
  const handleDisconnectStrava = async () => {
    try {
      await onDisconnectStrava();
    } catch (error) {
      console.error("Error disconnecting from Strava:", error);
    }
  };
  
  const handleRefreshData = async () => {
    try {
      await onRefreshData();
    } catch (error) {
      console.error("Error refreshing data:", error);
    }
  };
  
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold">Your Workout History</h2>
        <div className="space-x-2">
          {isStravaConnected ? (
            <>
              <button 
                onClick={handleRefreshData}
                disabled={isLoading}
                className={`px-4 py-2 ${isLoading ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'} text-white rounded-lg`}
              >
                {isLoading ? (<>
                <FaSpinner className="animate-spin h-4 w-4" />
                <span>Loading...</span>
              </>
            ) : 'Refresh Data'}
              </button>
              <button 
                onClick={handleDisconnectStrava}
                disabled={isLoading}
                className={`px-4 py-2 ${isLoading ? 'bg-gray-400' : 'bg-red-500 hover:bg-red-600'} text-white rounded-lg`}
              >
                {isLoading ? (<>
                <FaSpinner className="animate-spin h-4 w-4" />
                <span>Loading...</span>
              </>
            ) : 'Disconnect Strava'}
              </button>
            </>
          ) : (
            <button 
              onClick={handleConnectStrava}
              disabled={isLoading}
              className={`px-4 py-2 ${isLoading ? 'bg-gray-400' : 'bg-orange-500 hover:bg-orange-600'} text-white rounded-lg`}
            >
                              {isLoading ? (<>
                <FaSpinner className="animate-spin h-4 w-4" />
                <span>Loading...</span>
              </>
            ) : 'Connect to Strava'}
            </button>
          )}
        </div>
      </div>
      
      {!isStravaConnected && (
        <div className="text-center py-10">
          <p className="mb-4">Connect your Strava account to see your running history</p>

        </div>
      )}
      
      {isStravaConnected && workouts.length === 0 && !isLoading && (
        <div className="text-center py-10">
          <p>No running activities found in your Strava account.</p>
          <p className="mt-2">Go for a run and sync with Strava, then refresh.</p>
        </div>
      )}
      
      {isStravaConnected && workouts.length > 0 && (
        <div className="overflow-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Distance</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pace</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {workouts.map((workout) => {
                
                return (
                  <tr key={workout.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{workout.start_date}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{workout.name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{workout.type}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatDistance(workout.distance)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatTime(workout.moving_time)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatPace(workout.average_pace)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default WorkoutHistory;
