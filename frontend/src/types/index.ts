export type GoalDistance = 'Marathon' | 'Half Marathon' | '10K' | '5K' | 'Custom';

export interface RunningGoal {
  id: string;
  type: GoalDistance;
  target: number;
  goalTime: string;
  notes?: string;
  endDate: string;
}
