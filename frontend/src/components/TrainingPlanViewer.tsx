import React, { useState, useEffect } from 'react';
import { TrainingPlans } from '../types/trainingplans';
import { RunningGoal } from '../types/index';
import { FaSpinner } from 'react-icons/fa';
import { useSearchParams } from 'react-router-dom';
import { TrainingPreferences } from '../types/preferences';
import { FaUserPen } from "react-icons/fa6";
import { useNavigate } from 'react-router-dom';

interface TrainingPlanProps {
  goals: RunningGoal[];
  preferences?: TrainingPreferences[];
  trainingPlans: TrainingPlans[];
  generateOnLoad?: boolean;
  onSaveTrainingPlan: (plan: TrainingPlans) => void;
}

const TrainingPlanViewer: React.FC<TrainingPlanProps> = ({ onSaveTrainingPlan, goals, preferences }) => {
  const [response, setResponse] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(false);
  const [isSaved, setIsSaved] = useState<boolean>(false);
  const [searchParams] = useSearchParams();

  const goalId = searchParams.get('id') || 'default';

  const savePlan = () => {
    if (response) {
      const trainingPlans = { id: goalId, trainingPlans: response };
      onSaveTrainingPlan(trainingPlans);  
      setIsSaved(true);
      alert('Training plan saved!');
    }
  };

  const handleGeneratePlan = async () => {
    const message = 'Generate a running training plan';
    setLoading(true);
    setResponse(null);

    const existingPreferences = preferences?.find(preference => preference.id === goalId);
    const existingGoals = goals.find(goal => goal.id === goalId);

    try {
      const res = await fetch('http://localhost:8080/createplan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache',
        },
        body: JSON.stringify({ message, preferences: existingPreferences, goals: existingGoals }),
      });

      if (!res.ok) {
        throw new Error(`Error: ${res.statusText}`);
      }

      const data = await res.json();

      setResponse(data.response);
      setIsSaved(false); 
    } catch (error) {
      setResponse('Failed to fetch plan. Please try again.');
      console.error('Error generating training plan:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const shouldGenerate = searchParams.get('generate') === 'true';
  
    if (shouldGenerate && !isLoading) {
      handleGeneratePlan();
    } else {

      const storedPlans = localStorage.getItem('trainingPlans');
      const existingPlans: TrainingPlans[] = storedPlans ? JSON.parse(storedPlans) : [];
      const existingPlan = existingPlans.find(plan => plan.id === goalId);
  
      if (existingPlan) {
        setResponse(existingPlan.trainingPlans);
        setIsSaved(true);
      }
    }
  }, []);

  const navigate = useNavigate()
  const handleUpdatePreferences = (id: string) => {
    navigate(`/preferences?id=${id}`);
  };
  
  

  return (
    <div className="mt-4">
      <div className="flex space-x-2 mb-4">
        <button
          onClick={handleGeneratePlan}
          disabled={isLoading}
          className={`px-4 py-2 ${isLoading ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'} text-white rounded-lg`}
        >
          {isLoading ? (
            <>
              <FaSpinner className="animate-spin h-4 w-4" />
              <span>Loading...</span>
            </>
          ) : 'Regenerate Plan'}
        </button>
        <button
          onClick={savePlan}
          disabled={!response || isSaved || isLoading}
          className={`px-4 py-2 ${isSaved ? 'bg-green-500' : 'bg-gray-500'} text-white rounded-lg`}
        >
          {isSaved ? 'Saved' : 'Save Plan'}
        </button>

      </div>

      {response && (
  <div className="mt-4 p-4 bg-white rounded shadow relative w-full">
    <div className="flex justify-between items-center">
      <h2 className="font-bold mb-2 text-lg">Training Plan:</h2>
      {goals.map((goal) => (
        goal.id === goalId && (
          <button 
            key={goal.id}
            disabled={isLoading}
            onClick={() => handleUpdatePreferences(goal.id)}
            className="flex items-center text-gray-600 hover:text-gray-800 ml-auto"
          >
            <FaUserPen className="ml-1 h-5 w-5" />
          </button>
        )
      ))}
    </div>
    <div className="overflow-x-auto">
    <div className="w-full"
  dangerouslySetInnerHTML={{ 
    __html: response // Ensures that bullet points and numbers are displayed on separate lines
    .replace(/(\n\s*\d+\.\s+)/g, (match) => `</li><li>${match}`)  
    .replace(/<\/li><li>/, '<ol><li>')      
    .replace(/(<\/li><li>)+$/, '</li></ol>') 
    .replace(/(\n\s*-\s+)/g, '</li><li>')
    .replace(/^/, '<ul><li>')
    .replace(/$/, '</li></ul>')
    .replace('<ul><li></li>', '<ul>')
  }} 
/></div>
  </div>
)}

    </div>
  );
};

export default TrainingPlanViewer;
