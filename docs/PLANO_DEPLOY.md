# Plano de Deploy e Entrega — Agulhas Protege

Objetivo: ter o sistema 100% online (sem instalação ou execução local), com todos os serviços disponíveis até o fim da avaliação, e enviar o link ao Moodle com as contas de teste e o roteiro.

## 1. Arquitetura de produção

```
Navegador ──HTTPS──► Serviço web único (Docker)            ──► PostgreSQL gerenciado
                     ├─ FastAPI  (/api/v1/*, /health)            (Supabase)
                     ├─ React compilado (/, /dashboard, /admin)
                     └─ Coletor em segundo plano (a cada 10 min) ──► CEMADEN · Open-Meteo · ONS
```

- **Um só domínio** para site e API: os cookies httpOnly de login funcionam sem CORS e sem ajustes.
- **Imagem única** (`Dockerfile` na raiz): compila o frontend, instala o backend e, ao iniciar, roda `alembic upgrade head`, cria as contas de teste e a estação (`seed.py --sem-coleta`) e sobe a API. A coleta começa sozinha junto com o servidor.
- **Hospedagem:** Render (serviço web, plano gratuito, `render.yaml` pronto) + Supabase (PostgreSQL gratuito).

## 2. Pré-requisitos (decisões e contas do grupo)

| Item | Quem faz | Observação |
|---|---|---|
| Repositório no GitHub com este código | Grupo | O Render lê o repositório. Se for privado, autorizar o Render. |
| Conta no Render | Grupo | Gratuita. |
| Conta no Supabase | Grupo | Criar um projeto e guardar a senha do banco. |

Nada disso foi criado por mim: criar contas e publicar são ações do grupo.

## 3. Passo a passo

1. **Banco:** no Supabase, criar o projeto e anotar a senha do banco. Em *Connect*, copiar a string do **Session pooler (porta 5432)**, no formato `postgresql://postgres.SEUPROJETO:SENHA@aws-0-REGIAO.pooler.supabase.com:5432/postgres`.
   - Não usar o *Transaction pooler* (porta 6543): ele quebra as consultas preparadas do `psycopg`.
   - Não usar a conexão direta: o Render gratuito só tem IPv4 e a conexão direta do Supabase costuma ser só IPv6.
   - Se a senha tiver `@`, `#` ou `/`, gerar outra só com letras e números (ou codificar na URL: `%40`, `%23`, `%2F`).
   - Se der erro de SSL, acrescentar `?sslmode=require` no fim da URL.
2. **Subir o código** para o GitHub (branch `main`).
3. **Render:** *New → Blueprint* e apontar para o repositório. O `render.yaml` cria o serviço `agulhas-protege`.
4. **Variáveis de ambiente** (painel do Render):
   - `DATABASE_URL`: string do Session pooler do passo 1 (o sistema aceita `postgresql://` e `postgres://`).
   - `PUBLIC_URL`: URL pública final, por exemplo `https://agulhas-protege.onrender.com`.
   - `CORS_ORIGINS`: `["https://agulhas-protege.onrender.com"]` (ajustar para a URL real).
   - `JWT_SECRET_KEY` é gerada pelo Render. `COOKIE_SECURE=true` já vem no blueprint.
5. **Deploy:** aguardar o build (cerca de 5 a 8 minutos na primeira vez). O log deve mostrar a migração, "Usuários e estação ... configurados" e o servidor ouvindo.
6. **Manter acordado:** o plano gratuito do Render dorme após 15 minutos sem acesso. Criar um monitor gratuito (UptimeRobot) em `https://SUA-URL/health` a cada 5 minutos. Isso evita a espera de cerca de 30 segundos na avaliação e mantém a coleta rodando.
7. **Primeira coleta:** acontece ao iniciar. Se quiser conferir, entre como administrador em `/admin` e clique em "Coletar dados agora".

## 4. Verificação antes do envio

Executar contra a URL publicada, com o navegador em janela anônima:

- [ ] `https://SUA-URL/health` retorna `{"status":"ok"}`.
- [ ] A página inicial mostra o nível atual, a foto da câmera e o gráfico.
- [ ] Login com `testeadmin@teste.com` e com `testecomum@teste.com` funciona; recarregar a página (F5) mantém a sessão.
- [ ] `/admin` aparece só para o administrador; o painel "Coleta de Dados Reais" mostra "Última coleta" recente.
- [ ] Registrar, atender, encerrar e excluir uma ocorrência.
- [ ] Alterar as cotas e restaurar as originais (2,00 / 2,50 / 3,20).
- [ ] Os 21 passos de `docs/ROTEIRO_DE_TESTES.md` passam. Corrigir o texto do roteiro se algo diferir.
- [ ] Testar também no celular, pois o layout é responsivo.

## 5. Conteúdo do envio no Moodle

- **Nome do sistema:** Agulhas Protege.
- **Integrantes:** _(nomes de todos)_.
- **Plataforma entregue:** Web, com o link direto da seção 3.
- **Contas de teste:** as duas contas do roteiro.
- **Roteiro de testes e funcionalidades incompletas:** conteúdo de `docs/ROTEIRO_DE_TESTES.md`.

## 6. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Servidor dormindo na hora da avaliação | Monitor em `/health` a cada 5 minutos (passo 6). |
| Uma fonte externa fora do ar | A coleta é independente por fonte: o sistema continua mostrando os últimos dados gravados e o painel indica a hora da última coleta. |
| Projeto gratuito do Supabase pausado por inatividade (cerca de 1 semana sem uso) | A coleta de 10 em 10 minutos mantém o banco ativo, desde que o monitor em `/health` mantenha o Render acordado. Se pausar, restaurar no painel do Supabase. |
| Falha de conexão com o Supabase | Conferir a porta (5432, Session pooler), o usuário com ponto (`postgres.SEUPROJETO`) e a senha. Ver o log do Render. |
| Senhas de teste públicas | São contas de avaliação. Depois da nota, trocar as senhas ou apagar o serviço. |
| Nível do rio sem variação durante a avaliação | O roteiro valida o fluxo (leitura, classificação, alteração de cotas) mesmo com o rio estável. O ajuste de cotas altera a classificação na hora. |

## 7. Depois da entrega

Manter o serviço e o banco ativos até o fim da avaliação. Para encerrar: apagar o serviço no Render e o projeto no Supabase.
