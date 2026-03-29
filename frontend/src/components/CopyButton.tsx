import { useState, useCallback } from 'react';

interface CopyButtonProps {
  text: string;
}

function CopyButton({ text }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }, [text]);

  return (
    <button
      onClick={handleCopy}
      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
        copied
          ? 'bg-green-500/20 text-green-400 border border-green-500/30'
          : 'bg-gray-800 text-gray-400 hover:text-gray-200 border border-gray-700 hover:border-gray-500'
      }`}
    >
      {copied ? 'Copied!' : 'Copy'}
    </button>
  );
}

export default CopyButton;
