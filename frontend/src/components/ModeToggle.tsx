import type { NarrativeMode } from '../types';

interface ModeToggleProps {
  mode: NarrativeMode;
  onToggle: (mode: NarrativeMode) => void;
}

function ModeToggle({ mode, onToggle }: ModeToggleProps) {
  return (
    <div className="inline-flex items-center bg-gray-800 rounded-full p-1">
      <button
        onClick={() => onToggle('executive')}
        className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
          mode === 'executive'
            ? 'bg-blue-500 text-white shadow-lg'
            : 'text-gray-400 hover:text-gray-200'
        }`}
      >
        Executive
      </button>
      <button
        onClick={() => onToggle('analyst')}
        className={`px-5 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
          mode === 'analyst'
            ? 'bg-blue-500 text-white shadow-lg'
            : 'text-gray-400 hover:text-gray-200'
        }`}
      >
        Analyst
      </button>
    </div>
  );
}

export default ModeToggle;
