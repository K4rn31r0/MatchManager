# 01: Fundação persistente do MatchManager

**What to build:** Um usuário consegue abrir o aplicativo, criar um torneio em rascunho e vê-lo numa primeira listagem persistida em um arquivo JSON local. Esta fatia vertical também estabelece a separação entre regras de torneio, casos de uso, interface Flask/Jinja2 e persistência.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] As dependências da aplicação Flask são declaradas e o servidor pode ser iniciado.
- [ ] Um torneio em rascunho pode ser criado com nome único e dados gerais válidos.
- [ ] O nome do torneio é único sem diferenciar maiúsculas, minúsculas ou acentos.
- [ ] A lista inicial mostra os torneios já persistidos.
- [ ] Os dados são gravados e recuperados apenas por meio de um arquivo JSON local.
- [ ] A criação e as regras de nome são testadas independentemente de Flask e HTTP.

