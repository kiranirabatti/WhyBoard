import type { AnalysisMetadata } from '../types';

interface MetadataBarProps {
  metadata: AnalysisMetadata;
}

function getQualityLabel(score: number): { label: string; color: string } {
  if (score >= 80) return { label: 'Excellent', color: 'text-emerald-400' };
  if (score >= 60) return { label: 'Good', color: 'text-brand-400' };
  if (score >= 40) return { label: 'Fair', color: 'text-amber-400' };
  return { label: 'Limited', color: 'text-red-400' };
}

function getQualityBarColor(score: number): string {
  if (score >= 80) return 'bg-emerald-400';
  if (score >= 60) return 'bg-brand-400';
  if (score >= 40) return 'bg-amber-400';
  return 'bg-red-400';
}

function formatINR(amount: number): string {
  if (amount < 0.01) return `\u20B9${amount.toFixed(4)}`;
  return `\u20B9${amount.toFixed(2)}`;
}

function MetadataBar({ metadata }: MetadataBarProps) {
  const quality = getQualityLabel(metadata.data_quality_score);
  const { token_usage } = metadata;

  return (
    <div className="card p-5 space-y-4">
      {/* Metrics row */}
      <div className="grid grid-cols-4 gap-6">
        <div className="space-y-1">
          <p className="text-[10px] text-gray-600 uppercase tracking-widest font-medium">Response</p>
          <p className="text-sm font-semibold text-gray-300 tabular-nums">
            {metadata.response_time_seconds.toFixed(1)}s
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-[10px] text-gray-600 uppercase tracking-widest font-medium">Tokens</p>
          <p className="text-sm font-semibold text-gray-300 tabular-nums">
            {token_usage.total_tokens.toLocaleString()}
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-[10px] text-gray-600 uppercase tracking-widest font-medium">Cost</p>
          <p className="text-sm font-semibold text-emerald-400 tabular-nums">
            {formatINR(token_usage.cost_inr)}
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-[10px] text-gray-600 uppercase tracking-widest font-medium">Data Quality</p>
          <p className={`text-sm font-semibold tabular-nums ${quality.color}`}>
            {metadata.data_quality_score}
            <span className="text-gray-600 font-normal">/100</span>
          </p>
        </div>
      </div>

      {/* Quality progress bar */}
      <div className="w-full bg-surface-raised rounded-full h-1">
        <div
          className={`h-1 rounded-full transition-all duration-700 ease-out ${getQualityBarColor(metadata.data_quality_score)}`}
          style={{ width: `${metadata.data_quality_score}%` }}
        />
      </div>

      {/* Fine print */}
      <div className="flex items-center justify-between text-[11px] text-gray-600">
        <div className="flex items-center gap-3">
          <span className="capitalize">{metadata.data_type}</span>
          <span className="text-gray-700">&middot;</span>
          <span>{metadata.row_count.toLocaleString()} rows &times; {metadata.column_count} cols</span>
          <span className="text-gray-700">&middot;</span>
          <span>In: {token_usage.input_tokens.toLocaleString()} / Out: {token_usage.output_tokens.toLocaleString()}</span>
        </div>
        <span title={`$${token_usage.cost_usd.toFixed(4)} USD`}>
          ${token_usage.cost_usd.toFixed(4)}
        </span>
      </div>
    </div>
  );
}

export default MetadataBar;
