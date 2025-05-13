// Utility function to convert seconds to hours, minutes, and seconds
export const convertSecondsToTimeString = (totalSeconds: number): string => {
    // Handle negative or zero input
    if (totalSeconds <= 0) return '0h 0m 0s';
  
    // Calculate hours, minutes, and remaining seconds
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
  
    // Build the time string
    const parts: string[] = [];
    
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    if (seconds > 0 || parts.length === 0) parts.push(`${seconds}s`);
  
    return parts.join(' ');
  };
