# Roteiro de Testes — Agulhas Protege

**Sistema:** Agulhas Protege — monitoramento e alerta de cheias do Rio Sesmaria (Resende-RJ).
**Link:** _(preencher com a URL publicada)_

## Contas de teste

| Perfil | Login | Senha |
|---|---|---|
| Administrador | testeadmin@teste.com | Teste@2029 |
| Usuário comum (operador da Defesa Civil) | testecomum@teste.com | Teste@2029 |

## Como o sistema obtém os dados

O servidor coleta, por conta própria e a cada 10 minutos, o nível real do Rio Sesmaria (CEMADEN), chuva observada e prevista (Open-Meteo) e a vazão da Represa do Funil (ONS). Os números da tela podem ser conferidos nas fontes oficiais.
Na primeira visita após um período sem uso o servidor pode levar cerca de 30 segundos para acordar (hospedagem gratuita).

## Plano de testes

| # | Ação no sistema | Resultado esperado |
|---|---|---|
| 1 | Abrir o link sem fazer login. | A página inicial mostra o cartão "Estação CEMADEN Rio Sesmarias" com o nível em metros, a etiqueta de risco (Normal, Atenção, Alerta ou Emergência) e o horário da leitura. |
| 2 | Na página inicial, ver o painel "Dados da Estação em Tempo Real". | Aparecem a foto da câmera da estação (com data e hora), a chuva na última hora e em 24h e a lista de fontes com o horário da última coleta. |
| 3 | No gráfico histórico, alternar entre 24h, 7d e 30d. | O gráfico muda de período sem erro. As linhas de cota (Atenção, Alerta, Emergência) aparecem. O período 30d mostra apenas o que já foi coletado desde a publicação. |
| 4 | Clicar no botão de atualizar (ícone de setas) no topo e depois no ícone de lua. | Os dados são recarregados e o tema alterna entre claro e escuro, sem perder a tela. |
| 5 | Clicar em "Defesa Civil" e tentar entrar com senha errada (testecomum@teste.com / Errada@1). | Mensagem de erro "Email ou senha inválidos", sem entrar no sistema. |
| 6 | Entrar como usuário comum (testecomum@teste.com / Teste@2029). | Redireciona para `/dashboard` mostrando o selo do perfil, o cartão da estação, o botão "Registrar Ocorrência" e a lista de ocorrências. |
| 7 | Como usuário comum, abrir o endereço `/admin` manualmente. | O sistema bloqueia o acesso e volta para a página inicial, pois essa área é só do administrador. |
| 8 | Como usuário comum, clicar em "Registrar Ocorrência", preencher localização "Rua das Palmeiras, 45 - Resende" e descrição "Água subindo na calçada, moradores avisados." e salvar. | Aparece mensagem de confirmação e a ocorrência surge na lista com status "Aberta" e o nome do agente. |
| 9 | Tentar salvar uma ocorrência com localização de 2 letras. | O formulário recusa e informa que a localização precisa de no mínimo 5 caracteres. |
| 10 | Na ocorrência criada, clicar em "Iniciar Atendimento" e depois em "Encerrar". | O status muda para "Em Atendimento" e depois para "Encerrada", com mensagem de confirmação a cada mudança. Os filtros (Abertas, Em Andamento, Encerradas) refletem a mudança. |
| 11 | Recarregar a página (F5) estando em `/dashboard`. | A sessão é mantida: continua no dashboard, sem voltar para o login. |
| 12 | No dashboard, rolar até a previsão. | Aparecem três cartões (+24h, +48h, +72h) com nível estimado, chuva prevista, probabilidade de alerta, classificação de risco e confiabilidade. |
| 13 | Rolar até "Análise de Correlação Hidrológica". | Aparecem chuva defasada de São José do Barreiro, chuva acumulada, vazão do Funil com valores em m³/s e a matriz de correlação com coeficiente r e relevância calculados. |
| 14 | No painel do Funil, usar o botão de alerta por WhatsApp. | Abre o link `wa.me` com a mensagem pronta, contendo nível atual, previsão +24h, vazão do Funil e a ação recomendada. |
| 15 | Clicar no ícone de lixeira de uma ocorrência e confirmar. | A ocorrência some da lista e aparece mensagem informando que a exclusão ficou registrada na auditoria. |
| 16 | Sair, entrar como administrador (testeadmin@teste.com / Teste@2029). | Redireciona para `/admin`, "Gerenciar Estações e Cotas de Risco". |
| 17 | No `/admin`, clicar em "Ajustar Cotas", informar Atenção 1,00, Alerta 1,50, Emergência 2,00 e salvar. | Mensagem de sucesso. Na página inicial o cartão passa a mostrar o nível como "Atenção" (o nível real está acima de 1,00 m) e o gráfico redesenha as linhas de cota. |
| 18 | Tentar salvar cotas fora de ordem (Atenção 3,00, Alerta 2,00, Emergência 1,00). | O sistema recusa e informa que as cotas precisam estar em ordem crescente. |
| 19 | Restaurar as cotas originais (2,00 / 2,50 / 3,20). | O cartão volta à classificação anterior. |
| 20 | No `/admin`, em "Coleta de Dados Reais", conferir o status e clicar em "Coletar dados agora". | Mostra a última coleta, a última leitura do rio e o total de leituras. Após clicar, aparece "Coleta concluída" com o número de leituras novas (pode ser 0 se o CEMADEN ainda não publicou uma hora nova). |
| 21 | Abrir `/api/docs` e `/api/v1/coleta/status`. | A documentação da API abre e o endpoint público devolve a situação da coleta em JSON. |

## Funcionalidades incompletas ou indisponíveis

- **Previsão:** é um modelo hidrológico simplificado calculado sobre dados reais, e não um modelo oficial. A probabilidade vem de cenários de chuva (0,5x a 2x), e a confiabilidade é uma estimativa por horizonte.
- **Recomendação para o Funil:** é heurística de apoio à decisão. A vazão vem do ONS em base diária (um valor por dia, com atraso de 1 a 2 dias).
- **Histórico de 7d e 30d:** o CEMADEN só fornece cerca de 4 dias de série na consulta pública. O restante é acumulado a partir da publicação do sistema.
- **Foto da câmera:** vem do CEMADEN e é atualizada uma vez por hora. Se o CEMADEN estiver fora do ar, a última coleta bem-sucedida continua sendo exibida.
- **Cadastro de usuários:** não existe tela para criar novos usuários. As contas de teste são criadas automaticamente no início do servidor.
- **Notificações push/e-mail:** não implementadas. O alerta é feito pela mensagem de WhatsApp.
