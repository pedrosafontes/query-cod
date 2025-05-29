/** @type {import('tailwindcss').Config} */

const colors = require('tailwindcss/colors')

module.exports = {
  darkMode: ["class"],
  content: ["./frontend/**/*.{js,ts,jsx,tsx}"],
  theme: {
  	extend: {
  		colors: {
  			background: 'oklch(1 0 0)',
  			foreground: 'oklch(0.145 0 0)',
  			card: {
  				DEFAULT: 'oklch(1 0 0)',
  				foreground: 'oklch(0.145 0 0)'
  			},
  			popover: {
  				DEFAULT: 'oklch(1 0 0)',
  				foreground: 'oklch(0.145 0 0)'
  			},
  			primary: {
  				DEFAULT: 'oklch(0.205 0 0)',
  				foreground: 'oklch(0.985 0 0)'
  			},
  			secondary: {
  				DEFAULT: 'oklch(0.97 0 0)',
  				foreground: 'oklch(0.205 0 0)'
  			},
  			muted: {
  				DEFAULT: 'oklch(0.97 0 0)',
  				foreground: 'oklch(0.556 0 0)'
  			},
  			accent: {
  				DEFAULT: 'oklch(0.97 0 0)',
  				foreground: 'oklch(0.205 0 0)'
  			},
  			destructive: 'oklch(0.577 0.245 27.325)',
  			border: 'oklch(0.922 0 0)',
  			input: 'oklch(0.922 0 0)',
  			ring: 'oklch(0.708 0 0)',
  			chart: {
  				'1': 'oklch(0.646 0.222 41.116)',
  				'2': 'oklch(0.6 0.118 184.704)',
  				'3': 'oklch(0.398 0.07 227.392)',
  				'4': 'oklch(0.828 0.189 84.429)',
  				'5': 'oklch(0.769 0.188 70.08)'
  			},
  			sidebar: {
  				DEFAULT: 'oklch(0.985 0 0)',
  				foreground: 'oklch(0.145 0 0)',
  				primary: {
  					DEFAULT: 'oklch(0.205 0 0)',
  					foreground: 'oklch(0.985 0 0)'
  				},
  				accent: {
  					DEFAULT: 'oklch(0.97 0 0)',
  					foreground: 'oklch(0.205 0 0)'
  				},
  				border: 'oklch(0.922 0 0)',
  				ring: 'oklch(0.708 0 0)'
  			}
  		},
  		keyframes: {
  			'accordion-down': {
  				from: {
  					height: '0'
  				},
  				to: {
  					height: 'var(--radix-accordion-content-height)'
  				}
  			},
  			'accordion-up': {
  				from: {
  					height: 'var(--radix-accordion-content-height)'
  				},
  				to: {
  					height: '0'
  				}
  			}
  		},
  		animation: {
  			'accordion-down': 'accordion-down 0.2s ease-out',
  			'accordion-up': 'accordion-up 0.2s ease-out'
  		}
  	}
  },
  plugins: [],
}