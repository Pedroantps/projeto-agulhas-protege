import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

import { useThemeStore } from '@/stores/themeStore';

import { ThemeToggle } from '../ThemeToggle';

describe('ThemeToggle', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove('dark');
    document.documentElement.style.colorScheme = '';
    useThemeStore.setState({ theme: 'light' });
  });

  it('alterna para dark mode, atualiza o documento e persiste', async () => {
    const user = userEvent.setup();
    render(<ThemeToggle />);

    const toggle = screen.getByRole('button', { name: 'Ativar modo escuro' });
    await user.click(toggle);

    expect(document.documentElement).toHaveClass('dark');
    expect(document.documentElement.style.colorScheme).toBe('dark');
    expect(
      screen.getByRole('button', { name: 'Ativar modo claro' }),
    ).toBeInTheDocument();
    expect(localStorage.getItem('agulhas-theme')).toContain('"theme":"dark"');
  });

  it('restaura o tema persistido ao reidratar', async () => {
    localStorage.setItem(
      'agulhas-theme',
      JSON.stringify({ state: { theme: 'dark' }, version: 0 }),
    );

    await useThemeStore.persist.rehydrate();

    expect(useThemeStore.getState().theme).toBe('dark');
    expect(document.documentElement).toHaveClass('dark');
  });
});
