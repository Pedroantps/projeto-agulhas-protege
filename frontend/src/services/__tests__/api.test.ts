import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import {
  ApiError,
  atualizarCotas,
  criarOcorrencia,
  fetchHistorico,
  fetchStatusAtual,
  loginApi,
  logoutApi,
} from '../api';

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('API client', () => {
  const fetchMock = vi.fn<typeof fetch>();

  beforeEach(() => {
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    fetchMock.mockReset();
    vi.unstubAllGlobals();
  });

  it('consulta o status atual enviando cookies', async () => {
    const payload = [{ estacao_id: 'est-1', nome: 'Estação Central' }];
    fetchMock.mockResolvedValueOnce(jsonResponse(payload));

    await expect(fetchStatusAtual()).resolves.toEqual(payload);
    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/estacoes/status-atual',
      expect.objectContaining({ credentials: 'include' }),
    );
  });

  it('codifica os parâmetros do histórico', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse([]));

    await fetchHistorico('estação 1', 24);

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/v1/leituras/historico?estacao_id=esta%C3%A7%C3%A3o+1&horas=24',
      expect.any(Object),
    );
  });

  it('serializa JSON nas operações de escrita', async () => {
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ id: 'oc-1' }, 201))
      .mockResolvedValueOnce(jsonResponse({ ok: true }));
    const ocorrencia = {
      estacao_id: 'est-1',
      localizacao: 'Campos Elíseos',
      descricao: 'Alagamento na via',
    };

    await criarOcorrencia(ocorrencia);
    await atualizarCotas('estação/1', {
      cota_atencao: '2.00',
      cota_alerta: '2.50',
      cota_emergencia: '3.20',
    });

    const firstOptions = fetchMock.mock.calls[0]?.[1];
    expect(firstOptions).toMatchObject({
      method: 'POST',
      body: JSON.stringify(ocorrencia),
      credentials: 'include',
    });
    expect(new Headers(firstOptions?.headers).get('Content-Type')).toBe(
      'application/json',
    );
    expect(fetchMock.mock.calls[1]?.[0]).toBe(
      '/api/v1/estacoes/esta%C3%A7%C3%A3o%2F1/cotas',
    );
  });

  it('faz refresh e repete a requisição após 401', async () => {
    const payload = [{ estacao_id: 'est-1' }];
    fetchMock
      .mockResolvedValueOnce(jsonResponse({ detail: 'Não autenticado' }, 401))
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(jsonResponse(payload));

    await expect(fetchStatusAtual()).resolves.toEqual(payload);
    expect(fetchMock).toHaveBeenNthCalledWith(2, '/api/v1/auth/refresh', {
      method: 'POST',
      credentials: 'include',
    });
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it('não tenta refresh nas rotas de autenticação', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse({ detail: 'Credenciais inválidas' }, 401),
    );

    await expect(
      loginApi({ email: 'ana@example.com', senha: 'incorreta' }),
    ).rejects.toEqual(
      expect.objectContaining({
        name: 'ApiError',
        status: 401,
        detail: 'Credenciais inválidas',
      }),
    );
    expect(fetchMock).toHaveBeenCalledOnce();
  });

  it.each([
    [400, 'Dados inválidos: conteúdo inválido'],
    [403, 'Você não tem permissão para esta ação.'],
    [404, 'Recurso não encontrado.'],
    [422, 'Erro de validação: conteúdo inválido'],
    [429, 'Muitas requisições. Tente novamente em alguns segundos.'],
    [500, 'Erro interno do servidor. Contate o suporte.'],
  ])('contextualiza erros HTTP %i', async (status, message) => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse({ erro: 'conteúdo inválido' }, status),
    );

    await expect(loginApi({ email: 'a@b.com', senha: 'x' })).rejects.toThrow(
      message,
    );
  });

  it('preserva detalhe em status sem mensagem específica', async () => {
    fetchMock.mockResolvedValueOnce(
      jsonResponse({ detail: 'Servidor indisponível' }, 503),
    );

    const error = await loginApi({ email: 'a@b.com', senha: 'x' }).catch(
      (caught: unknown) => caught,
    );
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({
      status: 503,
      detail: 'Servidor indisponível',
    });
  });

  it('aceita respostas sem conteúdo', async () => {
    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }));
    await expect(logoutApi()).resolves.toBeUndefined();
  });

  it('aceita respostas de texto e erro sem objeto', async () => {
    fetchMock
      .mockResolvedValueOnce(new Response('ok', { status: 200 }))
      .mockResolvedValueOnce(new Response('falha', { status: 418 }));

    await expect(loginApi({ email: 'a@b.com', senha: 'x' })).resolves.toBe(
      'ok',
    );
    await expect(loginApi({ email: 'a@b.com', senha: 'x' })).rejects.toThrow(
      'Erro desconhecido.',
    );
  });
});
