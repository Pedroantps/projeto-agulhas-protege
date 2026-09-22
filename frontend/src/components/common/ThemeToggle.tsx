import { Moon, Sun } from 'lucide-react';

import { useThemeStore } from '@/stores/themeStore';

export function ThemeToggle() {
  const theme = useThemeStore((state) => state.theme);
  const toggleTheme = useThemeStore((state) => state.toggleTheme);

  return (
    <button
      id="theme-toggle"
      type="button"
      onClick={toggleTheme}
      className="rounded-lg bg-slate-100 p-2 text-slate-600 transition-colors hover:bg-slate-200 focus:outline-none focus:ring-2 focus:ring-brand focus:ring-offset-2 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600 dark:focus:ring-offset-slate-900"
      aria-label={theme === 'dark' ? 'Ativar modo claro' : 'Ativar modo escuro'}
      title={theme === 'dark' ? 'Ativar modo claro' : 'Ativar modo escuro'}
    >
      {theme === 'dark' ? (
        <Sun className="size-5" aria-hidden="true" />
      ) : (
        <Moon className="size-5" aria-hidden="true" />
      )}
    </button>
  );
}
