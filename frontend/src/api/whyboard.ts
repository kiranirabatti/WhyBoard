import type { AnalyzeResponse } from '../types';

const API_BASE = '/api';

export async function analyzeCsv(file: File, context?: string): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (context) {
    formData.append('context', context);
  }

  const response = await fetch(`${API_BASE}/analyze/csv`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Analysis failed' }));
    return { success: false, analysis: null, error: error.detail ?? 'Analysis failed' };
  }

  return response.json() as Promise<AnalyzeResponse>;
}

export async function analyzePaste(data: string, context?: string): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE}/analyze/paste`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data, context }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Analysis failed' }));
    return { success: false, analysis: null, error: error.detail ?? 'Analysis failed' };
  }

  return response.json() as Promise<AnalyzeResponse>;
}

export async function healthCheck(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE}/health`);
  return response.json() as Promise<{ status: string }>;
}
