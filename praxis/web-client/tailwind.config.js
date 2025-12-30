/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#ED7A9B', // rose-pompadour
          light: '#f2a2b9',
          dark: '#d85a7f',
        },
        secondary: {
          DEFAULT: '#73A9C2', // moonstone-blue
          light: '#9dc3d4',
          dark: '#5a8ea3',
        },
        // Mapping existing palette names for direct use if needed
        'rose-pompadour': '#ED7A9B',
        'moonstone-blue': '#73A9C2',

        // Theme-aware colors
        surface: {
          DEFAULT: 'var(--theme-surface)',
          elevated: 'var(--theme-surface-elevated)',
        },
        // Text colors that swap based on theme
        'sys-text': {
          primary: 'var(--theme-text-primary)',
          secondary: 'var(--theme-text-secondary)',
          tertiary: 'var(--theme-text-tertiary)',
        }
      },
      fontFamily: {
        sans: ['"Roboto Flex"', 'match-sys', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px rgba(0, 0, 0, 0.3)',
        'neon': '0 0 10px rgba(237, 122, 155, 0.5)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero-glow': 'linear-gradient(135deg, rgba(237,122,155,0.15) 0%, rgba(115,169,194,0.15) 100%)',
      }
    },
  },
  plugins: [],
}
