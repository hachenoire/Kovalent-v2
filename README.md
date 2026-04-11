# Kovalent
![Affiche du projet](Affiche_Kovalent.png)\
<br>
**Projet 3 de NSI**\
A retrouver sur notre [github](https://github.com/kimivictor2009/Kovalent)\
Voir "présentation.md" pour plus d'informations sur le projet

## Pour lancer le projet
- Ouvrez le répertoire "code"
- Ouvrez le fichier "main.py" avec python
- Exécutez le code
> [!IMPORTANT]
> **Vous devez avoir installé certains modules, tel que pygame ou screeninfo : vous pouvez les installer avec "requirements.txt"**\
> Vous pouvez utiliser :
```shell
pip install -r requirements.txt
```

## Pour jouer
Une fois le programme lancé, vous trouverez les instructions dans le jeu. Elles précisent le but du jeu, comment jouer, la progression et quelques atomes. Vous en découvrirez plus en jouant !

## Répertoire
```
📂 Kovalent
│
├── 📂 sources
│   │
│   └── main.py              -> Programme principal du jeu (à exécuter)
│
├── 📂 data
│   │
│   ├── 📂 img
│   │   │
|   |   ├── 📂 buttons
│   │   │   │
│   │   │   ├── next.png     -> Image du bouton de passage au niveau suivant
│   │   │   └── restart.png  -> Image du bouton qui réinitialise le niveau
│   │   │
│   │   ├── icon.png         -> Icone du jeu
│   │   ├── lock.png         -> Image des niveaux bloqués
│   │   └── title.png        -> Image du titre
│   │
│   ├── 📂 sound
│   │   │
│   │   ├── btn-sfx.wav      -> Effet sonore
│   │   ├── doom_music.wav   -> Musique pour le niveau 50
│   │   ├── error-sfx.wav    -> Effet sonore (destruction d'un lien ou impossibilité d'en créer un)
│   │   ├── link-sfx.wav     -> Effet sonore (lien entre 2 atomes)
│   │   ├── music.wav        -> Musique principale du jeu
│   │   └── win-sfx.wav      -> Effet sonore (résolution du niveau)
│   │
│   ├── atome.json           -> Base de données des atomes du jeu
│   ├── niveau.json          -> Base de données des niveaux du jeu
│   └── progress.txt         -> Enregistrement du progrès dans le jeu
│
├── Affiche_Kovalent.png     -> Affiche du jeu
├── presentation.md          -> Documentation détaillée
├── requirements.txt         -> Dépendances
├── Cahier_de_projet.odt     -> Cahier de projet
├── license.txt              -> License
└── README.md                -> Vous êtes ici
```

## Contact
Vous pouvez nous contacter, poser des questions, vous renseigner, à l'adresse suivante : <kimivictor@proton.me>
