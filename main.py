#!/usr/bin/env python
# *-* coding:utf-8 *-*

""" TriViSiJu: Graphical interface for the AstroJeune Festival
    
	Copyright (C) 2012  Jules DAVID, Tristan GREGOIRE, Simon NICOLAS and Vincent PRAT

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import pygtk
pygtk.require("2.0")
import gtk
from modules import *
from fonction import conf2dict, str2bool
import time
import os
import ConfigParser
import sys
import argparse

class MainWindow(gtk.Window):
    """ Fenêtre principale
    """

    def __init__(self, **kwarg):
        """ Constructeur de la fenêtre principale
        """
        ## Initialise la fenêtre
        gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
        self.set_title("TriViSiJu")
        self.set_default_size(800,600)
        self.set_position(gtk.WIN_POS_CENTER)

        ## Table
        self.grid = gtk.Table(rows=4, columns=7, homogeneous=True)
        rightBox = gtk.VBox(homogeneous=False,spacing=0)

        # Vidéos
        ## Charge la classe Player
        self.screen1 = PlayerFrame(self, 1, quitb=kwarg['quitb'], forcebutton=kwarg['forcebutton'])

        ## Compte à rebours
        self.countdown = countdownBox(forcebutton=kwarg['forcebutton'])
        self.countdown.setStartTime(h=0,m=0,s=48,cs=0)

        ## Texte crypté
        self.scrolltextbox = ScrollTextBox(forcebutton=kwarg['forcebutton'], speed=kwarg['speed'], crypt=kwarg['crypt'])

        ## Prompt
        self.prompt = promptBox()
        self.prompt.connect("fullscreen", self.on_fullscreen)
        self.prompt.connect("quit", self.quit)

        ## Caractéristiques techniques
        text6 = gtk.Label("<b>Panneau haut droite</b>\nCaractéristiques techniques")
        text6.set_use_markup(True)

        ## Liste des équipes
        self.teamBox = teamBox()
        self.teamBox.connect("message",self.prompt.onExternalInsert)
        self.prompt.connect("add-team", self.teamBox.addTeam)
        
        ## Affichage des textes provisoires
        rightBox.pack_start(text6,True,True)

        ## Table
        self.grid.attach(self.screen1,   0, 4, 0, 2, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)
        self.grid.attach(self.teamBox,   0, 2, 2, 4, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)
        self.grid.attach(rightBox,       2, 4, 2, 4, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)
        self.grid.attach(self.countdown, 4, 7, 0, 1, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)
        self.grid.attach(self.scrolltextbox, 4, 7, 1, 3, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)
        self.grid.attach(self.prompt, 4, 7, 3, 4, xoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK, yoptions=gtk.EXPAND|gtk.FILL|gtk.SHRINK)

        ## Ajout de self.grid sur la fenêtre principale
        self.add(self.grid)
        
        ## Affichage général
        self.show_all()
        
        ## Envoie de l'id à mplayer après l'avoir affiché
        self.screen1.Screen.setwid(long(self.screen1.Screen.get_id()))
        
        ## Charge la/les vidéo(s)
        self.loadmovie(kwarg['videopath1'], 1)

        ## Lance le timer et le défilement
        #if not kwarg['forcebutton']:
            # Lance le timer
            #self.countdown.start()
            # Défilement
            #self.scrolltextbox.scroll()
        
        ## Connexion de destroy à la fonction quit
        self.connect("destroy", self.quit)

        # Connexion du signal de changement d'état de la fenêtre
        self.connect("window-state-event", self.onStateChange)

    def on_fullscreen(self, sender):
        """ Slot de mise en plein écran """
        if self.full:
            self.unfullscreen()
        else:
            self.fullscreen()

    def onStateChange(self, window, event):
        """ Méthode appelée quand l'état de la fenêtre change
        """
        if event.new_window_state and gtk.gdk.WINDOW_STATE_FULLSCREEN:
            self.full = True
        else:
            self.full = False

    def loadmovie(self, videoPath, id):
        """ Charge la video si elle existe
        """
        ## Test videoPath
        if os.path.isfile(videoPath):
            exec("self.screen%s.Screen.loadfile('%s')"%(id, videoPath.replace(' ', '\ ')))

    def quit(self, *parent):
        """ Fonction quitter
        
        Tue proprement l'application root
        """
        ## Envoie le signal à mplayer
        self.screen1.Screen.quit()
        ## Envoie le signal à ScrollTextBox
        self.scrolltextbox.quit()
        ## Attend que mplayer se soit éteint
        time.sleep(0.1)
        ## Tue l'application root
        gtk.main_quit()

if __name__=="__main__":
    ## Licence
    licence = """
    TriViSiJu  Copyright (C) 2012 Jules DAVID, Tristan GREGOIRE, Simon NICOLAS and Vincent PRAT
    This program comes with ABSOLUTELY NO WARRANTY; for details type `./main.py -h'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `./main.py -h' for details.
    """
    print licence

    ## Descrition
    description = """ Application Grand Jeu : TriViSiJu
    
    Développé pour le Festival AstroJeune 2012
    """
    class Arg(object):
        """ Permet de renvoyer les arguments du parser sans utiliser de liste
        Voir http://docs.python.org/library/argparse.html#argparse.Namespace
        """
        pass
    
    ## Parse  les arguments
    args = Arg() # Conteneur pour les arguments
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-c', '--config', metavar='FILE', type=str,\
                        default=os.path.join(os.getcwd(), 'TriViSiJu.cfg'), action='store',\
                        help="Fichier de configuration")
    parser.add_argument('-s', '--section', metavar='STRING', type=str,\
                        default='Default', action='store',\
                        help="Section de paramètres à charger")
    parser.parse_args(sys.argv[1:], namespace=args) # Parse les arguments dans la classe conteneur
    
    ## Charge les paramètres
    if args.config != None and os.path.isfile(args.config):
        config = ConfigParser.RawConfigParser()
        config.read(args.config)
        if 'section' in dir(args) and config.has_section(args.section):
            kwarg = conf2dict(config.items(args.section))
        else:
            print "ATTENTION : la secion '%s' n'existe pas dans le fichier de configuration '%s'"%(args.section, args.config)
            kwarg = conf2dict(config.items('Default'))

    
    ## Convertit les string True/False en booléen
    for key, val in kwarg.iteritems():
        if val in ['True', 'False', 'true', 'false']:
            kwarg[key] = str2bool(val)
        else:
            try:
                kwarg[key] = float(val)
            except ValueError:
                pass

    ## Charge gobject (Important pour ScrollTextBox
    gobject.threads_init()
    
    ## arg et kwarg
    MainWindow(**kwarg)
    gtk.main()
