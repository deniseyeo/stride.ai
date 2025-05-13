import React from 'react';
import { RunningGoal } from '../types/index';
import { useNavigate } from 'react-router-dom';
import { TrainingPlans } from '../types/trainingplans';


interface GoalListProps {
  goals: RunningGoal[];
  onDeleteGoal: (id: string) => void;
  onCreateGoal: () => void;
  trainingPlans: TrainingPlans[];
}


const GoalList: React.FC<GoalListProps> = ({ 
  goals, 
  onDeleteGoal,
  onCreateGoal,
  trainingPlans
}) => {
  const navigate = useNavigate()
  const handleUpdateTrainingPlan = (id: string, hasTrainingPlan: boolean) => {
    const generateParam = hasTrainingPlan ? 'false' : 'true';
    navigate(`/plan?id=${id}&generate=${generateParam}`);
  };
  
  

  

  if (goals.length === 0) {
    return ( 
      <div className="text-center p-8 bg-white rounded-lg">
        <p className="text-gray-500 mb-4">You haven't set any running goals yet.</p>
        <button 
          className="px-4 py-2 bg-blue-600 text-white rounded-lg"
          onClick={onCreateGoal}
        >
          Create Your First Goal
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {goals.map(goal => {
        const today: string = new Date().toISOString().split('T')[0];
        const hasTrainingPlan = trainingPlans.some(plan => plan.id === goal.id);
        
        return ( 
          <div key={goal.id} className="bg-white p-4 rounded-lg shadow relative">
            <div className="flex justify-between items-start mb-2">
            <div className="flex-1">
                <h3 className="text-lg font-semibold text-center">
                  {goal.target}km 🏁 - {goal.notes}
                </h3>
                <div className="text-sm text-gray-600 text-center">
                <p><b>Goal Time:</b>{goal.goalTime}</p>
                  <b>Goal Creation Date:</b> {today}
                  <p><b>Goal/Race Date:</b> {goal.endDate}</p>
                </div>
              </div>
              <button 
                onClick={() => onDeleteGoal(goal.id)}
                className="text-red-500 hover:text-red-700 text-center"
              >
                ✕
              </button>
              <div>

            </div>
          
          </div>

        <button 
  onClick={() => handleUpdateTrainingPlan(goal.id, hasTrainingPlan)}
  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
>
  {hasTrainingPlan ? 'View Training Plan' : 'Create Training Plan'}
</button>

              </div>
          
        );
      })}
    </div>
  );
};

export default GoalList;
