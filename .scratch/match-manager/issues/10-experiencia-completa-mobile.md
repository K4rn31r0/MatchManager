# 10: Experiência completa mobile

**What to build:** O usuário consegue navegar e realizar as tarefas principais em celular ou desktop por uma interface simples, bonita e responsiva, com filtros, abas, estados vazios e mensagens claras.

**Blocked by:** 09 Ciclo, correções e encerramento

**Status:** done

- [x] A página inicial, equipes e torneios seguem uma navegação consistente.
- [x] Cada torneio apresenta abas de partidas, classificação e equipes.
- [x] As partidas podem ser filtradas por rodada ou fase e por status.
- [x] Datas e locais opcionais podem ser informados sem bloquear o resultado.
- [x] Formulários usam validação compreensível e mensagens em português.
- [x] Estados vazios, confirmações e erros são visíveis em telas pequenas.
- [x] A interface usa HTML renderizado no servidor, Jinja2 e CSS próprio mobile-first.
- [x] Nenhuma interação principal depende de framework JavaScript ou biblioteca de interface.
- [x] Fluxos principais podem ser concluídos no celular e no desktop.

## Comments

A página do torneio foi reorganizada em abas (Partidas, Classificação — apenas em pontos corridos após o início —, Equipes e Configuração/Regras). As abas não usam JavaScript: todas as seções são renderizadas no servidor e alternadas por âncoras com `:target`; com suporte a `:has()` apenas uma aba aparece por vez, e sem ele as seções ficam empilhadas. A aba padrão é Equipes no rascunho e Partidas após o início; os redirecionamentos levam à aba da ação. O novo caso de uso `ListTournamentMatches` filtra partidas por rodada/fase e status para os dois formatos, e `ScheduleMatch` grava data e local opcionais (após o início), independentes do resultado; ambos persistem no JSON. Um presenter de partidas formata equipes, placar ou vencedor, status e nomes de fase (Semifinal/Final). Formulários de resultado e de data/local ficam em `<details>`, reabrem com os valores digitados quando há erro, e o encerramento pede confirmação mostrando as partidas pendentes. A navegação principal marca a seção atual, há links de retorno, estados vazios e tabela de classificação com rolagem horizontal. A suíte completa passou (220 testes) e os fluxos de pontos corridos e mata-mata foram executados ponta a ponta no servidor real (`flask --app server.app run`), com capturas em 360 px e 1280 px de largura.

