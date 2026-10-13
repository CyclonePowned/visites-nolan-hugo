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

## TP02

### Le secret trouvé dans l'historique

Le zip du modèle n'avait pas d'historique Git, donc le faux jeton prévu par le formateur n'était pas dans notre dépôt. On l'a recréé nous-mêmes avant de protéger main, pour pouvoir faire l'étape 5 : un commit qui ajoute une fausse clé d'API dans app/old_settings.py, puis un commit qui retire le fichier.

En lançant gitleaks sur tout l'historique, il trouve une fuite dans le commit 15cdab0 « chore: paramètres temporaires », fait par Nolan Sauzet le 13 octobre 2026 à 8 h 42. Le fichier est app/old_settings.py, ligne 3, avec la règle generic-api-key. Le fichier avait déjà été supprimé au commit suivant (25fab4e), mais la clé reste lisible dans l'historique avec git show.

On a décidé de ne pas réécrire l'historique. Le dépôt est public, donc il faut considérer que la clé a déjà été récupérée, et réécrire l'historique n'y change rien. En plus ça change tous les SHA et oblige tout le monde à recloner. Ce qui compte, c'est la rotation : si c'était une vraie clé, on l'aurait révoquée tout de suite chez le fournisseur de l'API et on en aurait créé une nouvelle, rangée dans une variable d'environnement et pas dans le code. On a mis l'empreinte de cette fuite dans .gitleaksignore pour que le rapport soit propre, et gitleaks sur l'historique renvoie maintenant le code 0.

### Q1. Les règles qui auraient empêché le secret d'arriver sur main

La PR obligatoire avec revue aurait pu le bloquer, si le relecteur avait vu la clé. C'est une règle humaine, donc on peut passer à côté. Le hook gitleaks en pre-commit l'aurait refusé avant même le commit, et un contrôle requis qui lance gitleaks sur la PR l'aurait bloqué côté GitHub. Ces deux-là sont automatiques. Le plus fiable, c'est le contrôle requis, parce qu'il tourne sur le serveur et que personne ne peut le sauter.

### Q2. Est-ce que pre-commit protège un collègue qui ne l'a pas installé

Non. Pre-commit tourne seulement sur la machine de celui qui l'a installé, et on peut même le sauter avec --no-verify. Pour que la règle soit vraiment appliquée, il faut lancer gitleaks dans le pipeline (GitHub Actions) sur chaque PR et le mettre en contrôle requis dans le ruleset.

### Q3. Combien de temps un secret reste privé sur une forge publique

Quasiment pas du tout. Des robots lisent en continu tout ce qui est poussé sur les dépôts publics et récupèrent une clé en quelques minutes, parfois en quelques secondes. GitHub Secret Scanning reconnaît les jetons de beaucoup de fournisseurs. Les jetons GitHub sont révoqués automatiquement, et pour les partenaires comme AWS, Google Cloud, Azure, Slack ou Stripe, GitHub les prévient et ils peuvent révoquer la clé eux-mêmes.

### Réponses aux questions des étapes

Étape 1 : « dismiss stale approvals » annule l'approbation dès qu'un nouveau commit est poussé sur la PR. Sans ça, quelqu'un pourrait faire approuver une PR propre, puis ajouter autre chose juste avant de fusionner, sans que personne ne relise. On a testé : le push direct sur main est refusé avec GH013, et une PR avec un commit non signé reste bloquée.

Étape 2 : si le seul propriétaire d'un dossier est absent, plus aucune PR qui touche ce dossier ne peut être fusionnée. Il faut toujours au moins deux propriétaires par dossier, ou une équipe, et prévoir qui peut contourner la règle en cas d'urgence. On a testé avec une PR de Hugo qui modifiait .github/CODEOWNERS : GitHub a demandé tout seul la revue de Nolan.

Étape 3 : une PR Dependabot doit être approuvée par l'un de nous, comme les autres. C'est une bonne chose parce que le robot modifie des dépendances qui vont tourner chez nous. Quelqu'un doit vérifier ce qui change, surtout si une dépendance a été compromise. Juste après la fusion de dependabot.yml, Dependabot a ouvert cinq PR pour mettre à jour des paquets pip (httpx, pre-commit, prometheus-client, pytest-cov et uvicorn). Il n'y a pas eu de PR pour fastapi, parce que Dependabot s'arrête à 5 PR ouvertes par défaut, alors on a monté la limite à 10.

Étape 4 : avec AWS_SECRET_ACCESS_KEY et une valeur de 40 caractères, le commit est refusé (règle generic-api-key, entropie 4,87, app/config.py). Avec la même valeur dans une variable appelée MA_VARIABLE, le commit passe. gitleaks se sert donc du nom de la variable en plus de la valeur : il faut un mot comme key ou secret et une valeur assez aléatoire.

## TP03

### Le pipeline

