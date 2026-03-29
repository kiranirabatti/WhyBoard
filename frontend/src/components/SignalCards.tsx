import type { KeySignal } from '../types';

interface SignalCardsProps {
  signals: [KeySignal, KeySignal, KeySignal];
}

function getDirectionIcon(direction: KeySignal['direction']): string {
  switch (direction) {
    case 'up': return '\u2191';
    case 'down': return '\u2193';
    case 'flat': return '\u2192';
  }
}

function getDirectionColor(direction: KeySignal['direction']): string {
  switch (direction) {
    case 'up': return 'text-signal-up';
    case 'down': return 'text-signal-down';
    case 'flat': return 'text-signal-flat';
  }
}

function getBorderColor(direction: KeySignal['direction']): string {
  switch (direction) {
    case 'up': return 'border-green-500/30';
    case 'down': return 'border-red-500/30';
    case 'flat': return 'border-gray-600';
  }
}

function SignalCards({ signals }: SignalCardsProps) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {signals.map((signal, index) => (
        <div
          key={`signal-${index}-${signal.label}`}
          className={`bg-gray-900 border ${getBorderColor(signal.direction)} rounded-lg p-4`}
        >
          <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">
            {signal.label}
          </p>
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl font-bold ${getDirectionColor(signal.direction)}`}>
              {signal.value}
            </span>
            <span className={`text-lg ${getDirectionColor(signal.direction)}`}>
              {getDirectionIcon(signal.direction)}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}

export default SignalCards;
