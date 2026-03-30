import type { AnalysisMetadata } from '../types';

interface MetadataBarProps {
  metadata: AnalysisMetadata;
}

function getQualityLabel(score: number): { label: string; color: string } {
  if (score >= 80) return { label: 'Excellent', color: 'text-green-400' };
  if (score >= 60) return { label: 'Good', color: 'text-blue-400' };
  if (score >= 40) return { label: 'Fair', color: 'text-yellow-400' };
  return { label: 'Limited', color: 'text-red-400' };
}

function getQualityBarColor(score: number): string {
  if (score >= 80) return 'bg-green-400';
  if (score >= 60) return 'bg-blue-400';
  if (score >= 40) return 'bg-yellow-400';
  return 'bg-red-400';
}

function formatINR(amount: number): string {
  if (amount < 0.01) return `₹${amount.toFixed(4)}`;
  return `₹${amount.toFixed(2)}`;
}

function MetadataBar({ metadata }: MetadataBarProps) {
  const quality = getQualityLabel(metadata.data_quality_score);
  const { token_usage } = metadata;

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-4 space-y-3">
      {/* Top row: key metrics */}
      <div className="grid grid-cols-4 gap-4 text-center">
        {/* Response Time */}
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider">Response</p>
          <p className="text-lg font-bold text-gray-200">
            {metadata.response_time_seconds.toFixed(1)}s
          </p>
        </div>

        {/* Token Usage */}
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider">Tokens</p>
          <p className="text-lg font-bold text-gray-200">
            {token_usage.total_tokens.toLocaleString()}
          </p>
        </div>

        {/* Cost in INR */}
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider">Cost</p>
          <p className="text-lg font-bold text-green-400">
            {formatINR(token_usage.cost_inr)}
          </p>
        </div>

        {/* Data Quality */}
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wider">Quality</p>
          <p className={`text-lg font-bold ${quality.color}`}>
            {metadata.data_quality_score}/100
          </p>
        </div>
      </div>

      {/* Quality bar */}
      <div className="w-full bg-gray-800 rounded-full h-1.5">
        <div
          className={`h-1.5 rounded-full transition-all duration-500 ${getQualityBarColor(metadata.data_quality_score)}`}
          style={{ width: `${metadata.data_quality_score}%` }}
        />
      </div>

      {/* Detail row */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-4">
          <span>{metadata.data_type}</span>
          <span>{metadata.row_count.toLocaleString()} rows &times; {metadata.column_count} cols</span>
          <span>In: {token_usage.input_tokens.toLocaleString()} &middot; Out: {token_usage.output_tokens.toLocaleString()}</span>
        </div>
        <span title={`$${token_usage.cost_usd.toFixed(4)} USD`}>
          ${token_usage.cost_usd.toFixed(4)}
        </span>
      </div>
    </div>
  );
}

export default MetadataBar;
