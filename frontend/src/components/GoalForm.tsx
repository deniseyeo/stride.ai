import React, { useState, useEffect } from 'react';
import { GoalDistance, RunningGoal } from '../types/index';
import GoalTimePicker from '@components/GoalTimePicker';

interface GoalFormProps {
  onAddGoal: (goal: RunningGoal) => void;
}

const GoalForm: React.FC<GoalFormProps> = ({ onAddGoal }) => {
  const [goalDistance, setGoalDistance] = useState<GoalDistance>('marathon');
  const [target, setTarget] = useState<string>('42.2');
  const [notes, setNotes] = useState<string>('');
  const [goalTime, setGoalTime] = useState<string>('00:00:00');
  const [endDate, setEndDate] = useState<string>('');

  
  // Set default dates when component mounts
  useEffect(() => {
    const today = new Date();
    const nextMonth = new Date();
    nextMonth.setMonth(today.getMonth() + 1);
    setEndDate(formatDate(nextMonth));
  }, []);
  
  const formatDate = (date: Date): string => {
    return date.toISOString().split('T')[0];
  };

  useEffect(() => {
    switch (goalDistance) {
      case 'marathon':
        setTarget('42.2');
        break;
      case 'halfmarathon':
        setTarget('21.1');
        break;
      case '10k':
        setTarget('10.0');
        break;
      case '5k':
        setTarget('5.0');
        break;
      case 'custom':
        setTarget('');
        break;
      default:
        break;
    }
  }, [goalDistance]);
  
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const newGoal: RunningGoal = {
      id: Date.now().toString(),
      type: goalDistance,
      target: parseFloat(target),
      notes,
      goalTime,
      endDate
    };


    onAddGoal(newGoal);
    
    // Reset form
    setTarget('');
  };
  
  return (
    <div className="bg-white p-6 rounded-lg shadow mb-6">
      <h2 className="text-xl font-semibold mb-4">Create New Running Goal</h2>
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium mb-1">Goal Type</label>
            <select 
              className="w-full p-2 border rounded"
              value={goalDistance}
              onChange={(e) => setGoalDistance(e.target.value as GoalDistance)}
            >
              <option value="marathon">Marathon</option>
              <option value="halfmarathon">Half Marathon</option>
              <option value="10k">10K</option>
              <option value="5k">5K</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">
              Goal Distance (km)
            </label>
            <input 
            type="number"
            className="w-full p-2 border rounded"
            value={target}
            onChange={(e) => {
                const val = e.target.value;
                if (val === '') {
                setTarget('');
                return;
                }

                const parsed = parseFloat(val);
                if (!isNaN(parsed)) {
                setTarget(parsed.toFixed(2));
                }
            }}
            min="0"
            step="0.1"
            required
            disabled={goalDistance !== 'custom'}
/>
          </div>
          

          
          { <div>
            <label className="block text-sm font-medium mb-1">
              Goal Time (hh:mm:ss)
              </label>
              <GoalTimePicker onChange={setGoalTime} />
          </div> }

          { <div>
            <label className="block text-sm font-medium mb-1">
            Goal Name
            </label>
            <input 
              type="text" 
              className="w-full p-2 border rounded"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="E.g. Hackney Half 2026"
            />
          </div> }
        </div>

        
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
          <label className="block text-sm font-medium mb-1">Goal or Race Date</label>
            <input 
              type="date" 
              className="w-full p-2 border rounded"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              required
            />
          </div>
          
          <div>

          </div>
        </div>
        
        <button 
          type="submit" 
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Add Goal
        </button>
      </form>
    </div>
  );
};

export default GoalForm;