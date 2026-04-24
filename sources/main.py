# -*- coding: utf-8 -*-

# Projet : Kovalent
# Auteurs : Victor Alaimo et Kimi Vandaele-Otozaki ("KVTeam")

'''
==================== KOVALENT ====================

Bandeau d'informations - tenir à jour !

Version : 14.1

Dernière édition : Victor, 24/04/2026, 12h55


---------- COMMENTAIRE ----------

Après beaucoup de relectures, c'est enfin fini.
Mais en fait NON, car je vais encore l'améliorer !

Un truc que je ne regrette pas : n'avoir pas fait les déplacements adaptatifs par rapport à
la position de la souris : ça m'a pris un peu moins d'une heure ._.

J'ai plus aucune idée de comment et pourquoi je compte les versions mais c'est pas grave...

---------- NOTES ----------

    Note pour le stockage des atomes :
        atomes = [{id : 3, nom : "C", pos : (x=127, y=208), liaisons : [(id=5, nb_liaisons=2), (etc)]}, {atome2}, {etc}]

        type(atomes) = list[dict(int, str, tuple[int, int], list[tuple(int, int)])]

        liste des atomes
        atome = dictionnaire avec infos
        infos = id, formule, position et liaisons
    
    Penser à nommer les variables en anglais pour la réutilisation
    Penser aussi aux docstrings et aux commentaires
    Pas besoin de faire *SCALE pour du texte, la fonction le fait automatiquement
    Pas besoin de scale pour les boutons non plus
    
    j'ai passé trop de temps sur la detect_win mais j'ai réussi UwU


---------- HISTORIQUE DES MODIFICATIONS ----------

=> VERSION 11
    -> Version 11.0
        - Nouveaux arrières-plans
    -> Version 11.1
        - Importation de random
        - Système de particules de fête de la victoire du joueur
    -> Version 11.2
        - Fichier 'progress.txt' pour sauvegarder le progrès du joueur

=> VERSION 12
    -> Version 12.0
        - Déplacements des atomes plus propres et adaptatifs
        - Bordures invisibles améliorées
    -> Version 12.1
        - Réorganisation des dossiers (dossier img)
    -> Version 12.2
        - Ajout de pleins de sfx et de musique (j'ai bien galéré)
        - Bouton niveau suivant plus accessible
        - Animation du bouton niveau suivant

=> VERSION 13
    -> Version 13.0
        - Musique de doom pour les niveaux 50 et 51 (lol)
        - Diverses améliorations et corrections
        - Ordre aléatoire des atomes au début
    -> Version 13.1
        - Affichage du fps
        - Bouton pour le mode speedrun
        - Chronomètre pour le mode speedrun
    -> Version 13.2
        - Bouton pour les infos du mode speedrun
        - Sélection du niveau et modification du menu de jeu pour le mode speedrun
        - Modification des crédits et du menu d'informations

=> VERSION 14
    -> Version 14.0
        - Message de fin du speedrun et enregistrement du temps
        - Record à battre
        - Speedrun fonctionnel
        -> Version 14.0.1 : correction d'un bug avec les particules
    -> Version 14.1
        - Nouveau menu pour les niveaux custom
    

==================== main.py ====================
'''


# -----<===== INITIALISATION =====>-----

# ----- Modules importés -----

from __future__ import annotations
import pygame as pg
import json
from math import *
import os
from screeninfo import *
from random import *

# ----- Fichiers importés -----


with open(os.sep.join(['..', 'data', 'progress.txt']), 'r',encoding="utf-8") as f :
    progress = int(f.readlines()[0])
    #print(progress)

def set_progress(locked : int) -> None :
    with open(os.sep.join(['..', 'data', 'progress.txt']), 'r+',encoding="utf-8") as f :
        f.write(str(locked))

#kimi

with open(os.sep.join(['..', 'data', 'niveau.json']), 'r',encoding="utf-8") as file:
    levels_data = json.load(file) # importe le dict json sous le nom de levels_data
with open(os.sep.join(['..', 'data', 'atome.json']), 'r',encoding="utf-8") as fichier:
    atoms_data = json.load(fichier) # importe le dict json sous le nom de atoms_data

atoms_data = atoms_data["atome"] # maintenant c'est plus un dict c'est une list
levels_data = levels_data["niveau"]

#Easter egg à ne surtout pas mettre en marche
#PG5={ "nom": "PG5", "formule_brute":"C466591H444741N22147O22147", "atomes":["C"]*466591 + ["H"]*444741 + ["N"]*22147 + ["O"]*22147}
#print(PG5["atomes"][600000])
#levels_data.append(PG5)
#print(levels_data[52])


# Formatage des couleurs
# Victor

for i in range(len(atoms_data)) :
    atoms_data[i]["couleur"] = tuple(atoms_data[i]["couleur"])


# ----- Couleurs, constantes et variables/tableaux/autres -----

current_level = 0
fenetre_basique = False
if progress > 3 :
    skip_intro = True
else :
    skip_intro = False

if skip_intro :
    tick = 200
else :
    tick = 0

# Test pour une molécule de CH2O (chaque ligne est un atome)
atoms = [{"id" : 1, "name" : "C", "pos" : (702, 493), "links" : [(2, 2), (3, 1), (4, 1)]},
          {"id" : 2, "name" : "O", "pos" : (376, 430), "links" : [(1, 2)]},
          {"id" : 3, "name" : "H", "pos" : (868, 631), "links" : [(1, 1)]},
          {"id" : 4, "name" : "H", "pos" : (684, 314), "links" : [(1, 1)]}]


BLACK = (0, 0, 0)
DARK_GREY = (100, 100, 100)
LIGHT_GREY = (200, 200, 200)
WHITE = (255, 255, 255)
YELLOW = (230, 230, 0)
GREEN = (0, 200, 0)
ORANGE = (200, 100, 0)
RED = (200, 0, 0)
PURPLE = (100, 0, 150)
GRAY = (120, 120, 120)

def merge_colors(col1 : tuple, col2 : tuple) -> tuple :
    '''Produit une couleur moyenne des deux couleurs entrées'''
    col3 = ((col1[0]+col2[0])/2, (col1[1]+col2[1])/2, (col1[2]+col2[2])/2)
    return col3

print("\n") # Petit espace dans le shell pour les message d'erreur

mouse_pressed = False
mouse_pressed_right = False
moving = False
moved_atom_id = None
selected_atom = 0
difficulty = ""
level_color = ()
bg_type = "normal"
page = 1
has_won = False
vict_start_tick = 0
locked = progress
give_money = False
gm_tick = 0
win = False
particles = []
mouse_dx = 0 # distance de la souris au center de l'atome bougé
mouse_dy = 0
music_on = True
speedrun_mode = False
music_started = False
sp_start = 0
display_speedrun_infos = False
final_time = None
best_time = None
new_best = False