Le fichier .github/workflows/ci.yml se lance sur chaque PR et sur main après une fusion. Il installe le projet, lance ruff, pre-commit, pytest avec la couverture, et publie le rapport de couverture en artefact. Il tourne en même temps sur Python 3.12 et 3.13. Le prof nous a dit de ne jamais mettre latest, donc on a mis ubuntu-24.04 au lieu de ubuntu-latest, et pareil pour act avec l'image catthehacker/ubuntu:act-24.04.

Les deux checks requis dans le ruleset s'appellent test (py3.12) et test (py3.13).

### Q1. Durée du pipeline et ce qui prend le plus de temps

Au tout début, avec juste ruff et pytest, le job durait 26 s. Avec pre-commit et la couverture on est passé à environ 1 min 10. Ce qui prend le plus de temps c'est pre-commit, entre 27 et 36 s, parce qu'il réinstalle ses hooks à chaque fois (surtout gitleaks qui est en Go). Ensuite c'est pytest avec environ 9 s, puis l'installation des dépendances.

Pour le cache, au premier passage pip install prenait 10 à 11 s et le job entre 61 et 69 s. Aux passages suivants, avec « Cache restored » dans le journal, pip install prenait 5 à 7 s et le job entre 45 et 60 s. Le cache fait donc gagner 4 ou 5 s sur l'installation, mais ça change peu le total parce que la partie lente c'est pre-commit et le cache pip ne le couvre pas. Le pipeline reste de toute façon bien en dessous des 5 minutes.

### Q2. Ce qui empêche de contourner le pipeline

C'est le ruleset. La PR est obligatoire, les deux checks doivent être verts et personne n'a le droit de bypass. Sans ça le pipeline donnerait juste un avis, une PR rouge pourrait quand même être fusionnée. On a aussi lié les checks à GitHub Actions dans le ruleset, comme ça un autre outil ne peut pas envoyer un faux check vert avec le même nom.

### Q3. Ce qu'il faudrait changer pour GitLab CI ou Gitea Actions

Pour Gitea Actions presque rien, c'est la même syntaxe, il faut juste mettre le fichier dans .gitea/workflows. Pour GitLab CI il faut réécrire tout le fichier dans un .gitlab-ci.yml avec une autre syntaxe (stages, image, script), et il n'y a pas d'actions comme checkout ou setup-python, on passe par une image Docker Python. Par contre les idées restent les mêmes : un job par version de Python, un cache, un artefact et un contrôle obligatoire avant la fusion.

### Réponses aux questions des étapes

Étape 1 : le workflow s'est lancé sur la PR alors que main n'avait pas encore de ci.yml, parce que pour une PR GitHub lit le workflow dans le code de la PR, pas sur main. En fait il teste un commit de fusion temporaire entre la branche et main, on le voit dans le journal du checkout.

Étape 2 : la couverture est à 100 % sur les trois fichiers de app/, donc il n'y a pas vraiment de fichier moins couvert que les autres. Pour nous un seuil vers 80 % serait bien pour voir si la couverture baisse. Mais pas 100 %, sinon on finit par écrire des tests juste pour le chiffre, et une ligne exécutée par un test ne veut pas dire qu'elle est vraiment vérifiée.

Étape 3 : avec la matrice il y a deux checks sur la PR, un par version de Python, et il faut exiger les deux. La clé du cache est calculée à partir de pyproject.toml, on a dû mettre cache-dependency-path parce que par défaut setup-python cherche un requirements.txt qu'on n'a pas. On a aussi renommé l'artefact en coverage-3.12 et coverage-3.13, sinon les deux jobs publient le même nom.

Étape 4 : on a cassé le test de X-Visites-Version en ajoutant « -dev » à la version dans la PR #30. Les deux checks sont passés en rouge avec AssertionError: assert '0.1.0-dev' == '0.1.0' et la fusion était bloquée avec « Required statuses must pass ». Après le commit correctif, tout est repassé au vert. Petite chose en plus : la première fois j'avais mis la version en dur, et le commit a été refusé par pre-commit parce que ruff a vu que l'import de __version__ ne servait plus. Pour le bypass, un admin qui coche bypass peut fusionner même avec des checks rouges. Il faudrait que très peu de personnes aient ce droit et seulement pour une urgence. GitHub garde une trace de chaque bypass dans la PR et dans les Insights du ruleset.

Étape 5 : on a installé act 0.2.89. Avec act pull_request -j test --matrix python:3.13, toutes les étapes passent sauf upload-artifact, qui échoue avec « Unable to get the ACTIONS_RUNTIME_TOKEN env variable ». En local il n'y a pas les serveurs de GitHub, donc pas de stockage pour les artefacts, et le cache pip n'est pas restauré non plus (« pip cache is not found »). act ne remplace pas GitHub Actions pour valider une PR, parce que le ruleset ne regarde que les checks faits sur GitHub. Par contre il est pratique pour tester un workflow sans faire plein de commits, et ça sera sûrement utile au TP07 quand le dépôt passera en privé, parce que les minutes de GitHub Actions seront limitées.
