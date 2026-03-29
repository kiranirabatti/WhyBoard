import { useState, useRef, useCallback, type DragEvent, type ChangeEvent } from 'react';

interface DataInputProps {
  onAnalyzeCsv: (file: File, context?: string) => void;
  onAnalyzePaste: (data: string, context?: string) => void;
  isLoading: boolean;
}

type Tab = 'upload' | 'paste';

const PASTE_PLACEHOLDER = `Paste your data here (tab or comma separated):

Region\tRevenue\tUnits Sold
North\t240000\t120
South\t187000\t95
East\t156000\t78
West\t134000\t67`;

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
    <div className="w-full max-w-2xl mx-auto">
      {/* Tabs */}
      <div className="flex border-b border-gray-700 mb-6">
        <button
          onClick={() => setActiveTab('upload')}
          className={`px-6 py-3 text-sm font-medium transition-colors ${
            activeTab === 'upload'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Upload CSV
        </button>
        <button
          onClick={() => setActiveTab('paste')}
          className={`px-6 py-3 text-sm font-medium transition-colors ${
            activeTab === 'paste'
              ? 'text-blue-400 border-b-2 border-blue-400'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          Paste Data
        </button>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
            isDragOver
              ? 'border-blue-400 bg-blue-400/10'
              : selectedFile
                ? 'border-green-500 bg-green-500/5'
                : 'border-gray-600 hover:border-gray-400'
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
            <div>
              <p className="text-green-400 font-medium">{selectedFile.name}</p>
              <p className="text-gray-500 text-sm mt-1">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
          ) : (
            <div>
              <p className="text-gray-300">
                Drag & drop a CSV file here, or click to browse
              </p>
              <p className="text-gray-500 text-sm mt-2">Maximum 5 MB</p>
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
          className="w-full h-56 bg-gray-900 border border-gray-700 rounded-lg p-4 font-mono text-sm text-gray-200 placeholder-gray-600 resize-none focus:outline-none focus:border-blue-400 transition-colors"
        />
      )}

      {/* Context input */}
      <input
        type="text"
        value={context}
        onChange={(e) => setContext(e.target.value)}
        placeholder="Optional: Add context (e.g., 'Focus on regional trends')"
        className="w-full mt-4 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-sm text-gray-200 placeholder-gray-600 focus:outline-none focus:border-blue-400 transition-colors"
      />

      {/* Action buttons */}
      <div className="flex gap-3 mt-6">
        <button
          onClick={handleAnalyze}
          disabled={!hasData || isLoading}
          className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-700 disabled:text-gray-500 text-white font-medium py-3 px-6 rounded-lg transition-colors"
        >
          {isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
        {hasData && (
          <button
            onClick={handleClear}
            className="px-6 py-3 text-gray-400 hover:text-gray-200 border border-gray-700 rounded-lg transition-colors"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
}

export default DataInput;
