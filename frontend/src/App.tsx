import { useState, useCallback } from 'react';
import DataInput from './components/DataInput';
import type { WhyBoardAnalysis } from './types';
import { analyzeCsv, analyzePaste } from './api/whyboard';

function App() {
  const [analysis, setAnalysis] = useState<WhyBoardAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyzeCsv = useCallback(async (file: File, context?: string) => {
    setIsLoading(true);
    setError(null);
    setAnalysis(null);

    const result = await analyzeCsv(file, context);
    setIsLoading(false);

    if (result.success && result.analysis) {
      setAnalysis(result.analysis);
    } else {
      setError(result.error ?? 'Analysis failed. Please try again.');
    }
  }, []);

  const handleAnalyzePaste = useCallback(async (data: string, context?: string) => {
    setIsLoading(true);
    setError(null);
    setAnalysis(null);

    const result = await analyzePaste(data, context);
    setIsLoading(false);

    if (result.success && result.analysis) {
      setAnalysis(result.analysis);
    } else {
      setError(result.error ?? 'Analysis failed. Please try again.');
    }
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-gray-800 px-6 py-4">
        <h1 className="text-2xl font-bold tracking-tight">
          Why<span className="text-blue-400">Board</span>
        </h1>
        <p className="text-sm text-gray-400 mt-1">
          Narrative intelligence from your data
        </p>
      </header>

      <main className="flex-1 px-6 py-12">
        {!analysis && !isLoading && (
          <DataInput
            onAnalyzeCsv={handleAnalyzeCsv}
            onAnalyzePaste={handleAnalyzePaste}
            isLoading={isLoading}
          />
        )}

        {/* Loading skeleton */}
        {isLoading && (
          <div className="max-w-2xl mx-auto space-y-4 animate-pulse">
            <div className="h-6 bg-gray-800 rounded w-3/4" />
            <div className="h-6 bg-gray-800 rounded w-full" />
            <div className="h-6 bg-gray-800 rounded w-5/6" />
            <div className="h-4 bg-gray-800 rounded w-1/2 mt-8" />
            <div className="grid grid-cols-3 gap-4 mt-6">
              <div className="h-24 bg-gray-800 rounded" />
              <div className="h-24 bg-gray-800 rounded" />
              <div className="h-24 bg-gray-800 rounded" />
            </div>
          </div>
        )}

        {/* Error state */}
        {error && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-red-900/20 border border-red-800 rounded-lg p-6 text-center">
              <p className="text-red-400">{error}</p>
              <button
                onClick={() => { setError(null); setAnalysis(null); }}
                className="mt-4 text-sm text-gray-400 hover:text-gray-200 underline"
              >
                Try again
              </button>
            </div>
          </div>
        )}

        {/* Analysis result placeholder — Sprint 4 will add NarrativeView */}
        {analysis && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
              <p className="font-narrative text-lg text-gray-200 leading-relaxed">
                {analysis.executive_narrative}
              </p>
              <p className="text-sm text-gray-500 mt-4">
                Full narrative UI coming in Sprint 4. Toggle, signals, and copy.
              </p>
            </div>
            <button
              onClick={() => { setAnalysis(null); setError(null); }}
              className="mt-6 text-sm text-gray-400 hover:text-gray-200 underline"
            >
              Analyze another dataset
            </button>
          </div>
        )}
      </main>

      <footer className="border-t border-gray-800 px-6 py-3 text-center text-xs text-gray-600">
        WhyBoard v0.1.0 — ScriptsHub Internal
      </footer>
    </div>
  );
}

export default App;
