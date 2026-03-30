import { useState } from 'react';
import type { WhyBoardAnalysis, NarrativeMode } from '../types';
import ModeToggle from './ModeToggle';
import CopyButton from './CopyButton';
import SignalCards from './SignalCards';
import MetadataBar from './MetadataBar';
import ExportButton from './ExportButton';

interface NarrativeViewProps {
  analysis: WhyBoardAnalysis;
  onReset: () => void;
}

function NarrativeView({ analysis, onReset }: NarrativeViewProps) {
  const [mode, setMode] = useState<NarrativeMode>('executive');

  const activeNarrative = mode === 'executive'
    ? analysis.executive_narrative
    : analysis.analyst_narrative;

  return (
    <div className="space-y-6">
      {/* Toggle + Actions */}
      <div className="flex items-center justify-between">
        <ModeToggle mode={mode} onToggle={setMode} />
        <div className="flex items-center gap-2">
          <CopyButton text={activeNarrative} />
          <ExportButton analysis={analysis} />
        </div>
      </div>

      {/* Narrative — the hero */}
      <div className="card-elevated p-8 sm:p-10">
        <p
          key={mode}
          className="font-narrative text-narrative-lg text-gray-200 animate-fade-in"
        >
          {activeNarrative}
        </p>
      </div>

      {/* Signal Cards */}
      <SignalCards signals={analysis.key_signals} />

      {/* Risk + Opportunity */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card p-5 border-l-2 border-l-red-500/40">
          <div className="flex items-center gap-2 mb-2.5">
            <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126z" />
            </svg>
            <span className="text-xs font-semibold text-red-400 uppercase tracking-wider">Risk</span>
          </div>
          <p className="text-sm text-gray-300 leading-relaxed">{analysis.risk_flag}</p>
        </div>
        <div className="card p-5 border-l-2 border-l-emerald-500/40">
          <div className="flex items-center gap-2 mb-2.5">
            <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
            </svg>
            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Opportunity</span>
          </div>
          <p className="text-sm text-gray-300 leading-relaxed">{analysis.opportunity_flag}</p>
        </div>
      </div>

      {/* Metadata */}
      <MetadataBar metadata={analysis.metadata} />

      {/* Reset */}
      <div className="text-center pt-2 pb-8">
        <button
          onClick={onReset}
          className="text-sm text-gray-600 hover:text-gray-400 transition-colors"
        >
          Analyze another dataset
        </button>
      </div>
    </div>
  );
}

export default NarrativeView;
