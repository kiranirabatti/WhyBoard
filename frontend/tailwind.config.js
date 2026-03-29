/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        narrative: ['Georgia', 'Times New Roman', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        signal: {
          up: '#22c55e',
          down: '#ef4444',
          flat: '#6b7280',
        },
      },
    },
  },
  plugins: [],
};
