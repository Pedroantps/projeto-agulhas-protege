export type NivelRisco = 'NORMAL' | 'ATENCAO' | 'ALERTA' | 'EMERGENCIA';

interface RiskBadgeProps {
  nivel: NivelRisco;
  size?: 'sm' | 'md' | 'lg';
}

const BADGE_CONFIG: Record<
  NivelRisco,
  { classes: string; label: string; display: string }
> = {
  NORMAL: {
    classes:
      'border-risk-normal/30 bg-risk-normal-light text-risk-normal-dark dark:bg-risk-normal-dark-bg dark:text-risk-normal-dark-text',
    label: 'Normal — rio em nível habitual',
    display: 'NORMAL',
  },
  ATENCAO: {
    classes:
      'border-risk-atencao/30 bg-risk-atencao-light text-risk-atencao-dark dark:bg-risk-atencao-dark-bg dark:text-risk-atencao-dark-text',
    label: 'Atenção — elevação acima do habitual',
    display: 'ATENÇÃO',
  },
  ALERTA: {
    classes:
      'border-risk-alerta/30 bg-risk-alerta-light text-risk-alerta-dark dark:bg-risk-alerta-dark-bg dark:text-risk-alerta-dark-text',
    label: 'Alerta — risco de transbordamento',
    display: 'ALERTA',
  },
  EMERGENCIA: {
    classes:
      'animate-pulse border-risk-emergencia/30 bg-risk-emergencia-light text-risk-emergencia-dark motion-reduce:animate-none dark:bg-risk-emergencia-dark-bg dark:text-risk-emergencia-dark-text',
    label: 'Emergência — inundação em curso ou iminente',
    display: 'EMERGÊNCIA',
  },
};

const SIZE_CLASSES = {
  sm: 'px-2.5 py-0.5 text-[10px]',
  md: 'px-3 py-1 text-xs',
  lg: 'px-4 py-1.5 text-sm',
};

export function RiskBadge({ nivel, size = 'sm' }: RiskBadgeProps) {
  const { classes, label, display } = BADGE_CONFIG[nivel];

  return (
    <span
      className={`whitespace-nowrap rounded-full border font-bold ${SIZE_CLASSES[size]} ${classes}`}
      role="status"
      aria-label={`Classificação de risco: ${label}`}
    >
      {display}
    </span>
  );
}
