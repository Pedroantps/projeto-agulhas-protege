import type { AuthProfile } from '@/stores/authStore';

const API_BASE = '/api/v1';

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
  ) {
    super(detail);
    this.name = 'ApiError';
  }
}

function createRequestOptions(options: RequestInit): RequestInit {
  const headers = new Headers(options.headers);
  if (options.body && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  return {
    ...options,
    credentials: 'include',
    headers,
  };
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.status === 204) return undefined as T;

  const content = await response.text();
  if (!content) return undefined as T;

  try {
    return JSON.parse(content) as T;
  } catch {
    return content as T;
  }
}

function getErrorDetail(body: unknown): string {
  if (typeof body !== 'object' || body === null) return 'Erro desconhecido.';

  const data = body as Record<string, unknown>;
  if (typeof data.detail === 'string') return data.detail;
  // Erros de validação do Pydantic chegam como lista em `detail`.
  if (Array.isArray(data.detail) && data.detail.length > 0) {
    const first = data.detail[0] as { loc?: unknown[]; msg?: string };
    if (first.loc?.includes('email')) {
      return 'Informe um e-mail válido, por exemplo nome@dominio.com.';
    }
    if (first.msg) return first.msg.replace(/^Value error, /, '');
  }
  if (typeof data.erro === 'string') return data.erro;
  return 'Erro desconhecido.';
}

async function throwApiError(response: Response): Promise<never> {
  const detail = getErrorDetail(await parseResponse<unknown>(response));
  const messages: Record<number, string> = {
    400: `Dados inválidos: ${detail}`,
    403: 'Você não tem permissão para esta ação.',
    404: 'Recurso não encontrado.',
    422: `Erro de validação: ${detail}`,
    429: 'Muitas requisições. Tente novamente em alguns segundos.',
    500: 'Erro interno do servidor. Contate o suporte.',
  };

  throw new ApiError(response.status, messages[response.status] ?? detail);
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const requestOptions = createRequestOptions(options);
  let response = await fetch(`${API_BASE}${path}`, requestOptions);

  if (response.status === 401 && !path.startsWith('/auth/')) {
    const refreshResponse = await fetch(`${API_BASE}/auth/refresh`, {
      method: 'POST',
      credentials: 'include',
    });

    if (!refreshResponse.ok) {
      window.location.assign('/login');
      throw new ApiError(401, 'Sessão expirada. Redirecionando...');
    }

    response = await fetch(`${API_BASE}${path}`, requestOptions);
  }

  if (!response.ok) await throwApiError(response);
  return parseResponse<T>(response);
}

export interface EstacoesStatusResponse {
  estacao_id: string;
  codigo_externo: string;
  nome: string;
  rio: string;
  nivel_atual_metros: string;
  classificacao_risco: 'NORMAL' | 'ATENCAO' | 'ALERTA' | 'EMERGENCIA';
  data_hora_leitura: string;
  dados_desatualizados: boolean;
  cotas: { atencao: string; alerta: string; emergencia: string };
}

export interface LeituraHistorico {
  id: string;
  data_hora: string;
  nivel_metros: string;
  classificacao: string;
}

export interface OcorrenciaInput {
  estacao_id: string;
  alerta_id?: string;
  localizacao: string;
  descricao: string;
}

export interface OcorrenciaItem {
  id: string;
  estacao_id: string;
  estacao_nome?: string | null;
  usuario_id?: string | null;
  usuario_nome?: string | null;
  alerta_id?: string | null;
  localizacao: string;
  descricao: string;
  status: 'ABERTA' | 'EM_ANDAMENTO' | 'ENCERRADA';
  criado_em: string;
  atualizado_em?: string | null;
}

export interface CotasInput {
  cota_atencao: string;
  cota_alerta: string;
  cota_emergencia: string;
}

export interface LoginResponse {
  nome: string;
  perfil: AuthProfile;
}

export const fetchStatusAtual = (): Promise<EstacoesStatusResponse[]> =>
  request('/estacoes/status-atual');

export const fetchHistorico = (
  estacaoId: string,
  horas: number,
): Promise<LeituraHistorico[]> => {
  const params = new URLSearchParams({
    estacao_id: estacaoId,
    horas: String(horas),
  });
  return request(`/leituras/historico?${params.toString()}`);
};

export const fetchOcorrencias = (
  estacaoId?: string,
): Promise<OcorrenciaItem[]> => {
  const params = estacaoId
    ? `?estacao_id=${encodeURIComponent(estacaoId)}`
    : '';
  return request(`/ocorrencias${params}`);
};

export const criarOcorrencia = (data: OcorrenciaInput): Promise<OcorrenciaItem> =>
  request('/ocorrencias', {
    method: 'POST',
    body: JSON.stringify(data),
  });

export const atualizarStatusOcorrencia = (
  id: string,
  status: 'ABERTA' | 'EM_ANDAMENTO' | 'ENCERRADA',
): Promise<OcorrenciaItem> =>
  request(`/ocorrencias/${encodeURIComponent(id)}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });

export const excluirOcorrencia = (id: string): Promise<void> =>
  request<void>(`/ocorrencias/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  });

