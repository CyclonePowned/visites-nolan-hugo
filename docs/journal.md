# Journal

## TP01

### Q1. Temps entre le premier commit et sa fusion sur main

Premier commit (`feat(api): exposer la version dans X-Visites-Version`) : 12/10/2026 à 11 h 31.
Fusion sur main (PR #1, squash) : 12/10/2026 à 13 h 36.
Délai de changement : environ 2 h 05. L'essentiel est de l'attente : revue par l'autre membre, demande de changement, puis rebase à cause d'un conflit avec la PR #4 fusionnée entre-temps.

### Q2. Ce qui ne dépend pas de GitHub

Fonctionne tel quel sur GitLab, Gitea ou Forgejo :

- tout Git : branches, commits conventionnels, rebase, résolution de conflit, `--force-with-lease`, tags ;
- la signature SSH des commits et des tags, et sa vérification locale (`allowed_signers`) ;
- pre-commit et ruff, qui tournent sur le poste ;
- l'application, les tests pytest, Redis dans Docker.

Ce qui changerait :

- les commandes `gh` (création du dépôt, PR, revue, fusion) : `glab` sur GitLab, `tea` sur Gitea/Forgejo, ou l'interface web ;
- le vocabulaire : « merge request » sur GitLab au lieu de « pull request » ;
- les réglages de la forge : modèle de dépôt, collaborateurs, protection de branche, ajout des clés SSH.

### Q3. Pourquoi signer les commits si la forge vérifie déjà qui pousse

La forge vérifie seulement qui pousse, pas qui a écrit chaque commit. N'importe qui peut mettre le nom et l'e-mail d'un autre dans `user.name` / `user.email`. Si quelqu'un pousse un clone contenant des commits d'autres personnes, la forge ne voit que le pousseur. Et si le dépôt est migré vers une autre forge, l'information « qui a poussé » est perdue. La signature est dans le commit lui-même : elle prouve l'auteur partout, sur n'importe quelle forge et même hors ligne.

### Ce qui nous a pris le plus de temps

- **Installer Git 2.56** : la distribution ne fournit qu'une version plus ancienne, sans `git add --resolved`. Il a fallu le compiler depuis les sources, et la compilation a d'abord échoué faute de Rust.
- **La signature des commits** : la clé SSH n'était ajoutée sur GitHub qu'en authentification, pas en signature. Le premier commit de B est donc apparu « non vérifié » (`unknown_key`) jusqu'à l'ajout de la clé en type *Signing Key*.
- **pre-commit avant sa fusion** : une fois le hook installé, les commits sur les autres branches échouaient avec « No .pre-commit-config.yaml » tant que la PR pre-commit n'était pas sur main.
- **Un conflit non prévu** : les PR #1 et #4 ajoutaient chacune un test à la fin de `tests/test_api.py`. La #1 a dû être rebasée après la fusion de la #4.
- **L'attente entre nous** : la plus grande partie du délai vient des allers-retours de revue (demande de changement, correction, approbation) et de la coordination pour que le conflit volontaire de l'étape 5 se produise dans le bon ordre.

## Réponses aux questions des étapes

- **Étape 1, `~/.ssh/allowed_signers` :** il associe une adresse e-mail à une clé publique SSH de confiance. `git log --show-signature` l'utilise pour dire si la signature est bonne et à qui elle appartient. Sans lui, Git ne peut pas relier la signature à une personne.
- **Étape 2, modèle ou fork :** un dépôt créé depuis un modèle repart d'un historique neuf, sans lien avec l'original. Un fork garde tout l'historique et reste lié au dépôt d'origine pour lui proposer des PR.
- **Étape 4, la branche locale après le squash :** elle reste sur le poste avec ses commits d'origine. Le squash a créé sur main un commit nouveau, avec une autre empreinte, donc Git ne voit pas la branche comme fusionnée et `git branch -d` refuse de la supprimer. Il faut `git branch -D`.
- **Étape 5, `--force-with-lease` :** il ne force le push que si la branche distante est encore dans l'état que l'on connaît. Si quelqu'un a poussé entre-temps, il refuse au lieu d'écraser son travail. `--force` écrase sans vérifier.
- **Étape 6, fichier mal formaté :** le hook pre-commit bloque le commit. ruff-format reformate le fichier ; il faut refaire `git add` puis recommiter. `git commit --no-verify` saute les hooks : le commit passe sans contrôle, d'où l'intérêt de relancer les contrôles en CI.