# ----- Initialisation de pygame et création de la fenêtre -----

# Par Victor

WINDOW_HEIGHT = 700
WINDOW_LENGHT = 1050

PROP_WINDOW = 1.5  # la proportion de la longueur sur la hauteur

if not fenetre_basique :
    # Parcoure les moniteurs et prend le principal
    try :
        for m in get_monitors() :
            if m.is_primary : # Le moniteur principal
        
                if (m.height - 150)*PROP_WINDOW <= m.width : # Si la fenêtre est assez large par rapport à ce qu'on veut si on prend la hauteur en modèle
            
                    WINDOW_HEIGHT = m.height - 150 # le 150 est une distance entre le bord haut et bas et la fenêtre
                    WINDOW_LENGHT = WINDOW_HEIGHT * PROP_WINDOW
            
                else :  # Sinon
             
                    WINDOW_LENGHT = m.width - 50
                    WINDOW_HEIGHT = WINDOW_LENGHT / PROP_WINDOW
    except :
        print("Erreur ! Le module screeninfo n'a pas fonctionné comme prévu ! Veuillez vérifier la version (0.8.1) et relancez le programme si besoin.")
        print("------------------------------")
        print("Initialisation du jeu avec une fenêtre de taille prédéfinie...")
        print("------------------------------")
    
        WINDOW_HEIGHT = 700
        WINDOW_LENGHT = 1050
    


SCALE = WINDOW_HEIGHT/800
# Correspond à la taille de la fenêtre, tout doit être proportionnel
# SCALE vaut 1.0 si la fenêtre à une hauteur (par défaut) de 800px, ce qui correspond à celle de fenetre_basique
# ATTENTION C'EST UN FLOAT
# Pas besoin de faire *SCALE pour du texte, la fonction le fait automatiquement et pareil pour les boutons



WINDOW_SIZE = (WINDOW_LENGHT, WINDOW_HEIGHT)

pg.init()

surface = pg.display.set_mode(WINDOW_SIZE)
pg.display.set_caption("Kovalent")

# IMAGES
title = pg.transform.scale(pg.image.load(os.sep.join(['..', "data", "img", "title.png"])), (800*SCALE, 100*SCALE))
restart_btn = pg.transform.scale(pg.image.load(os.sep.join(['..', "data", "img", "buttons", "restart.png"])), (50*SCALE, 50*SCALE))
lock_img = pg.transform.scale(pg.image.load(os.sep.join(['..', "data", "img", "lock.png"])), (40*SCALE, 45*SCALE))
icon = pg.transform.scale(pg.image.load(os.sep.join(['..', "data", "img", "icon.png"])), (32, 32))
btn_next = pg.transform.scale(pg.image.load(os.sep.join(['..', "data", "img", "buttons", "next.png"])), (80*SCALE, 80*SCALE))

pg.display.set_icon(icon)

# SONS

pg.mixer.init()

win_sfx = pg.mixer.Sound(os.sep.join(['..', 'data', 'sound', "win-sfx.wav"]))
btn_sfx = pg.mixer.Sound(os.sep.join(['..', 'data', 'sound', "btn-sfx.wav"]))
link_sfx = pg.mixer.Sound(os.sep.join(['..', 'data', 'sound', "link-sfx.wav"]))
error_sfx = pg.mixer.Sound(os.sep.join(['..', 'data', 'sound', "error-sfx.wav"]))
game_music = pg.mixer.Sound(os.sep.join(['..', 'data', 'sound', "music.wav"]))
doom_music = pg.mixer.Sound(os.sep.join(['..', 'data', 'sound', "music.wav"]))


# ----- Fonts -----

# Par Victor

prop_txt = 1.5 # change la taille de tous les textes (si on change de police, permet de switcher rapidement)

pg.font.init()

fichier_font = "freesansbold.ttf"

try :
    ftest = pg.font.SysFont(fichier_font, 20) # Si l'import du fichier ne marche pas, on prend celui par défaut
except :
    fichier_font = pg.font.get_default_font()
    print("Échec de l'import de la police de caractère")
    print("Démarrage avec la police par défaut...")


def create_text(text : str, size : int, color : tuple = WHITE) -> pg.Surface : # Par Victor
    '''Renvoie une Surface de texte, à blit pour afficher'''
    
    font = pg.font.SysFont(fichier_font, int(size*prop_txt))
        
    return font.render(text, True, color)


def print_txt(text : str, pos : tuple, size : int = 30, color : tuple = WHITE, center : bool=False, dest = surface) -> None : # Par Victor
    '''Affiche du texte dans la fenêtre, mis automatiquement à son échelle'''
    
    s = create_text(text, int(size*SCALE), color)
    if center :
        dest.blit(s, (int(pos[0]*SCALE)-s.get_width()/2, int(pos[1]*SCALE)-s.get_height()/2.5))
    else :
        dest.blit(s, (int(pos[0]*SCALE), int(pos[1]*SCALE)))


# -----<===== FONCTIONS PRINCIPALES =====>-----

def click() -> bool:# Kimi
    global mouse_pressed
    
    if pg.mouse.get_pressed()[0]:
        if not mouse_pressed:
            mouse_pressed = True
            return True
    else:
        mouse_pressed = False
    
    return False

def right_click() -> bool:#Kimi
    global mouse_pressed_right
    
    if pg.mouse.get_pressed()[2]:
        if not mouse_pressed_right:
            mouse_pressed_right = True
            return True
    else:
        mouse_pressed_right = False
    
    return False


def render() -> None : # Par Victor
    '''Affiche tout ce qu'il faut afficher à l'écran'''
    
    global menu
    
    # Les 200 premiers ticks sont pour une petite intro
    
    if tick < 200 :
        menu = "main"
        intro()
    else :
        if menu == "main" :
            main_menu()
            print_txt("FPS : " + str(int(clock.get_fps())), (5, 5), 12, WHITE, False)
        elif menu == "level select" :
            level_select()
            print_txt("FPS : " + str(int(clock.get_fps())), (5, 5), 12, WHITE, False)
        elif menu == "rules" :
            rules()
            print_txt("FPS : " + str(int(clock.get_fps())), (5, 5), 12, WHITE, False)
        elif menu == "game":
            game()
            print_txt("FPS : " + str(int(clock.get_fps())), (5, 785), 12, WHITE, False)
        elif menu == "my_levels" :
            my_levels()
        

def create_particle_burst(p : list[dict]=[]) -> list[dict] :
    '''Crée un salve de particules, depuis les coins inférieurs'''
    # Gauche
    start = len(p)
    p = p + [{} for _ in range(randint(10, 15))]
    for i in range(start, len(p)) :
        col = randint(150, 255)
        particule = {"col" : (col, col, col), "pos" : (0, 800), "vel" : (1+(random()*8), -8+(random()*-6)), "size" : 10+(random()*10)}
        p[i] = particule
    
    # Droite
    start = len(p)
    p = p + [{} for _ in range(randint(10, 15))]
    for i in range(start, len(p)) :
        col = randint(150, 255)
        particule = {"col" : (col, col, col), "pos" : (1200, 800), "vel" : (-1+(random()*-8), -8+(random()*-6)), "size" : 10+(random()*10)}
        p[i] = particule
    
    return p


