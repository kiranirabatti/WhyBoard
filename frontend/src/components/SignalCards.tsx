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

function getDirectionStyles(direction: KeySignal['direction']): { text: string; bg: string; border: string } {
  switch (direction) {
    case 'up': return {
      text: 'text-signal-up',
      bg: 'bg-emerald-500/5',
      border: 'border-emerald-500/20',
    };
    case 'down': return {
      text: 'text-signal-down',
      bg: 'bg-red-500/5',
      border: 'border-red-500/20',
    };
    case 'flat': return {
      text: 'text-signal-flat',
      bg: 'bg-slate-500/5',
      border: 'border-slate-500/20',
    };
  }
}

function SignalCards({ signals }: SignalCardsProps) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {signals.map((signal, index) => {
        const styles = getDirectionStyles(signal.direction);
        return (
          <div
            key={`signal-${index}-${signal.label}`}
            className={`card p-5 ${styles.bg} animate-scale-in`}
            style={{ animationDelay: `${index * 80}ms`, animationFillMode: 'both' }}
          >
            <p className="text-xs text-gray-500 font-medium uppercase tracking-wider mb-3">
              {signal.label}
            </p>
            <div className="flex items-baseline gap-2">
              <span className={`text-xl font-bold ${styles.text}`}>
                {signal.value}
              </span>
              <span className={`text-base ${styles.text} opacity-60`}>
                {getDirectionIcon(signal.direction)}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default SignalCards;
