# MatchManager
Organizador de competições e partidas esportivas.

## Como executar

Requer Python 3.11 ou superior.

```bash
pip install -r requirements.txt
flask --app server.app run
```

Acesse http://127.0.0.1:5000. Os dados ficam em `instance/matchmanager.json`,
criado automaticamente no primeiro cadastro.

## Testes

```bash
pytest
```