def evolve_particles(p : list[dict]) -> list[dict] :
    '''Bouge et supprime les particules pour 1 frame'''
    
    copy_size = len(p)
    for i in p :
        if i["pos"][1] > 800 :
            copy_size -= 1
    
    copy = [{} for _ in range(copy_size)]
    
    j = 0
    for i in range(len(p)) :
        part = p[i]
        if part["pos"][1] <= 800 :
            part["pos"] = (part["pos"][0] + part["vel"][0], part["pos"][1] + part["vel"][1])
            part["vel"] = (part["vel"][0] * 0.99, part["vel"][1] + 0.2)
            copy[j] = part
            j += 1
    return copy

def render_particles(p : list[dict]) -> None :
    '''Dessine toutes les particules'''
    for i in p :
        pg.draw.circle(surface, i["col"], scaling(i["pos"]), i["size"]*SCALE)


def intro() -> None : # Par Victor
    '''Fait une intro des ticks 0 à 200'''
    if tick < 20 :
        surface.fill(BLACK)
    elif tick <= 80 :
        surface.fill(BLACK)
        teinte = ((tick-20)/60)*255
        print_txt("KVTeam", (600, 350), 50, (teinte, teinte, teinte), True)
        pg.draw.rect(surface, BLACK, ((200 + 200-((tick-20)/60)*200)*SCALE, 200*SCALE, 200*SCALE, 600*SCALE))
        pg.draw.rect(surface, BLACK, ((800 - 200+((tick-20)/60)*200)*SCALE, 200*SCALE, 200*SCALE, 600*SCALE))
    elif tick >= 170 :
        surface.fill(BLACK)
        teinte = (1-((tick-170)/30))*255
        print_txt("KVTeam", (600, 350), 50, (teinte, teinte, teinte), True)


def main_menu() -> None : # Par Victor
    '''Affiche le menu principal'''
    global menu, running, bg_type, page, music_on, music_started
    
    surface.fill(DARK_GREY)
    background(GRAY)
    
    if not music_started :
        music_started = True
        game_music.play(-1)
    
    surface.blit(title, (200*SCALE, 100*SCALE))
    
    if button((450, 300, 300, 100), "Jouer", BLACK, 55, LIGHT_GREY, WHITE) :
        menu = "level select"
    
    if button((400, 500, 400, 100), "Informations", BLACK, 50, LIGHT_GREY, WHITE) :
        menu = "rules"
        page = 1
    
    if button((990, 745, 200, 50), "Quitter", BLACK, 35, (255, 0, 0), merge_colors(WHITE, (255, 0, 0))) :
        running = False
    
    print_txt("Arrière-plan :", (10, 750), 40, WHITE, False)
    if bg_type == "normal" :
        if button((285, 745, 180, 50), "Carrés", BLACK, 35, GREEN, merge_colors(GREEN, WHITE)) :
            bg_type = "circles"
    elif bg_type == "circles" :
        if button((285, 745, 180, 50), "Cercles", BLACK, 35, GREEN, merge_colors(GREEN, WHITE)) :
            bg_type = "triangles"
    elif bg_type == "triangles" :
        if button((285, 745, 180, 50), "Triangles", BLACK, 35, GREEN, merge_colors(GREEN, WHITE)) :
            bg_type = "disabled"
    elif bg_type == "disabled" :
        if button((279, 745, 192, 50), "Désactivé", BLACK, 35, LIGHT_GREY, merge_colors(LIGHT_GREY, WHITE)) :
            bg_type = "normal"
    
    print_txt("Musique :", (10, 690), 40, WHITE, False)
    if music_on :
        if button((220, 685, 70, 50), "On", BLACK, 35, GREEN, merge_colors(GREEN, WHITE)) :
            music_on = False
            game_music.stop()
    else :
        if button((220, 685, 70, 50), "Off", BLACK, 35, LIGHT_GREY, merge_colors(LIGHT_GREY, WHITE)) :
            music_on = True
            game_music.play(-1)

def my_levels() -> None :
    global menu
    
    surface.fill(DARK_GREY)
    background(GRAY)
    
    print_txt("Rien ici pour l'instant... :/", (600, 300), 40, WHITE, True)
    
    if button((50, 650, 300, 100), "Retour", BLACK, 60, LIGHT_GREY, WHITE) :
            menu = "level select"


