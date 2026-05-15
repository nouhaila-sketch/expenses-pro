[![CI/CD](https://github.com/nouhaila-sketch/expenses-pro/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/nouhaila-sketch/expenses-pro/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10-blue)
![Docker](https://img.shields.io/badge/docker-available-2496ED)
![Kubernetes](https://img.shields.io/badge/kubernetes-326CE5?&style=plastic&logo=kubernetes&logoColor=white)

# expenses-pro

Application de suivi de depenses construite avec Flask.

## Description

Expenses-pro permet d'ajouter, lister, supprimer et exporter des depenses.
Elle inclut un tableau de bord avec un graphique par categorie et un systeme
d'authentification simple.

## Architecture

```
app.py         → points d'entree et routes Flask
templates/     → pages HTML (Jinja2)
tests/         → tests pytest
k8s/           → fichiers Kubernetes
```

Routes principales :

| Route | Methode | Description |
|-------|---------|-------------|
| `/` | GET | Tableau de bord (authentification requise) |
| `/add` | GET/POST | Ajouter une depense |
| `/list` | GET | Liste des depenses |
| `/delete/<id>` | GET | Supprimer une depense |
| `/login` | GET/POST | Connexion |
| `/register` | GET/POST | Inscription |
| `/logout` | GET | Deconnexion |
| `/export` | GET | Export CSV |

## Dependances

- Flask
- pytest
- ruff
- black

Les dependances sont listees dans `requirements.txt`.

```bash
pip install -r requirements.txt
```

## Execution

```bash
pip install -r requirements.txt
python app.py
```

L'application est accessible sur `http://localhost:5000`.

## Tests

```bash
python -m pytest -v
```

## CI / CD

La pipeline GitHub Actions s'execute sur chaque `push` et `pull request` :

1. **Lint** — `ruff check .`
2. **Format** — `black --check .`
3. **Tests** — `python -m pytest -v`
4. **Docker** — construction et publication sur GHCR (uniquement sur push)

En cas d'echec d'une de ces etapes, le pipeline echoue.

## Docker

Construction de l'image :

```bash
docker build -t expenses-pro .
```

Execution du conteneur :

```bash
docker run -p 5000:5000 expenses-pro
```

L'image est automatiquement publiee sur GHCR par la CI lors d'un push
ou d'un tag (`v*`).

## Structure du projet

```
expenses-pro/
├── .github/workflows/ci.yml
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── add.html
│   ├── list.html
│   ├── login.html
│   ├── register.html
│   └── index.html
├── tests/
│   ├── conftest.py
│   └── test_app.py
└── k8s/
    ├── deployment.yaml
    └── service.yaml
```
