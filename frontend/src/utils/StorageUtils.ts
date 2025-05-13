import { RunningGoal } from '@types';

// Retrieve the list of goals from localStorage
export const getStoredGoals = (): RunningGoal[] => {
  const storedGoals = localStorage.getItem('goals');
  return storedGoals ? JSON.parse(storedGoals) : [];
};

// Save the updated list of goals to localStorage
export const saveGoalsToLocalStorage = (goals: RunningGoal[]): void => {
  localStorage.setItem('goals', JSON.stringify(goals));
};
