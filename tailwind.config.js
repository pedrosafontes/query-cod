/** @type {import('tailwindcss').Config} */

const colors = require('tailwindcss/colors')

module.exports = {
  darkMode: ["class"],
  content: ["./frontend/**/*.{js,ts,jsx,tsx}"],
  theme: {
  	extend: {
  		colors: {
        destructive: colors.red[500],
        background: colors.white,
  			primary: colors.gray[950],
  			'primary-foreground': colors.white,
        'muted-foreground': colors.gray[500],
        secondary: colors.gray[200],
        'secondary-foreground': colors.gray[950],
        sidebar: {
          DEFAULT: colors.gray[50],
          foreground: colors.gray[800],
          primary: colors.gray[100],
          'primary-foreground': colors.gray[900],
          accent: colors.gray[200],
          'accent-foreground': colors.gray[900],
          border: colors.gray[300],
          ring: colors.gray[400],
        },
        popover: colors.white,
  		}
  	}
  },
  plugins: [],
}