# 04: Inscrição de equipes em torneios

**What to build:** Um usuário consegue montar a lista de participantes de um torneio em rascunho, reutilizando equipes existentes ou criando uma equipe diretamente durante a inscrição.

**Blocked by:** 02 Cadastro completo de equipes; 03 Administração de torneios

**Status:** done

- [x] Cada equipe pode participar de vários torneios.
- [x] Uma equipe aparece uma única vez dentro do mesmo torneio.
- [x] A tela lista equipes disponíveis separadas das já inscritas.
- [x] É possível criar uma equipe nova e inscrevê-la imediatamente.
- [x] Inscrições podem ser removidas antes do início.
- [x] Adição e remoção são bloqueadas após o início.
- [x] Tentativas de duplicação são recusadas com mensagem clara.
- [x] As regras de inscrição são testadas independentemente de Flask e HTTP.


## Comments

O fluxo foi validado na aba Equipes e em testes dos casos de uso com repositórios em memória. A suíte completa passou com 102 testes.
