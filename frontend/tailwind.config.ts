import type { Config } from 'tailwindcss';

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    fontFamily: {
      sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
    },
    extend: {
      colors: {
        risk: {
          normal: {
            DEFAULT: '#059669',
            light: '#d1fae5',
            dark: '#065f46',
            'dark-bg': 'rgba(6, 95, 70, 0.3)',
            'dark-text': '#34d399',
          },
          atencao: {
            DEFAULT: '#d97706',
            light: '#fef3c7',
            dark: '#92400e',
            'dark-bg': 'rgba(146, 64, 14, 0.3)',
            'dark-text': '#fbbf24',
          },
          alerta: {
            DEFAULT: '#ea580c',
            light: '#ffedd5',
            dark: '#9a3412',
            'dark-bg': 'rgba(154, 52, 18, 0.3)',
            'dark-text': '#fb923c',
          },
          emergencia: {
            DEFAULT: '#dc2626',
            light: '#fee2e2',
            dark: '#991b1b',
            'dark-bg': 'rgba(153, 27, 27, 0.3)',
            'dark-text': '#f87171',
          },
        },
        surface: {
          primary: '#ffffff',
          secondary: '#f8fafc',
          'dark-primary': '#0f172a',
          'dark-secondary': '#1e293b',
        },
        border: {
          DEFAULT: '#e2e8f0',
          dark: '#334155',
        },
        brand: {
          DEFAULT: '#0284c7',
          light: '#38bdf8',
          dark: '#0369a1',
        },
      },
      boxShadow: {
        card: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'card-hover':
          '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
        modal: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
