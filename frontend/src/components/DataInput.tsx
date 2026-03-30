import { useState, useRef, useCallback, type DragEvent, type ChangeEvent } from 'react';

interface DataInputProps {
  onAnalyzeCsv: (file: File, context?: string) => void;
  onAnalyzePaste: (data: string, context?: string) => void;
  isLoading: boolean;
}

type Tab = 'upload' | 'paste';

const PASTE_PLACEHOLDER = `Paste your data here — tab or comma separated:

Region\tRevenue\tUnits Sold\tGrowth %
North\t240000\t120\t18.5
South\t187000\t95\t-12.3
East\t156000\t78\t5.1
West\t134000\t67\t8.7`;

function DataInput({ onAnalyzeCsv, onAnalyzePaste, isLoading }: DataInputProps) {
  const [activeTab, setActiveTab] = useState<Tab>('upload');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [pasteData, setPasteData] = useState('');
  const [context, setContext] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const hasData = activeTab === 'upload' ? selectedFile !== null : pasteData.trim().length > 0;

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.name.endsWith('.csv')) {
      setSelectedFile(file);
    }
  }, []);

  const handleFileSelect = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  }, []);

  const handleAnalyze = useCallback(() => {
    const ctx = context.trim() || undefined;
    if (activeTab === 'upload' && selectedFile) {
      onAnalyzeCsv(selectedFile, ctx);
    } else if (activeTab === 'paste' && pasteData.trim()) {
      onAnalyzePaste(pasteData, ctx);
    }
  }, [activeTab, selectedFile, pasteData, context, onAnalyzeCsv, onAnalyzePaste]);

  const handleClear = useCallback(() => {
    setSelectedFile(null);
    setPasteData('');
    setContext('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">Add your data</h2>
        <p className="text-gray-500">Upload a CSV file or paste tabular data directly</p>
      </div>

      {/* Tabs */}
      <div className="card-elevated overflow-hidden">
        <div className="flex border-b border-surface-3/50">
          <button
            onClick={() => setActiveTab('upload')}
            className={`flex-1 px-6 py-3.5 text-sm font-medium transition-all relative ${
              activeTab === 'upload'
                ? 'text-brand-400'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            Upload CSV
            {activeTab === 'upload' && (
              <span className="absolute bottom-0 left-4 right-4 h-0.5 bg-brand-400 rounded-full" />
            )}
          </button>
          <button
            onClick={() => setActiveTab('paste')}
            className={`flex-1 px-6 py-3.5 text-sm font-medium transition-all relative ${
              activeTab === 'paste'
                ? 'text-brand-400'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            Paste Data
            {activeTab === 'paste' && (
              <span className="absolute bottom-0 left-4 right-4 h-0.5 bg-brand-400 rounded-full" />
            )}
          </button>
        </div>

        <div className="p-6">
          {/* Upload Tab */}
          {activeTab === 'upload' && (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-200 ${
                isDragOver
                  ? 'border-brand-400 bg-brand-400/5 scale-[1.01]'
                  : selectedFile
                    ? 'border-emerald-500/50 bg-emerald-500/5'
                    : 'border-surface-3 hover:border-gray-500 hover:bg-surface-2/50'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFileSelect}
                className="hidden"
              />
              {selectedFile ? (
                <div className="space-y-2">
                  <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto">
                    <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                  </div>
                  <p className="text-emerald-400 font-medium">{selectedFile.name}</p>
                  <p className="text-gray-600 text-sm">
                    {(selectedFile.size / 1024).toFixed(1)} KB
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="w-12 h-12 rounded-xl bg-surface-2 border border-surface-3 flex items-center justify-center mx-auto">
                    <svg className="w-6 h-6 text-gray-500" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                    </svg>
                  </div>
                  <p className="text-gray-300 font-medium">
                    Drop a CSV file here, or click to browse
                  </p>
                  <p className="text-gray-600 text-sm">Up to 5 MB</p>
                </div>
              )}
            </div>
          )}

          {/* Paste Tab */}
          {activeTab === 'paste' && (
            <textarea
              value={pasteData}
              onChange={(e) => setPasteData(e.target.value)}
              placeholder={PASTE_PLACEHOLDER}
              className="w-full h-52 bg-surface-0 border border-surface-3 rounded-xl p-4 font-mono text-sm text-gray-200 placeholder-gray-700 resize-none focus:outline-none focus:border-brand-500/50 focus:ring-1 focus:ring-brand-500/20 transition-all"
            />
          )}

          {/* Context input */}
          <div className="mt-4 relative">
            <input
              type="text"
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Add context: 'Board meeting prep', 'Focus on margins'..."
              className="w-full bg-surface-0 border border-surface-3 rounded-xl px-4 py-3 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-brand-500/50 focus:ring-1 focus:ring-brand-500/20 transition-all"
            />
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-700">Optional</span>
          </div>
        </div>

        {/* Action bar */}
        <div className="px-6 pb-6 flex items-center gap-3">
          <button
            onClick={handleAnalyze}
            disabled={!hasData || isLoading}
            className="btn-primary flex-1"
          >
            {isLoading ? 'Analyzing...' : 'Analyze'}
          </button>
          {hasData && (
            <button onClick={handleClear} className="btn-secondary">
              Clear
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default DataInput;
