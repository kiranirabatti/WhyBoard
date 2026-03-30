export interface KeySignal {
  label: string;
  value: string;
  direction: 'up' | 'down' | 'flat';
}

export interface TokenUsage {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  cost_usd: number;
  cost_inr: number;
}

export interface AnalysisMetadata {
  data_type: string;
  row_count: number;
  column_count: number;
  analyzed_at: string;
  response_time_seconds: number;
  token_usage: TokenUsage;
  data_quality_score: number;
}

export interface WhyBoardAnalysis {
  executive_narrative: string;
  analyst_narrative: string;
  key_signals: [KeySignal, KeySignal, KeySignal];
  risk_flag: string;
  opportunity_flag: string;
  metadata: AnalysisMetadata;
}

export type NarrativeMode = 'executive' | 'analyst';

export interface AnalyzeResponse {
  success: boolean;
  analysis: WhyBoardAnalysis | null;
  error?: string;
}
