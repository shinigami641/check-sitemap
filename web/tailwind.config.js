/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "Segoe UI", "Roboto", "Ubuntu", "Cantarell", "Noto Sans", "sans-serif"],
      },
      colors: {
        brand: {
          50: '#f5f9ff',
          100: '#eaf2ff',
          200: '#cfe0ff',
          300: '#a8c4ff',
          400: '#6f9fff',
          500: '#4a86ff',
          600: '#2f6dff',
          700: '#2559d6',
          800: '#1e47aa',
          900: '#1a3b8c',
        },
      },
    },
  },
  plugins: [],
}