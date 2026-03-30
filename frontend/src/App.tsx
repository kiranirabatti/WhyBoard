import { useState, useCallback } from 'react';
import DataInput from './components/DataInput';
import NarrativeView from './components/NarrativeView';
import LoadingSkeleton from './components/LoadingSkeleton';
import type { WhyBoardAnalysis } from './types';
import { analyzeCsv, analyzePaste } from './api/whyboard';

type AppState = 'welcome' | 'input' | 'loading' | 'result' | 'error';

function App() {
  const [state, setState] = useState<AppState>('welcome');
  const [analysis, setAnalysis] = useState<WhyBoardAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleStartAnalysis = useCallback(() => {
    setState('input');
  }, []);

  const handleReset = useCallback(() => {
    setAnalysis(null);
    setError(null);
    setState('welcome');
  }, []);

  const handleBackToInput = useCallback(() => {
    setError(null);
    setState('input');
  }, []);

  const handleAnalyzeCsv = useCallback(async (file: File, context?: string) => {
    setState('loading');
    setError(null);
    setAnalysis(null);

    const result = await analyzeCsv(file, context);

    if (result.success && result.analysis) {
      setAnalysis(result.analysis);
      setState('result');
    } else {
      setError(result.error ?? 'Analysis failed. Please try again.');
      setState('error');
    }
  }, []);

  const handleAnalyzePaste = useCallback(async (data: string, context?: string) => {
    setState('loading');
    setError(null);
    setAnalysis(null);

    const result = await analyzePaste(data, context);

    if (result.success && result.analysis) {
      setAnalysis(result.analysis);
      setState('result');
    } else {
      setError(result.error ?? 'Analysis failed. Please try again.');
      setState('error');
    }
  }, []);

  const handleTryDemo = useCallback(async () => {
    setState('loading');
    setError(null);
    setAnalysis(null);

    const demoData = [
      'Quarter\tCategory\tBudget\tActual\tVariance\tVariance_Pct',
      'Q1\tRevenue\t4200000\t4385000\t185000\t4.4',
      'Q1\tCOGS\t1680000\t1710000\t-30000\t-1.8',
      'Q1\tR&D\t840000\t978000\t-138000\t-16.4',
      'Q1\tNet_Income\t525000\t567000\t42000\t8.0',
      'Q2\tRevenue\t4500000\t4692000\t192000\t4.3',
      'Q2\tCOGS\t1800000\t1845000\t-45000\t-2.5',
      'Q2\tR&D\t900000\t1117000\t-217000\t-24.1',
      'Q2\tNet_Income\t563000\t518000\t-45000\t-8.0',
      'Q3\tRevenue\t4800000\t5064000\t264000\t5.5',
      'Q3\tR&D\t960000\t1274000\t-314000\t-32.7',
      'Q3\tNet_Income\t600000\t518000\t-82000\t-13.7',
    ].join('\n');

    const result = await analyzePaste(demoData, 'Board meeting prep — identify the real story behind budget variance');

    if (result.success && result.analysis) {
      setAnalysis(result.analysis);
      setState('result');
    } else {
      setError(result.error ?? 'Demo failed. Please try again.');
      setState('error');
    }
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-surface-0/80 backdrop-blur-xl border-b border-surface-3/30">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <button onClick={handleReset} className="flex items-center gap-3 group">
            <div className="w-9 h-9 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center group-hover:bg-brand-500/20 transition-colors">
              <span className="font-narrative text-brand-400 text-lg font-semibold">W</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight leading-none">
                Why<span className="text-brand-400">Board</span>
              </h1>
            </div>
          </button>

          {state === 'result' && (
            <button onClick={handleBackToInput} className="btn-secondary text-sm py-2 px-4">
              New Analysis
            </button>
          )}
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1">
        {/* Welcome screen */}
        {state === 'welcome' && (
          <div className="max-w-3xl mx-auto px-6 pt-20 pb-16 animate-fade-up">
            <div className="text-center space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-brand-500/10 border border-brand-500/20 text-brand-300 text-xs font-medium">
                <span className="w-1.5 h-1.5 rounded-full bg-brand-400 animate-pulse" />
                Powered by Claude AI
              </div>

              <h2 className="text-4xl sm:text-5xl font-bold tracking-tight leading-[1.1]">
                What your data
                <br />
                <span className="text-gradient">actually means</span>
              </h2>

              <p className="text-lg text-gray-400 max-w-xl mx-auto leading-relaxed">
                Upload a spreadsheet. Get the narrative a CEO needs in 10 seconds
                and the detail an analyst needs in 10 minutes.
              </p>

              <div className="flex items-center justify-center gap-4 pt-4">
                <button onClick={handleStartAnalysis} className="btn-primary text-base py-3.5 px-8">
                  Analyze Your Data
                </button>
                <button onClick={handleTryDemo} className="btn-secondary text-base py-3.5 px-8">
                  Try a Demo
                </button>
              </div>
            </div>

            {/* Feature cards */}
            <div className="grid grid-cols-3 gap-4 mt-20">
              <div className="card p-5 space-y-3">
                <div className="w-10 h-10 rounded-xl bg-brand-500/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-brand-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-200">Drop a CSV</h3>
                <p className="text-sm text-gray-500 leading-relaxed">
                  Upload any spreadsheet or paste tabular data. No formatting required.
                </p>
              </div>

              <div className="card p-5 space-y-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-200">AI Interprets</h3>
                <p className="text-sm text-gray-500 leading-relaxed">
                  Not what the data shows. What it <em className="text-gray-400">means</em>. Risks, signals, opportunities.
                </p>
              </div>

              <div className="card p-5 space-y-3">
                <div className="w-10 h-10 rounded-xl bg-violet-500/10 flex items-center justify-center">
                  <svg className="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 21L3 16.5m0 0L7.5 12M3 16.5h13.5m0-13.5L21 7.5m0 0L16.5 12M21 7.5H7.5" />
                  </svg>
                </div>
                <h3 className="font-semibold text-gray-200">Two Audiences</h3>
                <p className="text-sm text-gray-500 leading-relaxed">
                  Toggle between executive summary and analyst deep-dive. Same insight, right depth.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Data input */}
        {state === 'input' && (
          <div className="max-w-5xl mx-auto px-6 py-12 animate-fade-up">
            <DataInput
              onAnalyzeCsv={handleAnalyzeCsv}
              onAnalyzePaste={handleAnalyzePaste}
              isLoading={false}
            />
          </div>
        )}

        {/* Loading */}
        {state === 'loading' && (
          <div className="max-w-3xl mx-auto px-6 py-16">
            <LoadingSkeleton />
          </div>
        )}

        {/* Error */}
        {state === 'error' && (
          <div className="max-w-2xl mx-auto px-6 py-20 animate-fade-up">
            <div className="card-elevated p-8 text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto">
                <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-200">Analysis Failed</h3>
              <p className="text-gray-400 max-w-md mx-auto">{error}</p>
              <div className="flex items-center justify-center gap-3 pt-2">
                <button onClick={handleBackToInput} className="btn-primary py-2.5 px-6 text-sm">
                  Try Again
                </button>
                <button onClick={handleReset} className="btn-secondary py-2.5 px-6 text-sm">
                  Back to Home
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Results */}
        {state === 'result' && analysis && (
          <div className="max-w-3xl mx-auto px-6 py-10 animate-fade-up">
            <NarrativeView analysis={analysis} onReset={handleReset} />
          </div>
        )}
      </main>

      {/* Footer — only on welcome */}
      {state === 'welcome' && (
        <footer className="border-t border-surface-3/30 px-6 py-5">
          <div className="max-w-5xl mx-auto flex items-center justify-between text-xs text-gray-600">
            <span>ScriptsHub Internal</span>
            <span>Data is processed in memory and never stored</span>
          </div>
        </footer>
      )}
    </div>
  );
}

export default App;
