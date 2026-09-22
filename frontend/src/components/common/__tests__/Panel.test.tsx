import { render, screen } from '@testing-library/react';

import { Panel } from '../Panel';

describe('Panel', () => {
  it('renderiza título, conteúdo e associação acessível', () => {
    render(
      <Panel id="nivel-rio" title="Nível do rio" className="mt-4">
        <p>2,35 metros</p>
      </Panel>,
    );

    const panel = screen.getByRole('region', { name: 'Nível do rio' });
    expect(panel).toHaveAttribute('id', 'nivel-rio');
    expect(panel).toHaveClass('mt-4');
    expect(screen.getByText('2,35 metros')).toBeInTheDocument();
  });

  it('renderiza sem título opcional', () => {
    const { container } = render(<Panel>Conteúdo</Panel>);

    expect(container.querySelector('section')).not.toHaveAttribute(
      'aria-labelledby',
    );
  });
});
