# Présentation globale du projet
Plus d'informations sur le projet sont contenues dans le cahier de projet (Cahier_de_projet.odt), comme l'affiche, les détails des modules avec les deadlines ou l'usage de l'IA.
## Naissance de l’idée
Nous voulions faire un jeu à la fois amusant, dificile et impliquant des parties courtes.
Après de nombreuses sessions de réflexion, d'appels et de brainstorms, l'idée est née de programmer pour ce projet un jeu de puzzle de chimie.

## Problématique initiale
Le jeu doit être éducatif et divertissant, et doit susciter la réflexion du joueur.
Le but est de former des molécules à partir d'atomes, en respectant le nombre de connections possibles par atome. Il y a 50 niveaux à résoudre pour finir le jeu.

## Objectifs
L'objectif est de produire un jeu éducatif et divertissant.

# Organisation du travail
## Présentation de l’équipe
### Victor Alaimo
J'ai déjà de l'expérience en programmation, j'ai codé sur Scratch au collège pour produire seul des jeux complexes et de qualité. Cette année, en NSI, j'ai pu appronfondir mes connaissances de python et de HTML/JS/CSS, et nous avons avec Kimi fait des projets que je trouve bien fait et complets (bien sûrs, il ne sont pas parfait, mais le résultat est plus qu'assez bien pour moi).\
Le premier projet a été en Pygame, et nous avons réalisé un jeu d'échecs, "PyChess". J'ai beaucoup aimé ce projet, mais il était trop ambitieux et, bien que nous l'ayons fini, il nous a pris beaucoup de temps à concevoir.\
Pour le deuxième projet, nous avions une personne de plus dans le groupe alors nous avons décidé de faire un Puissance 4 en site web, car c'est une envergure raisonnable pour un trio. Il a été compliqué d'avancer mais le résultat était satisfaisant.\
Nos projets peuvent être téléchargés sur cette page : https://www.github.com/kimivictor2009 \
Je suis motivé pour ce projet-ci, et j'espère que le rendu sera le meilleur possible et qu'on le finisse à temps.

### Kimi Vandaele-Otozaki
J'avais une maigre experience en programmation avant d'arriver en classe de NSI mais je présentais une facilité à programmer grâce à 2-3 projets réalisé sur scratch ou dans d'autres cadre définis. Cette année j'ai pu apprendre de nouveaux langages de programmation et approfondir ceux que je connaissais déja en cours de NSI. Avec Victor, nous avons réalisé deux projets au cours de cette année, Kovalent est donc notre troisième projet en commun. \
Nos projets peuvent être trouvés sur cette page : https://www.github.com/kimivictor2009 \
Je suis motivé pour ce projet puisqu'il mélange l'informatique et la science qui sont deux matières que j'affectionne particulièrement.\

### Noé Boissimon
Noé est un élève de première, dans un autre groupe de NSI que les autres. Il a peu d'expérience dans la programmation, si ce n'est quelques cours de technologie sur Scratch au collège et les cours de NSI de cette année. Grâce à son approche de débutant sur Python, Noé a offert un regard précieux sur l'accessibilité du jeu. Son investissement personnel lui a permis de s'initier aux mécaniques de Pygame tout en veillant à ce que le projet reste compréhensible pour tous les types d'utilisateurs. 

## Rôle de chacun et répartition des tâches
### Victor
Je suis responsable de l'organisation du projet, de la plupart des documents en dehors du code, et du rôle de chacun.
Chacun a (en théorie) un rôle de même ampleur dans le code. Ma partie était de faire les menus, l'affichage des atomes et la détection de la victoire. J'ai également réalisé de nombreuses modifications imprévues à l'origine, comme l'arrière-plan ou le bouton "quitter", par exemple.

### Kimi
Mon role dans ce projet est de créer les bases de données à importer dans le code python (ex: niveau...) mais aussi de coder certains modules comme celui qui crée les liaisons entre les atomes. Certains roles de débuggage m'ont aussi été attribué.

### Noé
Menu de sélection des niveaux ainsi que déplacement et sélection des atomes. + Vidéo\

## Temps passé sur le projet
Nous avons commencé le projet vers le 1er mars 2026 (plus tard que prévu car le projet 2 nous a occupé jusqu'au bout), nous laissant moins d'un mois pour le terminer. Le temps passé dessus par jour en moyenne est donc conséquent et le rythme est difficile à tenir.

# Présentation des étapes du projet
Nous avons scindé le projet en modules, et chacun était chargé de certains modules. Voici la liste des modules :
- Initialisation de la fenêtre
- Dictionnaire des molécules
- Menu principal
- Menu de sélection des niveaux
- Atomes
- Affichage de l’objectif et menu de jeu
- Déplacement et sélection des atomes
- Détection de la victoire
- Boutons du jeu
Pour plus d'informations, voir le cahier de projet.

# Validation de l’opérationnalité du projet/de son fonctionnement

## État d’avancement du projet au moment du dépôt
Projet terminé.

## Approches mises en œuvre pour vérifier l’absence de bugs
Tout le long de la création du projet, nous nous sommes assuré pas à pas que tout fonctionnait (ce qui arrivait rarement du premier coup). Nous avons utilisé certaines méthodes de débogage, allant de modifications à l'aveuglette à l'ajout de "print()" dans le code pour mieux le comprendre, en passant par une réflexion collective sur le bug. Mais il fallait également trouver les bugs à résoudre.\
Par exemple, quand Victor a créé la détection de victoire (fonction detect_win()), basée sur le nombre de liaisons des atomes qui doit être égal à leur maximum, on pensait que son fonctionnement était bon. Mais suite à des test directement en jouant au jeu, Kimi s'est aperçu que l'on pouvait sur certains niveaux former plusieurs molécules distinctes, mais gagner quand même !\
Au final, il a fallu regarder en plus si tous les atomes ne forment bien qu'une seule et même molécule grâce à un script basé sur un concept conplexe proposé par le professeur.

## Difficultés rencontrées et solutions apportées
Nous avons rencontré quelques difficultés au cours du projet, comme par exemple pour réaliser l'affichage de liaison doubles ou triples, résolue avec des calculs vectoriels. La détection de victoire mentionnée ci-dessus a également posé problème. Du côté des données (niveaux et atomes), nous voulions originellement les stocker dans un fichier csv, mais le format n'était pas adapté aux nombreuses informations que l'on voulait enregistrer, alors nous avons dû opter pour le Json, même si notre maîtrise en était moindre.\

# Ouverture

## Idées d'amélioration du projet

On pourrait améliorer le projet avec par exemple :
- Plus de niveaux à résoudre
- Une optimisation du code
- Une amélioration du système de déblocage de niveaux avec un système de points (suggéré par le professeur de physique-chimie)
- Une amélioration graphique (trop de gris ?)
- Un deuxième mode de jeu
- Un mode infini avec des molécules aléatoires
- Une version site web éventuellement
- Un mode "speedrun", chronométré
- Plus d'atomes -> ions pour plus de molécules
- Un système d'écriture de fichier pour reprendre là où on en était

## Analyse critique

Le projet est tout d'abord plutôt amusant à jouer et assez bien équilibré. D'un autre côté, l'interface graphique n'est pas parfaite et pourrait être plus belle.
Certains menus sont mal optimisés et donc laggent, comme celui de sélection des niveaux, ou alors les derniers niveaux, qui demandent la manipulation de nombreux atomes.
La bibliothèque pygame était déconseillée, donc le projet pourrait ne pas marcher pour tous les systèmes d'exploitation ou versions de python.

## Compétences personnelles développées
Chacun a développé de précieuses compétences lors de la réalisation du projet : organisation, gestion du temps, programmation ou encore nouveaux concepts.

## Démarche d'inclusion
Le groupe n'était malheureusement pas mixte.