def rules() -> None : # Par Victor
    '''Affiche le menu des règles du jeu'''
    global menu, page, give_money, gm_tick

    surface.fill(DARK_GREY)
    background(GRAY)
    
    print_txt("Page " + str(page) + "/4", (600, 700), 40, WHITE, True)
    
    if page == 1 :
        print_txt("Informations sur le projet", (600, 100), 80, WHITE, True)
        print_txt("Règles du jeu", (600, 200), 50, WHITE, True)
        start_x = 150*SCALE
        print_txt("Le but du jeu est de relier les atomes entre eux en", (start_x, 300), 30, WHITE, False)
        print_txt("respectant leur nombre de valence (voir page 3). Vous devez former", (start_x, 350), 30, WHITE, False)
        print_txt("une molécule avec ces atomes, avec une structure libre.", (start_x, 400), 30, WHITE, False)
        print_txt("Il y a 50 niveaux, de plus en plus difficiles, à résoudre,", (start_x, 450), 30, WHITE, False)
        print_txt("les difficultés allant de facile à impossible. Pour débloquer un", (start_x, 500), 30, WHITE, False)
        print_txt("niveau et ainsi progresser, il faut d'abord finir le précédent.", (start_x, 550), 30, WHITE, False)
        
        if button((850, 650, 300, 100), "Suivant", BLACK, 60, LIGHT_GREY, WHITE) :
            page = 2
        if button((50, 650, 300, 100), "Menu", BLACK, 60, LIGHT_GREY, WHITE) :
            menu = "main"
            give_money = False
    
    elif page == 2 :
        print_txt("Informations sur le projet", (600, 100), 80, WHITE, True)
        print_txt("Instructions", (600, 200), 50, WHITE, True)
        start_x = 150*SCALE
        print_txt("Vous pouvez bouger les différents atomes au sein de l'aire de", (start_x, 300), 30, WHITE, False)
        print_txt("jeu en les faisant glisser à l'aide de la souris.", (start_x, 350), 30, WHITE, False)
        print_txt("Cliquez sur un atome pour le sélectionner, et faites un", (start_x, 400), 30, WHITE, False)
        print_txt("clic droit sur un autre atome pour créer un lien entre les deux.", (start_x, 450), 30, WHITE, False)
        print_txt("En cliquant plusieurs fois sur l'atome de destination, changez", (start_x, 500), 30, WHITE, False)
        print_txt("la force du lien (double, triple...) ou supprimez-le.", (start_x, 550), 30, WHITE, False)
        
        if button((850, 650, 300, 100), "Suivant", BLACK, 60, LIGHT_GREY, WHITE) :
            page += 1
        if button((50, 650, 300, 100), "Précédent", BLACK, 50, LIGHT_GREY, WHITE) :
            page -= 1
    
    elif page == 3 :
        print_txt("Informations sur le projet", (600, 100), 80, WHITE, True)
        print_txt("Atomes", (600, 200), 50, WHITE, True)
        start_x = 125*SCALE
        print_txt("Au cours du jeu, vous croiserez plusieurs atomes différents.", (start_x, 300), 30, WHITE, False)
        print_txt("Chacun a un nombre de liaisons avec d'autres atomes à respecter.", (start_x, 350), 30, WHITE, False)
        print_txt("Par exemple, l'atome de carbone (C) peut avoir 4 liaisons au total,", (start_x, 400), 30, WHITE, False)
        print_txt("ou alors 2 liaisons doubles, ou encore 1 triple et 1 simple. L'atome", (start_x, 450), 30, WHITE, False)
        print_txt("d'hydrogène (H), lui, ne peut en avoir qu'une seule.", (start_x, 500), 30, WHITE, False)
        
        if button((850, 650, 300, 100), "Suivant", BLACK, 60, LIGHT_GREY, WHITE) :
            page += 1
        if button((50, 650, 300, 100), "Précédent", BLACK, 50, LIGHT_GREY, WHITE) :
            page -= 1
    
    elif page == 4 :
        print_txt("Informations sur le projet", (600, 100), 80, WHITE, True)
        print_txt("Crédits", (600, 200), 50, WHITE, True)
        start_x = 150*SCALE
        print_txt("Merci à notre duo de développeurs acharnés :", (start_x, 250), 30, WHITE, False)
        print_txt('''Victor et Kimi (ou "KVTeam" comme on aime s'appeler)''', (start_x, 290), 30, WHITE, False)
        print_txt("Projet réalisé en python, avec Pygame", (start_x, 330), 30, WHITE, False)
        print_txt("Sons et musique : pixabay.com + Mike Gordon (nv. 50)", (start_x, 370), 30, WHITE, False)
        print_txt("Tous les assets visuels du jeu ont été réalisés par Victor.", (start_x, 410), 30, WHITE, False)
        print_txt("Ceci est une version plus poussée du programme que l'original,", (start_x, 450), 30, (255, 100, 100), False)
        print_txt("développée en solo par Victor, à partir de la version 10 du jeu.", (start_x, 490), 30, (255, 100, 100), False)
        print_txt("Merci à notre prof, et merci à VOUS, qui jouez à notre jeu :)", (start_x, 540), 32, GREEN, False)
        
        if button((50, 650, 300, 100), "Précédent", BLACK, 50, LIGHT_GREY, WHITE) :
            page -= 1
        
        if button((850, 650, 300, 100), "Compris !", BLACK, 55, LIGHT_GREY, WHITE) :
            menu = "main"
            give_money = False
        
        if not give_money :
            if button((950, 600, 200, 40), "Donner des sous", BLACK, 20, YELLOW, merge_colors(YELLOW, WHITE)) :
                give_money = True
                gm_tick = tick
        else :
            print_txt("Merci mais on n'est pas des voleurs", (950, 610), 20, YELLOW, True)
            print_txt("(Mais on peut vous débarrasser de votre argent si vous voulez vraiment)", (920, 630), 15, YELLOW, True)
            if tick - gm_tick > 230 :
                give_money = False
        
            


def level_select() : # Victor
    '''Affiche le menu de sélection du niveau à jouer'''
    global menu, current_level, difficulty, level_color, selected_atom, atoms, has_won, win, speedrun_mode, sp_start, display_speedrun_infos
    
    surface.fill(DARK_GREY)
    background(GRAY)
    
    print_txt("Sélectionnez un niveau", (600, 80), 70, WHITE, True)

    if button((20, 680, 250, 100), "Menu", BLACK, 60, LIGHT_GREY, WHITE):
        menu = "main"
    
    if not display_speedrun_infos :
        if button((300, 680, 400, 100), "Mes niveaux", BLACK, 60, LIGHT_GREY, WHITE):
            menu = "my_levels"
            
        print_txt("Mode speedrun :", (720, 715), 40, WHITE, False)
        if speedrun_mode :
            if button((1055, 710, 70, 50), "On", BLACK, 35, GREEN, merge_colors(GREEN, WHITE)) :
                speedrun_mode = False
        else :
            if button((1055, 710, 70, 50), "Off", BLACK, 35, LIGHT_GREY, merge_colors(LIGHT_GREY, WHITE)) :
                speedrun_mode = True
        if button((1140, 720, 30, 30), "?", BLACK, 30, LIGHT_GREY, merge_colors(LIGHT_GREY, WHITE)) :
            display_speedrun_infos = True
        
        if best_time != None :
            minutes, seconds, cs  = str(convert_time(best_time)[0]), str(convert_time(best_time)[1]), str(convert_time(best_time)[2])
        
            if len(seconds) == 1 and minutes != "0" :
                seconds = "0" + seconds
            if len(cs) == 1 :
                cs = "0" + cs
            
            if minutes == "0" :
                print_txt("Meilleur temps : " + seconds + "." + cs, (700, 760), 30, WHITE, False)
            else :
                print_txt("Meilleur temps : " + minutes + ":" + seconds + "." + cs, (700, 760), 30, WHITE, False)
    else :
        print_txt("Le mode speedrun chronomètre votre vitesse de résolution", (400, 695), 25, WHITE, False)
        print_txt("des niveaux. Le but est de résoudre du niveau 1 au 40 le", (400, 720), 25, WHITE, False)
        print_txt("plus vite possible pour battre votre record !", (400, 745), 25, WHITE, False)
        if button((1140, 720, 30, 30), "?", BLACK, 30, GREEN, merge_colors(GREEN, WHITE)) :
            display_speedrun_infos = False

    if speedrun_mode :
        temp_locked = 2
    else :
        temp_locked = locked
    
    num = 1
    for l in range(5):
        for i in range(10):
            x_pos = 150 + i * 100 - 30
            y_pos = 200 + l * 90 - 30
            
            if l == 0 :
                col = GREEN
            elif l == 1 :
                col = YELLOW
            elif l == 2 :
                col = ORANGE
            elif l == 3 :
                col = RED
            elif l == 4 and i < 9 :
                col = PURPLE
            else :
                col = (0, 0, 150)

            if num < temp_locked :
                b = button((x_pos, y_pos, 60, 60), str(num), BLACK, 30, merge_colors(col, LIGHT_GREY), merge_colors(merge_colors(col, LIGHT_GREY), WHITE))
            else :
                button((x_pos, y_pos, 60, 60), "", BLACK, 30, merge_colors(col, BLACK), merge_colors(col, BLACK))
                surface.blit(lock_img, ((x_pos+10)*SCALE, (y_pos+7.5)*SCALE))
                b = False
            
            if b :
                current_level = num # On enregistre le niveau
                level_info = levels_data[num-1]
                atoms = create_atoms(current_level)
                menu = "game"
                has_won = False
                win = False
                selected_atom = 0
                new_best = False
                
                if speedrun_mode :
                    sp_start = pg.time.get_ticks()
                                
                if current_level <= 10 :
                    difficulty = "Facile"
                    level_color = GREEN
                elif current_level <= 20 :
                    difficulty = "Normal"
                    level_color = YELLOW
                elif current_level <= 30 :
                    difficulty = "Difficile"
                    level_color = ORANGE
                elif current_level <= 40 :
                    difficulty = "Expert"
                    level_color = RED
                elif current_level <= 49 :
                    difficulty = "Maître"
                    level_color = PURPLE
                else :
                    difficulty = "Impossible"
                    level_color = BLACK
                
                if current_level >= 50 and music_on :
                    game_music.stop()
                    doom_music.play(-1)
                
            num += 1


