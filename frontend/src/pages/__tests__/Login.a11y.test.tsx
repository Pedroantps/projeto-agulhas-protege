import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { checkA11y } from '@/test-setup';
import { Login } from '../Login';
import * as authHook from '@/hooks/useAuth';

vi.mock('@/hooks/useAuth');

describe('Login — Acessibilidade', () => {
  it('não tem violações WCAG AA', async () => {
    vi.spyOn(authHook, 'useAuth').mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    const { container } = render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );

    const results = await checkA11y(container);
    expect(results.violations).toEqual([]);
  });
});
