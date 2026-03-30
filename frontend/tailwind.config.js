/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        narrative: ['Newsreader', 'Georgia', 'Times New Roman', 'serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        brand: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        surface: {
          0: '#030712',    // deepest bg
          1: '#0f172a',    // card bg
          2: '#1e293b',    // elevated
          3: '#334155',    // borders
        },
        signal: {
          up: '#34d399',
          down: '#f87171',
          flat: '#94a3b8',
        },
      },
      fontSize: {
        'narrative': ['1.25rem', { lineHeight: '1.9', letterSpacing: '-0.01em' }],
        'narrative-lg': ['1.375rem', { lineHeight: '1.85', letterSpacing: '-0.01em' }],
      },
      animation: {
        'fade-in': 'fade-in 400ms cubic-bezier(0.16, 1, 0.3, 1)',
        'fade-up': 'fade-up 500ms cubic-bezier(0.16, 1, 0.3, 1)',
        'scale-in': 'scale-in 300ms cubic-bezier(0.16, 1, 0.3, 1)',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(12px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        'scale-in': {
          from: { opacity: '0', transform: 'scale(0.95)' },
          to: { opacity: '1', transform: 'scale(1)' },
        },
        'shimmer': {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
};
