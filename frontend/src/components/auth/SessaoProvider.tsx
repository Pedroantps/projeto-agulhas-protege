import React, { useEffect, useState } from 'react';

import { PageSkeleton } from '@/components/common';
import { restaurarSessao } from '@/services/api';
import { useAuthStore } from '@/stores/authStore';

/**
 * Restaura a sessão (nome e perfil) pelos cookies httpOnly ao abrir ou recarregar o site,
 * antes de renderizar as rotas protegidas.
 */
export const SessaoProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const setUser = useAuthStore((state) => state.setUser);
  const [pronto, setPronto] = useState(false);

  useEffect(() => {
    let ativo = true;
    void restaurarSessao().then((usuario) => {
      if (!ativo) return;
      if (usuario) setUser({ nome: usuario.nome, perfil: usuario.perfil });
      setPronto(true);
    });
    return () => {
      ativo = false;
    };
  }, [setUser]);

  return pronto ? <>{children}</> : <PageSkeleton />;
};

export default SessaoProvider;
