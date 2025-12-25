/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        // Deep trustworthy blue
        primary: {
          50: '#F0F6FA',
          100: '#E8F1F8',  // Secondary blue
          200: '#D1E3F1',
          300: '#A3C6E2',
          400: '#75A9D3',
          500: '#478CC4',
          600: '#2E74B5', // Slightly lighter than 700
          700: '#0F4C81', // Main Primary
          800: '#0C3D68',
          900: '#082946',
          950: '#041728',
        },
        // Warm/Neutral grays
        gray: {
          50: '#FAFAF9',  // Warm off-white
          100: '#F5F5F4',
          200: '#E7E5E4',
          300: '#D6D3D1',
          400: '#A8A29E',
          500: '#78716C',
          600: '#57534E',
          700: '#44403C',
          800: '#292524',
          900: '#1C1917',
          950: '#0C0A09',
        },
        // Semantic colors
        success: {
          50: '#F0FDF4',
          500: '#16A34A',
          700: '#15803D',
        },
        warning: {
          50: '#FFFBEB',
          500: '#D97706', // Muted orange/amber
          700: '#B45309',
        },
        error: {
          50: '#FEF2F2',
          500: '#DC2626',
          700: '#B91C1C',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        serif: ['Fraunces', 'serif'],
        display: ['Fraunces', 'serif'],
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
      },
      boxShadow: {
        'card': '0 2px 8px rgba(0,0,0,0.08)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.12)',
      },
    },
  },
  plugins: [],
}
