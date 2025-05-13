import React, { useState, useEffect } from 'react';
import GoalForm from '@components/GoalForm';
import GoalList from '@components/GoalList';
import WorkoutHistory from '@components/WorkoutHistory';
import { RunningGoal } from './types/index';
import { WorkoutData } from './types/workout';
import { TrainingPreferences } from './types/preferences';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import PreferencesForm from '@components/PreferencesForm';
import TrainingPlanViewer from '@components/TrainingPlanViewer';
import { TrainingPlans } from './types/trainingplans';


const App: React.FC = () => {
  return (
    <Router>
      <AppContent />
    </Router>
  );
};

const AppContent: React.FC = () => {
  const navigate = useNavigate();
  const [goals, setGoals] = useState<RunningGoal[]>(() => {
    const savedGoals = localStorage.getItem('runningGoals');
    return savedGoals ? JSON.parse(savedGoals) : [];
  });

  const [preferences, setPreferences] = useState<TrainingPreferences[]>(() => {
    const savedPreferences = localStorage.getItem('trainingPreferences');
    return savedPreferences ? JSON.parse(savedPreferences) : [];
  });
  
  const [trainingPlans, setTrainingPlans] = useState<TrainingPlans[]>(() => {
    const savedPlans = localStorage.getItem('trainingPlans');
    return savedPlans ? JSON.parse(savedPlans) : [];
  });
  
  const [workouts, setWorkouts] = useState<WorkoutData[]>([]);
  const [isStravaConnected, setIsStravaConnected] = useState<boolean>(false);
  const [viewMode, setViewMode] = useState<'create' | 'list' | 'history' | 'plan'>('create');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Save goals to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('runningGoals', JSON.stringify(goals));
  }, [goals]);
  
  // Save training plans to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('trainingPlans', JSON.stringify(trainingPlans));
  }, [trainingPlans]);

  // Initial setup and Strava authentication handling
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const stravaConnected = urlParams.get('strava_connected');
    const stravaError = urlParams.get('strava_error');
    const viewParam = urlParams.get('view');

    if (stravaConnected === 'true') {
      console.log('Strava connected successfully!');
      setIsStravaConnected(true);
      localStorage.setItem('stravaConnected', 'true');
      
      if (viewParam === 'history') {
        setViewMode('history');
      }
      
      // Only fetch workout data when explicitly connected through Strava
      fetchWorkoutData();
      
      // Clean up URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (stravaError) {
      console.error('Strava connection error:', stravaError);
      alert(`Failed to connect to Strava: ${stravaError}`);
      window.history.replaceState({}, document.title, window.location.pathname);
    } else {
      // Check if we have a previously established connection that needs to be verified
      const previouslyConnected = localStorage.getItem('stravaConnected') === 'true';
      if (previouslyConnected) {
        // Verify the connection is still valid
        checkStravaConnection();
      }
    }
  }, []);

  // Function to check if Strava connection is still valid without fetching full workout data
  const checkStravaConnection = async () => {
    try {
      setIsLoading(true);
    } catch (error) {
      console.error('Error checking Strava connection:', error);
      setIsStravaConnected(false);
      localStorage.removeItem('stravaConnected');
    } finally {
      setIsLoading(false);
    }
  };

  // Function to fetch workout data from Strava
  const fetchWorkoutData = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8080/workouts', {
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setWorkouts(data);
        setIsStravaConnected(true);
        localStorage.setItem('stravaConnected', 'true');
      } else if (response.status === 401 || response.status === 403 || response.status === 404) {
        setIsStravaConnected(false);
        localStorage.removeItem('stravaConnected');

        if (response.status === 404) {
          alert('Strava connection not found. Please connect to Strava again.');
        }
      } else {
        console.error('Error fetching workouts:', await response.text());
      }
    } catch (error) {
      console.error('Error fetching workout data:', error);
      setIsStravaConnected(false);
      localStorage.removeItem('stravaConnected');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddGoal = (goal: RunningGoal) => {
    setGoals([...goals, goal]);
    setViewMode('list');
  };

  const handleDeleteGoal = (id: string) => {
    setGoals(goals.filter(goal => goal.id !== id));

    const updatedPreferences = preferences.filter(pref => pref.id !== id);
    setPreferences(updatedPreferences);
    localStorage.setItem('trainingPreferences', JSON.stringify(updatedPreferences));

    const updatedPlans = trainingPlans.filter(plan => plan.id !== id);
    setTrainingPlans(updatedPlans);
    localStorage.setItem('trainingPlans', JSON.stringify(updatedPlans));
  };

  const handleConnectStrava = () => {
    window.location.href = 'http://localhost:8080/auth';
  };

  const handleDisconnectStrava = async () => {
    try {
      const response = await fetch('http://localhost:8080/disconnect', {
        method: 'DELETE',
        credentials: 'include'
      });

      if (response.ok) {
        setIsStravaConnected(false);
        localStorage.removeItem('stravaConnected');
        setWorkouts([]);
        alert('Strava disconnected successfully');
      } else {
        console.error('Error disconnecting Strava:', await response.text());
      }
    } catch (error) {
      console.error('Error disconnecting Strava:', error);
    }
  };

  const handleAddPreferences = (preference: TrainingPreferences) => {
    const updatedPreferences = preferences.filter(p => p.id !== preference.id);
    updatedPreferences.push(preference);
    setPreferences(updatedPreferences);
    localStorage.setItem('trainingPreferences', JSON.stringify(updatedPreferences));
    navigate(-1);
  };

  const handleAddTrainingPlans = (plan: TrainingPlans) => {
    const updatedPlans = trainingPlans.filter(p => p.id !== plan.id);
    updatedPlans.push(plan);
    setTrainingPlans(updatedPlans);
    localStorage.setItem('trainingPlans', JSON.stringify(updatedPlans)); // Fixed key to match useState
  };

  return (
    <div className="p-6 w-full max-w-screen-lg mx-auto bg-gray-50 rounded-lg shadow-md overflow-x-auto">
      <h1 className="text-3xl font-bold text-center mb-6 text-blue-800">Stride</h1>

      <div className="flex justify-center mb-4">
        <div className="flex space-x-2">
          <button 
            className={`px-4 py-2 rounded-lg ${viewMode === 'create' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            onClick={() => {
              navigate('/');
              setViewMode('create');
            }}
          >
            Create Goal
          </button>
          <button 
            className={`px-4 py-2 rounded-lg ${viewMode === 'list' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            onClick={() => {
              navigate('/');
              setViewMode('list');
            }}
          >
            My Goals ({goals.length})
          </button>
          <button 
            className={`px-4 py-2 rounded-lg ${viewMode === 'history' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            onClick={() => {
              navigate('/');
              setViewMode('history');
            }}
          >
            Workout History
          </button>
        </div>
      </div>

      <Routes>
        <Route path="/" element={
          <>
            {viewMode === 'create' && <GoalForm onAddGoal={handleAddGoal} />}
            {viewMode === 'list' && (
              <GoalList 
                goals={goals}
                onDeleteGoal={handleDeleteGoal}
                onCreateGoal={() => setViewMode('create')}
                trainingPlans={trainingPlans}
              />
            )}
            {viewMode === 'history' && (
              <WorkoutHistory
                workouts={workouts}
                isStravaConnected={isStravaConnected}
                isLoading={isLoading}
                onConnectStrava={handleConnectStrava}
                onDisconnectStrava={handleDisconnectStrava}
                onRefreshData={fetchWorkoutData}
              />
            )}
          </>
        } />
        <Route 
          path="/preferences" 
          element={<PreferencesForm preferences={preferences} onSavePreferences={handleAddPreferences} />} 
        />
        <Route 
          path="/plan" 
          element={
            <TrainingPlanViewer 
            goals={goals}
            preferences={preferences}
            trainingPlans={trainingPlans} 
            generateOnLoad={false} 
            onSaveTrainingPlan={handleAddTrainingPlans} 
            />
          } 
        />
      </Routes>
    </div>
  );
};

export default App;