export const atualizarCotas = (estacaoId: string, data: CotasInput) =>
  request(`/estacoes/${encodeURIComponent(estacaoId)}/cotas`, {
    method: 'PUT',

    body: JSON.stringify(data),
  });

export const loginApi = (data: { email: string; senha: string }) =>
  request<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(data),
  });

/**
 * Restaura a sessão a partir dos cookies httpOnly (após recarregar a página).
 * Tenta renovar com o refresh token uma vez; devolve null se não houver sessão válida.
 */
export const restaurarSessao = async (): Promise<LoginResponse | null> => {
  try {
    return await request<LoginResponse>('/auth/me');
  } catch {
    try {
      await request('/auth/refresh', { method: 'POST' });
      return await request<LoginResponse>('/auth/me');
    } catch {
      return null;
    }
  }
};

export const logoutApi = (): Promise<void> =>
  request<void>('/auth/logout', {
    method: 'POST',
  });


export interface CorrelacaoVariavel {
  id: string;
  nome: string;
  origem: string;
  tipo: 'chuva_sjb_lag' | 'chuva_acumulada' | 'vazao_funil' | 'previsao';
  lag_horas: string;
  coeficiente_r: number;
  relevancia: 'ALTA' | 'MEDIA' | 'MODERADA';
  descricao_fisica: string;
}

export interface PrevisaoNivelDia {
  dia_offset: number;
  rotulo: string;
  data_alvo: string;
  chuva_prevista_mm: string;
  vazao_funil_esperada_m3s: string;
  nivel_estimado_metros: string;
  probabilidade_alerta: number;
  probabilidade_emergencia: number;
  classificacao_risco: 'NORMAL' | 'ATENCAO' | 'ALERTA' | 'EMERGENCIA';
  confiabilidade_percentual: number;
}

export interface RecomendacaoFunil {
  vazao_atual_m3s: string;
  vazao_maxima_sugerida_m3s: string;
  tempo_transito_medio: string;
  situacao_remanso: 'FAVORAVEL' | 'ALERTA_REMANSO' | 'REMANSO_CRITICO';
  acao_preventiva: string;
  impacto_estimado_leito_cm: number;
}

export interface TelemetriaBacia {
  chuva_sjb_1h_lag4_mm: string;
  chuva_sjb_1h_lag5_mm: string;
  chuva_sjb_1h_lag6_mm: string;
  chuva_sjb_acumulada_12h_mm: string;
  chuva_sjb_acumulada_24h_mm: string;
  chuva_sjb_acumulada_48h_mm: string;
  chuva_sjb_acumulada_168h_mm: string;
  saturacao_solo_sjb_percent: number;
  chuva_resende_acumulada_12h_mm: string;
  chuva_resende_acumulada_24h_mm: string;
  chuva_resende_acumulada_48h_mm: string;
  chuva_resende_acumulada_168h_mm: string;
  vazao_funil_atual_m3s: string;
  vazao_funil_lag1_m3s: string;
  vazao_funil_lag2_m3s: string;
  vazao_funil_media_transito_m3s: string;
}

export interface SesmariaDashboardResponse {
  estacao_id: string;
  nome: string;
  rio: string;
  municipio: string;
  nivel_atual_metros: string;
  classificacao_risco: 'NORMAL' | 'ATENCAO' | 'ALERTA' | 'EMERGENCIA';
  data_hora_leitura: string;
  cota_atencao: string;
  cota_alerta: string;
  cota_emergencia: string;
  telemetria: TelemetriaBacia;
  correlacoes: CorrelacaoVariavel[];
  previsoes: PrevisaoNivelDia[];
  recomendacao_funil: RecomendacaoFunil;
  eventos_criticos_base: number;
  mensagem_alerta_whatsapp: string;
  dados_disponiveis: boolean;
  fonte_dados: string;
  coletado_em: string | null;
  chuva_estacao_1h_mm: string | null;
  chuva_estacao_24h_mm: string | null;
  foto_estacao_url: string | null;
  foto_estacao_data_hora: string | null;
}

export const fetchSesmariaDashboard = (): Promise<SesmariaDashboardResponse> =>
  request('/sesmaria/dashboard-ia');

export const fetchAlertaWhatsApp = (): Promise<{
  mensagem: string;
  url_whatsapp: string;
}> => request('/sesmaria/alerta-whatsapp');

export interface StatusColeta {
  habilitada: boolean;
  intervalo_minutos: number;
  ultima_coleta: string | null;
  ultima_leitura: string | null;
  total_leituras: number;
  fontes: string[];
}

export interface ExecucaoColeta {
  leituras_novas: number;
  fontes_ok: string[];
  erros: Record<string, string>;
}

export const fetchStatusColeta = (): Promise<StatusColeta> =>
  request('/coleta/status');

export const executarColeta = (): Promise<ExecucaoColeta> =>
  request('/coleta/executar', { method: 'POST' });
