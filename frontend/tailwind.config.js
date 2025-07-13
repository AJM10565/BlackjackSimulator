/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'felt-green': '#2d6e3e',
        'card-red': '#dc2626',
        'card-black': '#000000',
      }
    },
  },
  plugins: [],
}