def game(): # Kimi et Victor
    '''Affiche et gère le jeu'''
    global menu, selected_atom, moving, moved_atom_id, current_level, atoms, has_won, vict_start_tick, locked, win, particles, mouse_dx, mouse_dy, final_time, best_time, new_best
    
    surface.fill(DARK_GREY)
    background(merge_colors(level_color, DARK_GREY)) # kimi
    level_info(current_level)
    
    if win :
        if not has_won :
            vict_start_tick = tick
            
            particles = create_particle_burst(particles)
            
            win_sfx.play()
            
            if speedrun_mode and current_level == 40 :
                final_time = pg.time.get_ticks() - sp_start
                if best_time == None :
                    best_time = final_time
                    new_best = True
                elif final_time < best_time :
                    best_time = final_time
                    new_best = True
                else :
                    new_best = False
            
            if current_level == locked-1 :
                locked += 1
                set_progress(locked)
        has_won = True
        
    if speedrun_mode and current_level < 41 and not (current_level == 40 and has_won) :
        menu_btn_txt = "Abandonner"
    else :
        menu_btn_txt = "Menu"
        
    if button((15, 15, 190, 30), menu_btn_txt, BLACK, 20, LIGHT_GREY, WHITE):
        menu = "level select"
        moving = False # Sécu
        has_won = False
        win = False
        particles = []
        if current_level >= 50 and music_on :
            doom_music.stop()
            game_music.play(-1)

    
    if current_level < locked-1 and current_level<50 and not speedrun_mode :#kimi
        if button((15, 45, 190, 30), "Niveau suivant", BLACK, 20, LIGHT_GREY, WHITE) :
            current_level += 1
            atoms = create_atoms(current_level)
            selected_atom = 0
            moving = False
            moved_atom_id = None
            has_won = False
            win = False
            new_best = False
            if current_level >= 50 and music_on :
                game_music.stop()
                doom_music.play(-1)

            
    elif has_won and current_level==50:
        if button((15, 45, 190, 30), "Fin ?", BLACK, 20, LIGHT_GREY, WHITE) :
            current_level += 1
            atoms = create_atoms(current_level)
            selected_atom = 0
            moving = False
            moved_atom_id = None
            has_won = False
            win = False
            new_best = False
            if current_level >= 50 :
                game_music.stop()
                doom_music.play(-1)

            
    elif current_level == locked-1 and current_level < 50 and not speedrun_mode : #kimi
        if button((15, 45, 190, 30), "Niveau suivant", BLACK, 20, DARK_GREY, DARK_GREY) :
            moving = False
    
    
    if button((215, 15, 60, 60), "", BLACK, 20, LIGHT_GREY, WHITE):
        atoms = create_atoms(current_level)
        selected_atom = 0
        has_won = False
        win = False
    surface.blit(restart_btn, (220*SCALE, 20*SCALE))
    
    
    mx, my = pg.mouse.get_pos()
    is_clicking = pg.mouse.get_pressed()[0]
    #is_right_clicking = pg.mouse.get_pressed()[2] sert a rien pour l'instant
            
    # relâche le bouton
    if not is_clicking:
        moving = False
        moved_atom_id = None
    
    
    display_atoms(atoms)
    
    render_particles(particles)
    particles = evolve_particles(particles)
    
    if has_won :
        if speedrun_mode and current_level == 40 :
            time_difference = tick - vict_start_tick
            if time_difference < 40 :
                print_txt("Speedrun terminé !", (600, 300), sqrt(sin((time_difference)/80*pi))*80, GREEN, True)
            else :
                print_txt("Speedrun terminé !", (600, 300), 80, GREEN, True)
                minutes, seconds, cs  = str(convert_time(final_time)[0]), str(convert_time(final_time)[1]), str(convert_time(final_time)[2])
        
                if len(seconds) == 1 and minutes != "0" :
                    seconds = "0" + seconds
                if len(cs) == 1 :
                    cs = "0" + cs
                
                if minutes == "0" :
                    print_txt("Temps final : " + seconds + "." + cs, (600, 500), 60, GREEN, True)
                else :
                    print_txt("Temps final : " + minutes + ":" + seconds + "." + cs, (600, 500), 60, GREEN, True)
                
                if new_best :
                    print_txt("Nouveau record !", (600, 600), 50, GREEN, True)
                else :
                    minutes, seconds, cs  = str(convert_time(best_time)[0]), str(convert_time(best_time)[1]), str(convert_time(best_time)[2])
        
                    if len(seconds) == 1 and minutes != "0" :
                        seconds = "0" + seconds
                    if len(cs) == 1 :
                        cs = "0" + cs
                    
                    if minutes == "0" :
                        print_txt("Meilleur temps : " + seconds + "." + cs, (600, 600), 50, GREEN, True)
                    else :
                        print_txt("Meilleur temps : " + minutes + ":" + seconds + "." + cs, (600, 600), 50, GREEN, True)
                
        else :
            #print(sqrt(sin((time_difference)/80*pi))*80)
            time_difference = tick - vict_start_tick
            if time_difference < 40 :
                print_txt("Niveau résolu !", (600, 300), sqrt(sin((time_difference)/80*pi))*80, WHITE, True)
                if speedrun_mode:
                    if button((540, 540, 120, 120), "", BLACK, 20, LIGHT_GREY, WHITE) :
                        current_level += 1
                        atoms = create_atoms(current_level)
                        selected_atom = 0
                        moving = False
                        moved_atom_id = None
                        has_won = False
                        win = False
                        if current_level >= 50 and music_on :
                            game_music.stop()
                            doom_music.play(-1)
                    surface.blit(btn_next, (560*SCALE, 560*SCALE))
                
            elif time_difference < 250 :
                print_txt("Niveau résolu !", (600, 300), 80, WHITE, True)
                if current_level < 51 :
                    if button((540, 540, 120, 120), "", BLACK, 20, LIGHT_GREY, WHITE) :
                        current_level += 1
                        atoms = create_atoms(current_level)
                        selected_atom = 0
                        moving = False
                        moved_atom_id = None
                        has_won = False
                        win = False
                        if current_level >= 50 and music_on :
                            game_music.stop()
                            doom_music.play(-1)
                    surface.blit(btn_next, (560*SCALE, 560*SCALE))
                
            elif time_difference < 275 :
                print_txt("Niveau résolu !", (600, 300), 80-((time_difference - 250)/25)*80, WHITE, True)
                if current_level < 51 :
                    if button((540+((time_difference - 250)/25)*500, 540+((time_difference - 250)/25)*100, 120, 120), "", BLACK, 20, LIGHT_GREY, WHITE) :
                        current_level += 1
                        atoms = create_atoms(current_level)
                        selected_atom = 0
                        moving = False
                        moved_atom_id = None
                        has_won = False
                        win = False
                        if current_level >= 50 and music_on :
                            game_music.stop()
                            doom_music.play(-1)
                    surface.blit(btn_next, (((540+((time_difference - 250)/25)*500)+20)*SCALE, ((540+((time_difference - 250)/25)*100)+20)*SCALE))
                
            else :
                if current_level < 51 :
                    if button((1040, 640, 120, 120), "", BLACK, 20, LIGHT_GREY, WHITE) :
                        current_level += 1
                        atoms = create_atoms(current_level)
                        selected_atom = 0
                        moving = False
                        moved_atom_id = None
                        has_won = False
                        win = False
                        if current_level >= 50 and music_on :
                            game_music.stop()
                            doom_music.play(-1)
                    surface.blit(btn_next, (1060*SCALE, 660*SCALE))
    

    if click(): # Si on clique
        move_target = find_atom_under_mouse(atoms)
        if move_target != None :
            selected_atom = move_target 
            moved_atom_id = move_target
            mouse_dx = (mx - find_in_dlist(atoms, "id", moved_atom_id)["pos"][0]*SCALE)
            mouse_dy = (my - find_in_dlist(atoms, "id", moved_atom_id)["pos"][1]*SCALE)
            moving = True
            #print(selected_atom)
        else :
            selected_atom = 0
            #print(selected_atom)
    
    # Mise à jour de la position
    if moving and moved_atom_id != None :
        for atome in atoms:
            if atome["id"] == moved_atom_id :
                atome["pos"] = ((mx - mouse_dx)/SCALE, (my - mouse_dy)/SCALE)
                #print("x : " + str(mouse_dx), " y : " + str(mouse_dy))
                    
                if atome["pos"][0] < 60 :
                    atome["pos"] = (60, atome["pos"][1])
                if atome["pos"][0] > 1140 :
                    atome["pos"] = (1140, atome["pos"][1])
                if atome["pos"][1] < 150 :
                    atome["pos"] = (atome["pos"][0], 150)
                if atome["pos"][1] > 740 :
                    atome["pos"] = (atome["pos"][0], 740)
    
    
    create_links()
    
    if speedrun_mode and not (current_level == 40 and has_won) :
        
        sp_time = pg.time.get_ticks() - sp_start
        minutes, seconds, cs  = str(convert_time(sp_time)[0]), str(convert_time(sp_time)[1]), str(convert_time(sp_time)[2])
        
        if len(seconds) == 1 and minutes != "0" :
            seconds = "0" + seconds
        if len(cs) == 1 :
            cs = "0" + cs
        
        if minutes == "0" :
            pg.draw.rect(surface, BLACK, (1050*SCALE, 735*SCALE, 300*SCALE, 100*SCALE))
            print_txt("   " + seconds, (1030, 745), 50, GREEN, False)
            print_txt("." + cs, (1030 + create_text("   " + seconds, 50).get_width(), 760), 30, GREEN, False)
        else :
            pg.draw.rect(surface, BLACK, (995*SCALE, 735*SCALE, 300*SCALE, 100*SCALE))
            print_txt(minutes + ":" + seconds, (1010, 745), 50, GREEN, False)
            print_txt("." + cs, (1010 + create_text(minutes + ":" + seconds, 50).get_width(), 760), 30, GREEN, False)
        
        #print(((sp_time/60000)-minutes))
    
    #print(mouse_pressed)
    #print_txt("Debug : mousepos=" + str(pg.mouse.get_pos()) + ", win=" + str(detect_win()), (600, 750), 30, WHITE, True)


