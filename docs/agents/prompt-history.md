# Histórico de prompts

Registro sequencial das ações significativas realizadas com apoio de IA, com o prompt que originou cada uma.

## 001 — Implementação da issue 01: Fundação persistente

**Data:** 2026-11-23
**Ferramenta:** Claude Code (Claude Opus 5.5)
**Branch:** `issue-01-fundacao-persistente`

**Prompt:**

> agr, seguindo o padrao do enunciado e o que foi especificado nos mds do repo, precisaria implementar issue 01 e 02. Vamos fazer com calma, uma por uma em branches separadas

**Decisões confirmadas com o usuário antes da implementação:** nome e formato obrigatórios; modalidade e datas opcionais; data de término anterior à de início é recusada; seams de teste em `CreateTournament`, `ListTournaments` (com repositório fake em memória) e `JsonTournamentRepository` (com arquivo temporário).

**O que foi feito:** Implementada a primeira fatia vertical seguindo Clean Architecture e TDD (red → green por seam). No core foram criados a entidade imutável `Tournament` (com `TournamentFormat`, `TournamentStatus` e invariantes de nome e datas), a regra de domínio `normalize_name` (compara nomes ignorando maiúsculas, acentos e espaços externos), a interface `TournamentRepository`, os erros de domínio e os casos de uso `CreateTournament` e `ListTournaments`, que recebem dependências por injeção (repositório, gerador de ids e relógio). Na infraestrutura, `JsonFileStorage` grava um único arquivo JSON de forma atômica e `JsonTournamentRepository` implementa o contrato do core. Na camada de adaptadores, o controller Flask converte o formulário em entrada do caso de uso e traduz erros em mensagens em português, e o presenter formata rótulos e datas. `server/app.py` é a raiz de composição. Foram adicionados `requirements.txt`, configuração do pytest, templates Jinja2 e CSS próprio mínimo. Resultado: 20 testes passando e código conforme PEP-8 (`pycodestyle`).
