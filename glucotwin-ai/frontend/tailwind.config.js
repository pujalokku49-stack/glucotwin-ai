/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#ecfdf5',
          100: '#d1fae5',
          500: '#10b981',
          600: '#059669',
          700: '#047857',
          900: '#064e3b',
        },
        clinical: {
          bg: '#0f172a',
          surface: '#1e293b',
          card: '#1e293b',
          border: '#334155',
          text: '#f8fafc',
          muted: '#94a3b8'
        }
      }
    },
  },
  plugins: [],
}
