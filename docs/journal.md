# Journal

## TP01

### Q1. Temps entre le premier commit et sa fusion sur main

Mon premier commit (l'en-tête X-Visites-Version) date de 11 h 31 et il a été fusionné sur main à 13 h 36, donc environ 2 h. La plupart du temps c'était de l'attente : la revue de Hugo, la correction demandée, puis un rebase parce que sa PR /reset avait été fusionnée avant et touchait le même fichier de tests.

### Q2. Ce qui ne dépend pas de GitHub

Tout ce qui est Git marche pareil sur GitLab, Gitea ou Forgejo : les branches, les commits, le rebase, le conflit, le force-with-lease, les tags et la signature SSH. Pre-commit, ruff, les tests et Redis dans Docker tournent sur notre machine, donc ça ne change rien non plus. Ce qui changerait, ce sont les commandes gh (il faudrait glab ou tea, ou passer par le site), le nom des PR (merge request sur GitLab) et les réglages du dépôt comme les collaborateurs ou les clés SSH.

### Q3. Pourquoi signer les commits si la forge vérifie déjà qui pousse

La forge sait qui a poussé, mais pas qui a écrit chaque commit. N'importe qui peut mettre le nom et l'e-mail de quelqu'un d'autre dans sa config Git. Si quelqu'un pousse un clone avec les commits des autres, ou si on change de forge, on perd cette info. La signature reste dans le commit, donc on peut toujours vérifier l'auteur, peu importe où est le dépôt.

### Ce qui nous a pris le plus de temps

Installer Git 2.56, parce que Debian a une version plus ancienne et qu'il a fallu le compiler. Ensuite la signature : la clé de Hugo n'était pas ajoutée en clé de signature sur GitHub, donc son premier commit apparaissait non vérifié. On a aussi eu un conflit qu'on n'avait pas prévu entre nos deux PR sur le fichier de tests. Et pas mal d'attente entre nous pour les revues et pour faire le conflit de l'étape 5 dans le bon ordre.

### Réponses aux questions des étapes

Étape 1 : le fichier allowed_signers associe une adresse e-mail à une clé publique. git log --show-signature s'en sert pour savoir à qui appartient la signature.

Étape 2 : un dépôt créé depuis un modèle repart de zéro, sans l'historique ni de lien avec l'original. Un fork garde tout l'historique et reste lié au dépôt d'origine.

Étape 4 : après le squash, la branche locale existe toujours. Le commit sur main est un nouveau commit, donc Git pense que la branche n'est pas fusionnée et git branch -d refuse. Il faut utiliser -D.

Étape 5 : c'est Hugo qui a résolu le conflit sur le titre du README, avec un rebase sur main puis git add --resolved. --force-with-lease vérifie que personne n'a poussé sur la branche entre temps avant d'écraser, alors que --force écrase sans regarder.

Étape 6 : si un fichier Python est mal formaté, pre-commit bloque le commit et ruff corrige le fichier, il faut refaire git add puis commit. Avec --no-verify les hooks sont ignorés et le commit passe quand même.
