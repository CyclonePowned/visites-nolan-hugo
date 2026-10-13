[![CI](https://github.com/CyclonePowned/visites-nolan-hugo/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/CyclonePowned/visites-nolan-hugo/actions/workflows/ci.yml)

# Visites : API de comptage des visites

API FastAPI qui compte les visites dans Redis.

## Démarrer

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
docker run -d --name redis -p 6379:6379 redis:8-alpine
pytest -q
uvicorn app.main:app --reload
```

## Endpoints

| Méthode | Chemin     | Rôle                                                        |
|---------|------------|-------------------------------------------------------------|
| GET     | `/`        | incrémente et renvoie le compteur, en-tête `X-Visites-Version` |
| POST    | `/reset`   | remet le compteur à zéro et renvoie `{"visites": 0}`        |
| GET     | `/health`  | état de l'API et de Redis (503 si Redis est absent)         |
| GET     | `/metrics` | métriques Prometheus                                        |

## Contrôles avant commit

```bash
pre-commit install
pre-commit run --all-files
```

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md).
