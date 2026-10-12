# Contribuer au projet

## Flux de travail (GitHub Flow)
1. Créer une branche courte depuis `main` à jour.
2. Développer la fonctionnalité et faire des commits.
3. Ouvrir une Pull Request (PR).
4. Faire relire le code par l'autre membre du binôme (revue croisée avec demande de changement si nécessaire).
5. Mettre à jour avec `git rebase` et `git push --force-with-lease` si besoin.
6. Fusionner par **squash** (un seul commit sur `main`).
7. Supprimer la branche distante et locale.

## Convention de commits
Nous utilisons les **Conventional Commits**. Tous les commits doivent être **signés**.
Exemples de types : `feat`, `fix`, `docs`, `test`, `chore`, `style`.

## Commandes utiles
- Installer les dépendances : `pip install -e ".[dev]"`
- Lancer les tests : `pytest -q`
- Installer pre-commit : `pre-commit install`
- Lancer pre-commit manuellement : `pre-commit run --all-files`
