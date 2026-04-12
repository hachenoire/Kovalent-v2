# Kovalent Reforged

Ce dossier contient une réécriture complète du jeu original avec une architecture Python moderne, modulaire et beaucoup plus facile à comprendre que l'ancien `main.py` géant.

L'objectif de cette version n'est pas seulement de faire fonctionner le jeu, mais aussi de montrer de bonnes pratiques de conception :

- séparer les responsabilités,
- rendre la logique testable,
- éviter les variables globales partout,
- mieux organiser le code pour les futures évolutions.

## Lancement

Depuis la racine du dépôt :

```bash
./.venv/bin/python new_app/main.py
```

Si vous n'utilisez pas l'environnement virtuel du projet :

```bash
pip install pygame
python3 new_app/main.py
```

## Vue d'ensemble de l'architecture

L'application est organisée en plusieurs couches. Chaque couche a une responsabilité claire.

- `kovalent/domain` : les règles métier pures du jeu.
- `kovalent/application` : la logique qui orchestre une partie et les écrans.
- `kovalent/infrastructure` : la lecture des fichiers, les sauvegardes et les assets.
- `kovalent/ui` : tout ce qui concerne l'affichage et les interactions Pygame.
- `kovalent/app.py` : le point d'entrée principal qui relie toutes les couches.

Cette séparation permet d'éviter de mélanger dans un même fichier :

- les règles de chimie,
- la gestion de la sauvegarde,
- la logique des menus,
- le rendu graphique,
- la lecture des sons et des images.

## Pourquoi cette structure est meilleure

Dans l'ancienne version, presque tout était regroupé dans un seul gros fichier. Cela fonctionne pour un petit prototype, mais devient vite difficile à maintenir.

Dans cette réécriture :

- la logique du jeu ne dépend pas directement de Pygame,
- l'interface graphique ne décide pas seule des règles,
- les fichiers JSON sont chargés par des modules dédiés,
- les scènes sont séparées pour éviter les grands blocs `if menu == ...`,
- une partie de la logique peut être testée automatiquement.

Le résultat est un code :

- plus lisible,
- plus testable,
- plus réutilisable,
- plus simple à faire évoluer.

## Explication des couches

### 1. `domain` : le coeur du jeu

Le dossier `kovalent/domain` contient les éléments les plus importants sur le plan métier.

On y trouve :

- les modèles de données du jeu,
- les types utilisés un peu partout,
- les règles de chimie,
- la détection de victoire,
- la génération de la disposition initiale des atomes.

Exemples :

- `AtomSpec` décrit un type d'atome : symbole, valence, couleur, rayon.
- `LevelSpec` décrit un niveau : nom, formule, liste des atomes.
- `RuntimeAtom` représente un atome pendant une partie en cours.
- `ChemistryService` applique les règles de création et de modification des liaisons.

Idée importante :
le `domain` ne devrait pas dépendre de l'interface graphique. Cela permet de tester les règles du jeu sans ouvrir une fenêtre Pygame.

### 2. `application` : le chef d'orchestre

Le dossier `kovalent/application` contient la logique qui pilote l'état global du jeu.

La classe centrale est `GameSession`.

Elle gère par exemple :

- l'écran courant,
- le niveau actif,
- la sélection et le déplacement des atomes,
- le mode speedrun,
- la progression débloquée,
- les effets sonores à jouer.

Cette couche reçoit des intentions de haut niveau :

- démarrer un niveau,
- recommencer un niveau,
- faire glisser un atome,
- créer ou modifier une liaison,
- passer au niveau suivant.

L'intérêt est que l'interface ne manipule pas directement tous les détails du jeu. Elle demande simplement à la session d'effectuer une action.

### 3. `infrastructure` : les détails techniques

Le dossier `kovalent/infrastructure` contient les modules qui parlent au monde extérieur :

- lecture des fichiers JSON,
- sauvegarde de la progression,
- chargement des images,
- chargement des sons,
- gestion du cache des assets.

Cette couche s'occupe des détails techniques concrets, mais elle ne décide pas des règles du jeu.

Exemples :

- `JsonCatalogRepository` charge les niveaux et les atomes,
- `JsonSaveRepository` charge et sauvegarde la progression,
- `AssetStore` gère les images, les polices et l'audio.

### 4. `ui` : l'interface Pygame

Le dossier `kovalent/ui` contient tout ce qui est lié à l'affichage.

On y trouve :

- les scènes,
- les widgets,
- le thème graphique,
- le système de mise à l'échelle de la fenêtre.

La logique des écrans est découpée en scènes :

- `IntroScene`,
- `MainMenuScene`,
- `RulesScene`,
- `LevelSelectScene`,
- `GameplayScene`.