def convert_time(time) -> (int, int, int):
    '''Convertit des millisecondes en minutes/secondes/centièmes'''
    minutes = int(time/60000)
    seconds = int(((time/60000)-int(minutes))*60)
    cs = int((((time/60000)-int(minutes))*60-int(seconds))*100)

    return minutes, seconds, cs

def create_links() -> None:#kimi
    """gère les liaison entre atomes"""
    global selected_atom, win
    
    target_id = find_atom_under_mouse(atoms)
    
    if right_click() and target_id != None and selected_atom != 0 and target_id != selected_atom:
        
        atom1 = find_in_dlist(atoms, "id", selected_atom)
        atom2 = find_in_dlist(atoms, "id", target_id)
        atom1_valence = find_valence(atom1['name'])
        atom2_valence = find_valence(atom2['name'])
        #print(atom1["links"][0][1])
        if atom1_valence < atom2_valence and atom1_valence < 3 :
            atom12_valence = atom1_valence
        elif atom2_valence <= atom1_valence and atom2_valence <= 3 :
            atom12_valence = atom2_valence
        else:
            atom12_valence = 3
        
        
        liaison_existante_1 = None
        for l in atom1["links"]:
            if l[0] == target_id:
                liaison_existante_1 = l
                break
                
        liaison_existante_2 = None
        for l in atom2["links"]:
            if l[0] == selected_atom:
                liaison_existante_2 = l
                break
        
        atom1_nb_liaisons = 0
        for i in atom1["links"]:
            atom1_nb_liaisons += int(i[1])
        #print(atom1_nb_liaisons)
        
        atom2_nb_liaisons = 0
        for i in atom2["links"]:
            atom2_nb_liaisons += int(i[1])
        #print(atom2_nb_liaisons)

        if liaison_existante_1 == None :
            if atom1_nb_liaisons<atom1_valence and atom2_nb_liaisons<atom2_valence:
                atom1["links"].append((target_id, 1))
                atom2["links"].append((selected_atom, 1))
                link_sfx.play()
            else :
                error_sfx.play()
        else:
             
            atom1["links"].remove(liaison_existante_1)
            atom2["links"].remove(liaison_existante_2)
            nb_liaisons = liaison_existante_1[1]
            
            if nb_liaisons < atom12_valence and atom1_nb_liaisons<atom1_valence and atom2_nb_liaisons<atom2_valence: 
                atom1["links"].append((target_id, nb_liaisons + 1))
                atom2["links"].append((selected_atom, nb_liaisons + 1))
                link_sfx.play()
            else :
                error_sfx.play()
            
        win = detect_win()


