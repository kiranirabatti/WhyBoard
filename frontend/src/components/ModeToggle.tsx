import type { NarrativeMode } from '../types';

interface ModeToggleProps {
  mode: NarrativeMode;
  onToggle: (mode: NarrativeMode) => void;
}

function ModeToggle({ mode, onToggle }: ModeToggleProps) {
  return (
    <div className="inline-flex items-center bg-surface-1 border border-surface-3/50 rounded-xl p-1">
      <button
        onClick={() => onToggle('executive')}
        className={`px-5 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
          mode === 'executive'
            ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/25'
            : 'text-gray-500 hover:text-gray-300'
        }`}
      >
        Executive
      </button>
      <button
        onClick={() => onToggle('analyst')}
        className={`px-5 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
          mode === 'analyst'
            ? 'bg-brand-500 text-white shadow-lg shadow-brand-500/25'
            : 'text-gray-500 hover:text-gray-300'
        }`}
      >
        Analyst
      </button>
    </div>
  );
}

export default ModeToggle;
