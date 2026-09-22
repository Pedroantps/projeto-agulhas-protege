import { render, screen } from '@testing-library/react';

import { CardSkeleton, PageSkeleton, Skeleton } from '../Skeleton';

describe('Skeleton', () => {
  it('aplica dimensões, arredondamento e classe personalizados', () => {
    const { container } = render(
      <Skeleton
        width="w-20"
        height="h-8"
        rounded="full"
        className="shrink-0"
      />,
    );

    expect(container.firstChild).toHaveClass(
      'w-20',
      'h-8',
      'rounded-full',
      'shrink-0',
    );
    expect(container.firstChild).toHaveAttribute('aria-hidden', 'true');
  });

  it('expõe estado de carregamento no CardSkeleton', () => {
    render(<CardSkeleton />);

    expect(
      screen.getByRole('status', { name: 'Carregando informações do cartão' }),
    ).toHaveAttribute('aria-busy', 'true');
  });

  it('renderiza três cartões no PageSkeleton', () => {
    render(<PageSkeleton />);

    expect(
      screen.getByRole('status', { name: 'Carregando página' }),
    ).toBeInTheDocument();
    expect(
      screen.getAllByRole('status', {
        name: 'Carregando informações do cartão',
      }),
    ).toHaveLength(3);
  });
});