def find_valence(atom_name:str)->int:#kimi optimisé par Victor avec appel de la fonction find_in_dlist
    """trouve le nombre de valence d'un atome"""
    
    return find_in_dlist(atoms_data, "symbole", atom_name)["valence"]


def scaling(pos : tuple) -> tuple[int, int] : # Par Victor
    '''Prend une paire de coordonnées et la renvoie après l'avoir mise à l'échelle'''
    x = int(pos[0]*SCALE)
    y = int(pos[1]*SCALE)
    return (x, y)


def lines_moved(spacing, s, p, p2) -> None : # désolé mais j'ai la flemme de spécifier une fonction qui ne sert qu'une fois - Par Victor
    '''Utile uniquement pour la fonction display_atoms(), pour gagner de la place, vu la répétition'''
    size = int(s*SCALE)
    
    # Kalkuls matématik (pas du tout copiés du professeur, voyons...)
    
    vect_x = p[0]-p2[0]
    vect_y = p[1]-p2[1]
    
    truc = (spacing*sqrt(vect_x**2+vect_y**2)) # jsp comment nommer la variable j'ai plus d'inspi
    # spacing est en unité cheloue, mais en gros plus c'est petit, plus les lignes s'écartent du centre
     
    x = p[0]+(vect_y/truc)
    y = p[1]-(vect_x/truc)
    x2 = p2[0]+(vect_y/truc)
    y2 = p2[1]-(vect_x/truc)
    pg.draw.line(surface, LIGHT_GREY, scaling((x, y)), scaling((x2, y2)), size)
    
    x = p[0]-(vect_y/truc)
    y = p[1]+(vect_x/truc)
    x2 = p2[0]-(vect_y/truc)
    y2 = p2[1]+(vect_x/truc)
    pg.draw.line(surface, LIGHT_GREY, scaling((x, y)), scaling((x2, y2)), size)


def find_atom_under_mouse(liste_atomes: list) -> int | None : # Kimi
    '''Renvoie l'ID de l'atome ou None si vide'''
    mx, my = pg.mouse.get_pos()
    for atome in liste_atomes:
        # On récupère les infos de l'atome (rayon) dans le JSON
        info = find_in_dlist(atoms_data, "symbole", atome["name"])
        rayon_ecran = info["rayon"] * SCALE
        # Position 
        ax, ay = scaling(atome["pos"])
        # Calcul de la distance
        distance = sqrt((mx - ax)**2 + (my - ay)**2)
        
        if distance <= rayon_ecran:
            return atome["id"]
    return None


def display_atoms(a : list) -> None : # Par Victor
    '''Affiche les atomes de la liste entrée et leur liaisons'''
    
    for i in range(len(a)) : # pour chaque atome
        p = a[i]["pos"]
        for j in a[i]["links"] :
            if a.index(find_in_dlist(atoms, "id", j[0])) > i :
                p2 = find_in_dlist(atoms, "id", j[0])["pos"]
                
                if j[1] == 1 : # Liaison simple
                    pg.draw.line(surface, LIGHT_GREY, scaling(p), scaling(p2), int(10*SCALE))
                    
                elif j[1] == 2 : # Liaison double
                    size = 8.5
                    spacing = 0.1
                    
                    lines_moved(spacing, size, p, p2)
                    
                elif j[1] == 3 : # Liaison triple
                    size = 7
                    spacing = 0.07
                    
                    lines_moved(spacing, size, p, p2)
                    
                    pg.draw.line(surface, LIGHT_GREY, scaling(p), scaling(p2), size)
                    
                elif j[1] == 4 : # Liaison quadruple
                    size = 6
                    
                    spacing = 0.05
                    lines_moved(spacing, size, p, p2)
                    
                    spacing = 0.15
                    lines_moved(spacing, size, p, p2)
            
            
    for i in a : # pour chaque atome
        a_info = find_in_dlist(atoms_data, "symbole", i["name"])
        p = i["pos"]
        pg.draw.circle(surface, a_info["couleur"], scaling(p), a_info["rayon"]*SCALE)
        if i["name"] == "C" :
            print_txt(i["name"], p, a_info["rayon"]*1.3, WHITE, True) # Juste pour le carbone, on met le symbole en blanc (vu qu'il est noir)
        else :
            print_txt(i["name"], p, a_info["rayon"]*1.3, BLACK, True)
        if i["id"] == selected_atom :
            pg.draw.circle(surface, YELLOW, scaling(p), (a_info["rayon"]+10)*SCALE, 5)


def find_in_dlist(t : list[dict], key : str, value : object) -> dict : # Par Victor
    '''Recherche dans t le premier dictionnaire avec une clef d'une certaine valeur'''
    r = {}
    for i in t :
        if i[key] == value :
            r = i
    return r


def button(rect : tuple, text : str, text_color : tuple, text_size : int, color : tuple, color2 : tuple) -> bool : # Par Victor
    '''Affiche un bouton à rect(gauche, haut, longueur, hauteur),
    du texte, avec couleur et taille, et sa couleur, et renvoie True si il est cliqué.
    Il passe à la couleur de color2 (optionnel) quand la souris est dessus'''
    global mouse_pressed
    
    rleft = rect[0]
    rtop = rect[1]
    rwidth = rect[2]
    rheight = rect[3]
    
    mp = pg.mouse.get_pos()
    mpx = mp[0]
    mpy = mp[1]
    
    if mpx >= rleft*SCALE and mpy >= rtop*SCALE and mpx <= (rleft + rwidth)*SCALE and mpy <= (rtop + rheight)*SCALE :
        pg.draw.rect(surface, color2, (rleft*SCALE, rtop*SCALE, rwidth*SCALE, rheight*SCALE))
        print_txt(text, ((rleft + (rwidth/2)), (rtop + (rheight/2))), text_size, text_color, True)
        if click() : # click gauche
            #print("truc")
            btn_sfx.play()
            return True
        else :
            return False
                
    else :
        pg.draw.rect(surface, color, (rleft*SCALE, rtop*SCALE, rwidth*SCALE, rheight*SCALE))
        print_txt(text, ((rleft + (rwidth/2)), (rtop + (rheight/2))), text_size, text_color, True)
        return False


