import React, { useState, useEffect } from 'react';
import { TrainingPreferences } from '../types/preferences';
import { useLocation } from 'react-router-dom';

interface PreferencesProps {
  preferences: TrainingPreferences[];
  onSavePreferences: (preference: TrainingPreferences) => void;
}

const PreferencesForm: React.FC<PreferencesProps> = ({ preferences, onSavePreferences }) => {
  const location = useLocation(); 
  const params = new URLSearchParams(location.search); 
  const id = params.get('id') || ''; // Ensure id is always a string

  const existingPreference = preferences.find(p => p.id === id);

  const [availableDays, setAvailableDays] = useState<string[]>(existingPreference?.availableDays || ['Sun']);
  const [preferredLongRunDay, setPreferredLongRunDay] = useState<string>(existingPreference?.preferredLongRunDay || 'Sun');
  const [strengthTraining, setStrengthTraining] = useState<boolean>(existingPreference?.strengthTraining ?? false);
  const [validationError, setValidationError] = useState<string>('');
  const [formValid, setFormValid] = useState<boolean>(true);

  const daysOfWeek = ['Mon', 'Tues', 'Wed', 'Thurs', 'Fri', 'Sat', 'Sun'];

  // Update form fields if preferences or id changes
  useEffect(() => {
    if (existingPreference) {
      setAvailableDays(existingPreference.availableDays);
      setPreferredLongRunDay(existingPreference.preferredLongRunDay);
      setStrengthTraining(existingPreference.strengthTraining);
    }
  }, [existingPreference]);

  useEffect(() => {
    validateForm();
  }, [strengthTraining, availableDays]);

  const validateForm = () => {
    if (availableDays.length === 0) {
      setValidationError('Please select at least one available day.');
      setFormValid(false);
      return;
    }
    
    if (strengthTraining && availableDays.length < 2) {
      setValidationError('When strength training is selected, you must choose at least 2 available days.');
      setFormValid(false);
      return;
    }
    
    // If we get here, the form is valid
    setValidationError('');
    setFormValid(true);
  };

  // Handle available days change
  const handleAvailableDaysChange = (day: string, isChecked: boolean) => {
    let newAvailableDays: string[];
    
    if (isChecked) {
      newAvailableDays = [...availableDays, day];
    } else {
      newAvailableDays = availableDays.filter(d => d !== day);
      if (preferredLongRunDay === day && newAvailableDays.length > 0) {
        setPreferredLongRunDay(newAvailableDays[0]);
      } else if (newAvailableDays.length === 0) {
        setPreferredLongRunDay('');
      }
    }
    
    setAvailableDays(newAvailableDays);
  };


  const handleStrengthTrainingChange = (value: boolean) => {
    if (value && availableDays.length < 2) {
      setValidationError('Strength training requires at least 2 available days. Please select more days first.');
    }
    
    setStrengthTraining(value);
  };

  const handleSubmitPreferences = (e: React.FormEvent) => {
    e.preventDefault();

    if (!formValid) {
      return;
    }

    const trainingPreferences: TrainingPreferences = {
      id,
      preferredLongRunDay,
      strengthTraining,
      availableDays,
    };

    onSavePreferences(trainingPreferences);
  };

  const isButtonDisabled = !formValid || 
    availableDays.length === 0 || 
    (strengthTraining && availableDays.length < 2) ||
    preferredLongRunDay === '';

  return (
    <div className="flex flex-col space-y-4 w-full">
      <h2 className="text-xl font-semibold mb-4">
        {existingPreference ? 'Edit' : 'Create'} Training Preferences
      </h2>
      <form onSubmit={handleSubmitPreferences}>

        <div>
          <span className="text-sm font-medium mr-1">Available Training Days:</span>
          <div className="flex flex-wrap gap-4 mt-2">
            {daysOfWeek.map((day) => (
              <label key={day} className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  name="availableDays"
                  value={day}
                  checked={availableDays.includes(day)}
                  onChange={(e) => handleAvailableDaysChange(day, e.target.checked)}
                  className="form-checkbox text-blue-600"
                />
                <span className="text-sm">{day}</span>
              </label>
            ))}
          </div>
          <p className="text-sm text-gray-600 mt-1">
            {strengthTraining && availableDays.length < 2 && (
              <span className="text-red-500 ml-2">
                Need at least 2 days for strength training
              </span>
            )}
          </p>
        </div>

        <div>
          <span className="text-sm font-medium mr-1">Include Strength Training:</span>
          <div className="flex flex-wrap gap-4 mt-2">
            {[
              { label: 'Yes', value: true },
              { label: 'No', value: false },
            ].map((option) => (
              <label key={option.label} className="flex items-center space-x-2">
                <input
                  type="radio"
                  name="strengthTraining"
                  value={String(option.value)}
                  checked={strengthTraining === option.value}
                  onChange={() => handleStrengthTrainingChange(option.value)}
                  className="form-radio text-blue-600"
                />
                <span className="text-sm">{option.label}</span>
              </label>
            ))}
          </div>
          {strengthTraining && (
            <p className="text-sm text-blue-600 mt-1">

            </p>
          )}
        </div>

        <div>
          <span className="text-sm font-medium mr-1">Preferred Long Run Training Day:</span>
          <div className="flex flex-wrap gap-4 mt-2">
            {daysOfWeek.map((day) => {
              const isAvailable = availableDays.includes(day);
              return (
                <label key={day} className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="preferredLongRunDay"
                    value={day}
                    checked={preferredLongRunDay === day}
                    onChange={(e) => setPreferredLongRunDay(e.target.value)}
                    className="form-radio text-blue-600"
                    disabled={!isAvailable}
                  />
                  <span className={`text-sm ${!isAvailable ? 'text-gray-400' : ''}`}>
                    {day}
                  </span>
                </label>
              );
            })}
          </div>
          {availableDays.length === 0 && (
            <p className="text-red-500 text-sm mt-1">
              Select at least one available day first
            </p>
          )}
        </div>

        {validationError && (
          <p className="text-red-500 text-sm mt-2 font-medium">
            {validationError}
          </p>
        )}

        <button 
          type="submit" 
          className={`w-full py-2 rounded-lg transition mt-4 ${
            isButtonDisabled 
              ? 'bg-gray-400 text-gray-200 cursor-not-allowed' 
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
          disabled={isButtonDisabled}
        >
          Save Preferences
        </button>
      </form>
    </div>
  );
};

export default PreferencesForm;