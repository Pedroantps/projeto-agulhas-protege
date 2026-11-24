# 🌊 Agulhas Protege — Sistema de Monitoramento e Alerta de Cheias

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4+-38B2AC?style=flat&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com)

Plataforma digital integrada para a população de **Resende-RJ** e para a **Defesa Civil Municipal**, fornecendo monitoramento fluviométrico em tempo real (com foco na Bacia do Rio Sesmaria e afluentes do Rio Paraíba do Sul), projeções preditivas com inteligência analítica, classificação automática de risco de cheias, gerenciamento de cotas e registro operacional de ocorrências de campo.

---

## 📌 Sumário

1. [Visão Geral & Funcionalidades](#-visão-geral--funcionalidades)
2. [Arquitetura & Tecnologias](#-arquitetura--tecnologias)
3. [Pré-requisitos](#-pré-requisitos)
4. [Como Rodar Localmente](#-como-rodar-localmente)
   - [Opção 1: Via Docker Compose (Recomendado)](#opção-1-via-docker-compose-recomendado)
   - [Opção 2: Execução Nativa (Backend + Frontend)](#opção-2-execução-nativa-desenvolvimento)
5. [Credenciais Padrão de Acesso](#-credenciais-padrão-de-acesso-seed)
6. [Estrutura do Projeto](#-estrutura-do-projeto)
7. [Testes e Qualidade de Código](#-testes-e-qualidade-de-código)

---

## 🚀 Visão Geral & Funcionalidades

- **🏠 Portal Público do Cidadão (`/`):**
  - Consulta do nível atual da água em metros com classificação visual imediata de risco (*Normal*, *Atenção*, *Alerta*, *Emergência*).
  - Gráficos históricos de séries temporais com filtros dinâmicos de período (24h, 72h, 7 dias).
  - Alertas automáticos com orientações claras de segurança da Defesa Civil.
  - Indicador de leitura defasada (>2h sem telemetria).
  - Design totalmente responsivo (mobile-first), dark mode e acessibilidade em conformidade com as diretrizes WCAG 2.1 AA.

- **🛡️ Dashboard Operacional da Defesa Civil (`/dashboard`):**
  - Painel de telemetria consolidado para operadores e gestores.
  - **Módulo de IA & Correlação Rio Sesmaria:** Projeção preditiva para +1d a +3d, correlação hidrológica entre precipitação a montante (São José do Barreiro), vazão da Represa do Funil e geração automatizada de relatórios para despacho via WhatsApp.
  - **Registro de Ocorrências:** Cadastro de intervenções de campo da Defesa Civil com validação estrita, proteção contra mass-assignment e persistência auditada.

- **⚙️ Painel de Administração (`/admin`):**
  - Parametrização dinâmica das cotas de risco por estação (*Atenção*, *Alerta*, *Emergência*).
  - Validação técnica rigorosa de ordem de grandeza e trilha de auditoria completa das alterações.

---

## 🛠️ Arquitetura & Tecnologias

### Backend
- **Linguagem & Runtime:** Python 3.12+ gerenciado via [`uv`](https://docs.astral.sh/uv/)
- **Framework Web:** [FastAPI](https://fastapi.tiangolo.com/) com validação por Pydantic v2
- **Banco de Dados:** PostgreSQL 16 com driver assíncrono `psycopg3` e ORM SQLAlchemy 2.0 (`asyncio`)
- **Migrações:** Alembic
- **Segurança & Resiliência:** JWT com suporte a Refresh Token rotation, hash de senhas com `bcrypt`, Rate Limiting via `SlowAPI`, headers de segurança HTTP e logs estruturados em JSON via `structlog`

### Frontend
- **Framework & Build:** [React 18](https://react.dev/) + [Vite](https://vitejs.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Estilização:** [Tailwind CSS](https://tailwindcss.com/) com tokens semânticos e suporte nativo a Dark Mode
- **Gerenciamento de Estado & Dados:** [TanStack React Query v5](https://tanstack.com/query/latest) (cache, revalidação e mutações) + [Zustand](https://github.com/pmndrs/zustand) (autenticação e preferências)
- **Visualização de Dados:** [Recharts](https://recharts.org/) (gráficos de linha, cotas de referência e tooltips acessíveis)
- **Ícones & Notificações:** Lucide React e React Hot Toast

---

## 📋 Pré-requisitos

Para rodar o projeto em sua máquina local, você precisará de:

| Ferramenta | Versão Mínima | Uso |
|:---|:---|:---|
| **Git** | 2.x+ | Controle de versão |
| **Docker & Docker Compose** | 24+ / Compose v2+ | Execução em contêineres (*Opção 1*) |
| **Python** | 3.12+ | Execução nativa do backend (*Opção 2*) |
| **uv** | 0.4+ | Gerenciador rápido de dependências Python (*Opção 2*) |
| **Node.js** | 20+ (LTS) | Execução nativa do frontend (*Opção 2*) |
| **npm** | 10+ | Gerenciador de pacotes do frontend (*Opção 2*) |

> [!TIP]
> Caso ainda não tenha o `uv` instalado, instale com:
> - **Windows (PowerShell):** `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
> - **Linux/macOS:** `curl -LsSf https://astral.sh/uv/install.sh | sh`

---

## 💻 Como Rodar Localmente

### Opção 1: Via Docker Compose (Recomendado)

Esta é a maneira mais simples de inicializar toda a aplicação (PostgreSQL, Backend FastAPI e Frontend Vite) com um único comando.

#### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/AgulhasProtege.git
cd AgulhasProtege
```

#### 2. Configure as variáveis de ambiente
Copie o arquivo de exemplo para o arquivo `.env` na raiz do projeto:

**Linux / macOS / Git Bash:**
```bash
cp .env.example .env
```

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

#### 3. Suba os contêineres
```bash
docker compose up --build -d
```

> [!NOTE]
> O contêiner de backend aplicará automaticamente as migrações do banco (`alembic upgrade head`) na inicialização.

#### 4. Popule o banco com os dados iniciais (Seed)
Execute o script de seed dentro do contêiner do backend para criar os usuários padrão e a estação telemétrica:
```bash
docker compose exec backend uv run python scripts/seed.py
```

#### 5. Acesse a aplicação
- **Frontend (Web):** [http://localhost:5173](http://localhost:5173)
- **Documentação Interativa da API (Swagger UI):** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **Documentação Alternativa da API (ReDoc):** [http://localhost:8000/api/redoc](http://localhost:8000/api/redoc)
- **Health Check da API:** [http://localhost:8000/health](http://localhost:8000/health)

Para parar os serviços:
```bash
docker compose down
```

---

### Opção 2: Execução Nativa (Desenvolvimento)

Caso prefira rodar os serviços localmente fora de contêineres para desenvolvimento ativo e depuração rápida.

#### Passo 1: Inicializar o Banco de Dados PostgreSQL

Você pode utilizar uma instância local de PostgreSQL 16 ou iniciar apenas o contêiner do banco via Docker:

```bash
docker compose up db -d
```

O banco estará disponível na porta `5432` com as credenciais padrões (`user: agulhas`, `password: dev_password`, `db: agulhas_protege`).

---

#### Passo 2: Configurar e Rodar o Backend

1. Entre no diretório do backend:
   ```bash
   cd backend
   ```

2. Crie o arquivo de ambiente local a partir do `.env.example`:
   ```bash
   # Linux / macOS / Git Bash
   cp .env.example .env

   # Windows PowerShell
   Copy-Item .env.example .env
   ```

3. Instale as dependências usando o `uv`:
   ```bash
   uv sync --dev
   ```

4. Execute as migrações do banco de dados:
   ```bash
   uv run alembic upgrade head
   ```

5. Execute o script de seed para criar usuários e estações de teste:
   ```bash
   uv run python scripts/seed.py
   ```

6. Inicie o servidor FastAPI em modo de recarregamento contínuo (*hot-reload*):
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

> A API estará rodando em [http://localhost:8000](http://localhost:8000) e os docs em [http://localhost:8000/api/docs](http://localhost:8000/api/docs).

---

#### Passo 3: Configurar e Rodar o Frontend

Abra um novo terminal e siga os passos:

1. Entre no diretório do frontend:
   ```bash
   cd frontend
   ```

2. Instale as dependências do Node.js:
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento Vite:
   ```bash
   npm run dev
   ```

> O Vite disponibilizará o frontend em [http://localhost:5173](http://localhost:5173). As requisições direcionadas para `/api/*` serão redirecionadas automaticamente pelo proxy reverso do Vite para `http://localhost:8000`.

---

## 📡 Dados Reais (coleta feita pelo backend)

O backend busca sozinho, a cada 10 minutos (`COLETA_INTERVALO_MINUTOS`), as fontes públicas abaixo e grava no PostgreSQL. Nenhum cliente (web ou mobile) precisa consultar essas fontes diretamente.

| Dado | Fonte | Onde é usado |
|---|---|---|
| Nível do Rio Sesmaria (série horária) | CEMADEN, estação `330420118H` | Cards, gráfico histórico, classificação de risco |
| Chuva medida e foto da câmera | CEMADEN, mesma estação | Painel "Dados da Estação em Tempo Real" |
| Chuva observada e prevista (Resende e São José do Barreiro) | Open-Meteo | Previsão +24h/+48h/+72h e telemetria da bacia |
| Vazão defluente da Represa do Funil | ONS Dados Abertos | Painel do Funil e correlação |

O painel de previsão usa um modelo hidrológico simplificado (tanque linear com cenários de chuva), calculado sobre esses dados. As correlações de Pearson são calculadas sobre as leituras reais armazenadas. A recomendação para o Funil é uma heurística de apoio à decisão e não substitui comunicados oficiais.

Endpoints novos: `GET /api/v1/coleta/status` (público), `POST /api/v1/coleta/executar` (admin), `GET /api/v1/auth/me` (restaura sessão) e `DELETE /api/v1/ocorrencias/{id}` (com auditoria).

> **Windows:** o `psycopg` assíncrono não funciona no loop padrão do Windows. Para rodar a API fora do Docker no Windows, use `uv run python scripts/run_dev.py`.

## 🚀 Deploy

Veja [docs/PLANO_DEPLOY.md](docs/PLANO_DEPLOY.md) (passo a passo) e [docs/ROTEIRO_DE_TESTES.md](docs/ROTEIRO_DE_TESTES.md) (roteiro de validação).

## 🔑 Credenciais Padrão de Acesso (Seed)

O script de inicialização (`scripts/seed.py`) cadastra as seguintes contas para testes locais:

| Perfil | E-mail | Senha | Acesso / Permissões |
|:---|:---|:---|:---|
| **Administrador** | `testeadmin@teste.com` | `Teste@2029` | Acesso total: Portal público, Dashboard (`/dashboard`), IA Sesmaria, Registro de Ocorrências e Gestão de Cotas de Risco (`/admin`). |
| **Operador Defesa Civil (usuário comum)** | `testecomum@teste.com` | `Teste@2029` | Acesso operacional: Portal público, Dashboard (`/dashboard`), visualização de telemetria, IA Sesmaria e Registro de Ocorrências. |
| **Cidadão (Público)** | *Não requer autenticação* | — | Acesso livre à página inicial (`/`): telemetria atual, gráficos históricos e avisos públicos. |

---

## 📂 Estrutura do Projeto

```text
AgulhasProtege/
├── .env.example              # Exemplo de variáveis de ambiente raiz (Docker Compose)
├── docker-compose.yml        # Orquestração do DB, Backend e Frontend
├── README.md                 # Este documento
├── backend/
│   ├── app/
│   │   ├── api/v1/           # Rotas da API (auth, estacoes, leituras, ocorrencias, sesmaria)
│   │   ├── core/             # Configurações, segurança (JWT, hash) e middlewares
│   │   ├── db/               # Sessão do SQLAlchemy e migrações Alembic
│   │   ├── models/           # Entidades SQLAlchemy (Usuario, Estacao, Leitura, etc.)
│   │   ├── schemas/          # Modelos Pydantic v2 (validações e contratos)
│   │   └── services/         # Regras de negócio (classificação de risco, correlação IA)
│   ├── scripts/
│   │   ├── seed.py           # População inicial com usuários e telemetria
│   │   └── verify_database.py# Script de diagnóstico de integridade do banco
│   ├── tests/                # Testes unitários e de integração (pytest)
│   ├── pyproject.toml        # Metadados e dependências Python (uv)
│   └── Dockerfile            # Imagem do container Backend
├── frontend/
│   ├── src/
│   │   ├── components/       # Componentes reutilizáveis (Panel, RiskBadge, Modal, Gráficos)
│   │   ├── pages/            # Páginas (HomePublica, Login, Dashboard, Admin)
│   │   ├── services/         # Clientes Axios/API com interceptors de autenticação
│   │   ├── stores/           # Zustand stores (authStore, themeStore)
│   │   ├── types/            # Tipagens TypeScript dos contratos da API
│   │   └── App.tsx           # Configuração de rotas e providers
│   ├── e2e/                  # Testes End-to-End com Playwright
│   ├── package.json          # Dependências e scripts do Frontend
│   └── vite.config.ts        # Configuração do Vite com proxy reverso da API
└── plans/                    # Especificação formal de requisitos e SDDs de arquitetura
```

---

## 🧪 Testes e Qualidade de Código

### Backend

Na pasta `backend/`:

```bash
# Executar todos os testes com relatório de cobertura de código
uv run pytest

# Executar linter de código (Ruff)
uv run ruff check .

# Formatar código automaticamente
uv run ruff format .

# Verificação estática de tipos (mypy)
uv run mypy app
```

### Frontend

Na pasta `frontend/`:

```bash
# Executar testes unitários e de componentes (Vitest)
npm run test

# Executar testes com cobertura
npm run test:coverage

# Executar testes de acessibilidade (axe-core)
npm run test:a11y

# Executar testes End-to-End (Playwright)
npm run test:e2e

# Verificar qualidade de código com ESLint
npm run lint

# Checagem de formatação (Prettier)
npm run format:check
```

---