def level_info(current_level:int)->None:#Kimi
    """Affiche les infos du level"""
    global level_color, difficulty
    pg.draw.rect(surface, LIGHT_GREY, (0, 0, 1200*SCALE, 90*SCALE)) # Bandeau supérieur
    
    if current_level <= 10 :
        difficulty = "Facile"
        level_color = GREEN
    elif current_level <= 20 :
        difficulty = "Normal"
        level_color = YELLOW
    elif current_level <= 30 :
        difficulty = "Difficile"
        level_color = ORANGE
    elif current_level <= 40 :
        difficulty = "Expert"
        level_color = RED
    elif current_level <= 49 :
        difficulty = "Maître"
        level_color = PURPLE
    else :
        difficulty = "Impossible"
        level_color = BLACK
        
    nom = levels_data[current_level-1]['nom']
    f_brute = levels_data[current_level-1]['formule brute']
    print_txt("Niveau " + str(current_level), (1050, 30), 35, BLACK, True)
    print_txt(difficulty, (1050, 65), 30, level_color, True)
    print_txt(str(nom), (600, 30), 35, BLACK, True)
    print_txt(str(f_brute), (600, 65), 30, BLACK, True)


def create_atoms(current_level:int)->list:#victor+kimi
    """Crée chaque atome"""
    atom_list = levels_data[current_level-1]['atomes']
    atom_id_list = ['']*len(atom_list)
    shuffle(atom_list)
    #print(atom_list)
    for i in range(len(atom_list)) :
        valence = find_in_dlist(atoms_data, "symbole", atom_list[i])["valence"]
        atom_id_list[i]={"id" : int(i+1),"name" : str(atom_list[i]), "pos" : ((600 + cos(radians(360/len(atom_list)*i))*350), (450 + sin(radians(360/len(atom_list)*i))*250)), "links": []}
    #print(atom_id_list)
    return atom_id_list


def detect_win() -> bool : # Par Victor
    '''Détecte si le joueur a gagné et renvoie un booléen correspondant
    Détection simple : on vérifie juste que tous les atomes ont le bon nombre de liaisons
    Puis complexe : tous les atomes doivent faire partie de la même chaîne'''
    
    win = True
    # Ouais bon en fait c'est plus une détection de défaite
    
    for a in atoms :
        nb_links = 0
        for i in a["links"] :
            nb_links += i[1] # Compte le nombre de liens de l'atome a
            
        #print(a["name"], nb_links)
        #print("valence", find_in_dlist(atoms_data, "symbole", a["name"])["valence"])
        
        if nb_links != find_in_dlist(atoms_data, "symbole", a["name"])["valence"] : # Quand le nombre de liaisons n'est pas le max
            win = False
    
    
    if win :
        n = len(atoms)
        all_links = [[False for i in range(n)] for i in range(n)]
    
        for i in range(n):
            all_links[i][i] = True
            linked_to_i = get_links_ids(i+1)
            for l in linked_to_i:
                all_links[i][l-1] = True
                all_links[l-1][i] = True
    
        looping = True
        counter = 0
        while looping :
            counter += 1
            for i in range(n):
                for j in range(n):
                    if all_links[i][j] :
                        for k in range(n) :
                            if all_links[j][k] :
                                all_links[i][k] = True
                                all_links[k][i] = True
        
            all_true = True
            for i in range(n):
                for j in range(n):
                    if all_links[i][j] :
                        all_true = False
                    
            if all_true or counter >= n :
                looping = False
        
    
    
        for i in range(n):
            for j in range(n):
                if not all_links[i][j] :
                    win = False
            
    #print(all_links)
    
    
    return win


def get_links_ids(a_id : int) -> list[int] : # Par Victor
    '''Renvoie la liste des id des atomes liés à l'atome ciblé'''
    #print(a_id)
    links = find_in_dlist(atoms, "id", a_id)["links"]
    l = [0 for i in range(len(links))]
    for i in range(len(links)) :
        l[i] = links[i][0]
    return l

 
def background(color:tuple) -> None : # Par Victor amélioré par Kimi
    '''Dessine un arrière plan stylé'''
    if bg_type != "disabled" :
        if bg_type == "normal" :
            for i in range(6) :
                modifier = 0.2 + i/15
                radius = 350 + i*80
                pt1 = (((600 + cos(radians(90+tick*modifier))*radius), (450 + sin(radians(90+tick*modifier))*radius)))
                pt2 = (((600 + cos(radians(180+tick*modifier))*radius), (450 + sin(radians(180+tick*modifier))*radius)))
                pt3 = (((600 + cos(radians(270+tick*modifier))*radius), (450 + sin(radians(270+tick*modifier))*radius)))
                pt4 = (((600 + cos(radians(tick*modifier))*radius), (450 + sin(radians(tick*modifier))*radius)))
                r=min(color[0]+i*20,255)
                g=min(color[1]+i*20,255)
                b=min(color[2]+i*20,255)
                pg.draw.lines(surface, (r,g,b), True, [scaling(pt1), scaling(pt2), scaling(pt3), scaling(pt4)], int(5*SCALE))
                
        elif bg_type == "circles" :
            for i in range(6) :
                radius = 50 + i*100 + sin(tick/20 + i*2)*5
                r=min(color[0]+i*20,255)
                g=min(color[1]+i*20,255)
                b=min(color[2]+i*20,255)
                pg.draw.circle(surface, (r,g,b), scaling((600, 400)), radius, int(5*SCALE))
                
        elif bg_type == "triangles" :
            for i in range(5) :
                modifier = 0.2 + i/15
                radius = 350 + i*90
                pt1 = (((600 + cos(radians(tick*modifier))*radius), (450 + sin(radians(tick*modifier))*radius)))
                pt2 = (((600 + cos(radians(120+tick*modifier))*radius), (450 + sin(radians(120+tick*modifier))*radius)))
                pt3 = (((600 + cos(radians(240+tick*modifier))*radius), (450 + sin(radians(240+tick*modifier))*radius)))
                r=min(color[0]+i*20,255)
                g=min(color[1]+i*20,255)
                b=min(color[2]+i*20,255)
                pg.draw.lines(surface, (r,g,b), True, [scaling(pt1), scaling(pt2), scaling(pt3)], int(5*SCALE))




   


# -----<===== BOUCLE PRINCIPALE =====>-----

# Par Victor

menu = "main"

clock = pg.time.Clock()

running = True

while running :
    
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False   # Quitte la boucle quand l'évènement QUIT est détecté
    
    
    render()
    pg.display.flip()
    
    
    # ----- TESTS -----
    
    #print(menu)
    #print(pg.mouse.get_pressed())
    #print(levels_data[0]['atomes'][0])
    
    # -----------------
    
    
    tick += 1 # + 1 ticks par frame (60 par seconde)

    clock.tick(60) # Met le FPS à 60
    

print("Fermeture de la fenêtre...")

pg.font.quit()
pg.display.quit()
pg.quit()

print("----------------------------------------")

print("Merci d'avoir joué à notre jeu ! À bientôt pour plus de chimie ;)")





















