import React, { useState, useEffect } from 'react';

interface GoalTimePickerProps {
  onChange: (time: string) => void;
}

const GoalTimePicker: React.FC<GoalTimePickerProps> = ({ onChange }) => {
  const [hours, setHours] = useState(0);
  const [minutes, setMinutes] = useState(0);
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const formatted = [
      hours.toString().padStart(2, '0'),
      minutes.toString().padStart(2, '0'),
      seconds.toString().padStart(2, '0'),
    ].join(':');

    onChange(formatted);
  }, [hours, minutes, seconds, onChange]);

  const renderOptions = (limit: number) => (
    Array.from({ length: limit + 1 }, (_, i) => (
      <option key={i} value={i}>
        {i.toString().padStart(2, '0')}
      </option>
    ))
  );

  return (
    <div className="flex space-x-2">
      <select
        className="w-full p-2 border rounded"
        value={hours}
        onChange={(e) => setHours(Number(e.target.value))}
      >
        {renderOptions(23)}
      </select>

      <select
        className="w-full p-2 border rounded"
        value={minutes}
        onChange={(e) => setMinutes(Number(e.target.value))}
      >
        {renderOptions(59)}
      </select>

      <select
        className="w-full p-2 border rounded"
        value={seconds}
        onChange={(e) => setSeconds(Number(e.target.value))}
      >
        {renderOptions(59)}
      </select>
    </div>
  );
};

export default GoalTimePicker;
