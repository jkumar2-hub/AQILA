/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // AQILA design system — from API_CONTRACTS.md node colour reference
        teal: {
          DEFAULT: '#1D9E75',
          50:  '#e8faf4',
          100: '#c3f0e1',
          200: '#83dfc0',
          300: '#43ce9e',
          400: '#1D9E75',
          500: '#157a5a',
          600: '#0f5a42',
        },
        amber: {
          DEFAULT: '#EF9F27',
        },
        violet: {
          DEFAULT: '#534AB7',
        },
        navy: {
          50:  '#e8eaf6',
          100: '#c5cae9',
          200: '#9fa8da',
          300: '#7986cb',
          400: '#5c6bc0',
          500: '#3949ab',
          600: '#303f9f',
          700: '#283593',
          800: '#1a237e',
          900: '#0d1117',
          950: '#080c12',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