Chaque scène a un rôle clair :

- `handle_event(...)` : réagir aux clics, touches et mouvements,
- `update(...)` : mettre à jour l'état visuel,
- `draw(...)` : dessiner le contenu à l'écran.

Ce découpage évite d'avoir une seule énorme boucle avec des centaines de conditions.

### 5. `app.py` : l'assemblage final

Le fichier `kovalent/app.py` initialise Pygame, charge les données, crée la session, enregistre les scènes et lance la boucle principale.

Il sert de point de coordination entre les différentes couches.

Autrement dit :

- `domain` sait ce qu'est le jeu,
- `application` sait comment une partie évolue,
- `infrastructure` sait lire et charger les ressources,
- `ui` sait afficher et interagir,
- `app.py` branche tout ensemble.

## Le concept de classe en Python

Comme cette réécriture repose beaucoup sur les classes, il est important de comprendre ce concept.

### Qu'est-ce qu'une classe ?

Une classe est un modèle qui permet de créer des objets.

On peut voir une classe comme un plan de construction.

Par exemple :

- la classe décrit ce qu'un objet possède,
- un objet concret est une instance de cette classe.

Exemple simple :

```python
class Chien:
    def __init__(self, nom: str) -> None:
        self.nom = nom

    def aboyer(self) -> None:
        print(f"{self.nom} aboie")
```

Ici :

- `Chien` est une classe,
- `nom` est une donnée stockée dans l'objet,
- `aboyer()` est une action que l'objet peut faire,
- `self` représente l'objet lui-même.

Si on écrit :

```python
rex = Chien("Rex")
```

alors `rex` est une instance de la classe `Chien`.

### Pourquoi utiliser des classes ?

Les classes servent à regrouper dans une même structure :

- des données,
- des comportements,
- un rôle clair dans le programme.

Cela rend le code plus organisé qu'un ensemble de variables globales et de fonctions dispersées.

### Comment cela s'applique dans ce projet

Dans cette réécriture, plusieurs classes représentent des responsabilités précises.

#### `GameSession`

Cette classe représente l'état global de la partie.

Elle contient :

- les données sur le niveau courant,
- l'état du speedrun,
- la progression du joueur,
- la sélection de l'atome,
- les actions possibles.

C'est une bonne pratique, car toute la logique de partie est regroupée au même endroit.

#### `ChemistryService`

Cette classe regroupe les règles liées aux liaisons chimiques et à la victoire.

On évite ainsi d'éparpiller ces règles un peu partout dans l'interface graphique.

#### `AssetStore`

Cette classe centralise les images, les sons et les polices.

Sans cela, le code d'affichage devrait recharger des ressources dans plusieurs endroits, ce qui serait moins efficace et plus confus.

#### `Button`

Cette classe représente un bouton d'interface.

Elle contient :

- sa position,
- son texte,
- ses couleurs,
- la logique utile pour savoir s'il est survolé ou cliqué.

Cela évite de réécrire les mêmes calculs pour chaque bouton.

## Classe, objet, attribut, méthode

Voici les mots importants à retenir :

- **classe** : le modèle général.
- **objet** ou **instance** : un exemplaire concret créé à partir d'une classe.
- **attribut** : une donnée stockée dans l'objet.
- **méthode** : une fonction définie dans une classe.

Exemple concret dans ce projet :

- `RuntimeAtom` est une classe,
- un atome donné dans une partie est une instance,
- `position` ou `bonds` sont des attributs,
- `used_valence` ou `set_bond(...)` sont des méthodes ou comportements associés.

## Pourquoi cette approche est pédagogique

Cette nouvelle architecture montre qu'un programme peut être pensé comme un ensemble de composants spécialisés qui collaborent entre eux.

Au lieu de tout faire partout :

- les règles sont dans les services métier,
- l'état global est dans la session,
- l'affichage est dans les scènes,
- les ressources externes sont dans l'infrastructure.

C'est une manière beaucoup plus propre de construire un projet Python de taille moyenne.

## Tests

Le dossier `kovalent/tests` contient des tests automatiques qui vérifient une partie du comportement du coeur du jeu.

Cela permet de contrôler plus facilement qu'une modification ne casse pas :

- la logique des liaisons,
- la détection de victoire,
- le déblocage des niveaux,
- la logique du speedrun.

## Résumé

En une phrase, cette architecture sépare :

- ce que le jeu signifie,
- la manière dont il évolue,
- la manière dont il charge ses données,
- la manière dont il s'affiche.

C'est cette séparation qui rend la réécriture plus solide, plus claire et plus professionnelle.
