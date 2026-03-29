export interface KeySignal {
  label: string;
  value: string;
  direction: 'up' | 'down' | 'flat';
}

export interface WhyBoardAnalysis {
  executive_narrative: string;
  analyst_narrative: string;
  key_signals: [KeySignal, KeySignal, KeySignal];
  risk_flag: string;
  opportunity_flag: string;
  data_type: string;
  row_count: number;
  column_count: number;
  analyzed_at: string;
}

export type NarrativeMode = 'executive' | 'analyst';

export interface AnalyzeResponse {
  success: boolean;
  analysis: WhyBoardAnalysis | null;
  error?: string;
}
