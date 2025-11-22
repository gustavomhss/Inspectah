/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        risk: {
          low: '#0f766e',
          medium: '#ca8a04',
          high: '#b91c1c',
          unknown: '#4b5563',
        },
        slate: {
          950: '#0b1224',
        },
      },
      fontFamily: {
        display: ['"Manrope"', 'Inter', 'system-ui', 'sans-serif'],
        body: ['"Manrope"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 10px 40px -20px rgba(0, 0, 0, 0.35)',
      },
    },
  },
  plugins: [],
};
