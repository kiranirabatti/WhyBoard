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
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Toggle + Actions row */}
      <div className="flex items-center justify-between">
        <ModeToggle mode={mode} onToggle={setMode} />
        <div className="flex items-center gap-2">
          <CopyButton text={activeNarrative} />
          <ExportButton analysis={analysis} />
        </div>
      </div>

      {/* Narrative — the hero output */}
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-8">
        <p
          key={mode}
          className="font-narrative text-lg text-gray-200 leading-relaxed animate-fade-in"
        >
          {activeNarrative}
        </p>
      </div>

      {/* Signal Cards */}
      <SignalCards signals={analysis.key_signals} />

      {/* Risk + Opportunity flags */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-red-900/10 border border-red-800/30 rounded-lg p-4">
          <p className="text-xs text-red-400 uppercase tracking-wider mb-2">Risk</p>
          <p className="text-sm text-gray-300">{analysis.risk_flag}</p>
        </div>
        <div className="bg-green-900/10 border border-green-800/30 rounded-lg p-4">
          <p className="text-xs text-green-400 uppercase tracking-wider mb-2">Opportunity</p>
          <p className="text-sm text-gray-300">{analysis.opportunity_flag}</p>
        </div>
      </div>

      {/* Metadata Bar — tokens, cost, timing, quality */}
      <MetadataBar metadata={analysis.metadata} />

      {/* Reset button */}
      <div className="text-center pt-2">
        <button
          onClick={onReset}
          className="text-sm text-gray-500 hover:text-gray-300 underline"
        >
          Analyze another dataset
        </button>
      </div>
    </div>
  );
}

export default NarrativeView;
