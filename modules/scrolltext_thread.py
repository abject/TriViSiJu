#!/usr/bin/env python
#-*-coding: utf8 -*-

import pygtk
pygtk.require("2.0")
import gtk
import time
import gobject
import subprocess
import threading
import os

class ScrollBuffer(threading.Thread):
    """ Classe :threading.Thread

    Permet une gestion plus fine de gtk.TextBuffer

    - root      : Classe gtk.ScrolledWindow parente (permet le 'défilement')
    - buffer    : Classe gtk.TextBuffer
    - lines     : List de lines à faire défiler. (defaut: [""])
    - n         : Entier à partir duquel on lit la list 'lines'. (defaut: 0)
    - speed     : Vitesse de défilement (temps entre chaque ligne en seconde : (defaut 0.1))
    """

    def __init__(self, root, buffer, lines=[""], n=0, speed=0.1):
        """ Initialise la classe
        """
        ## Permet de remplacer les méthodes de la classe parente (ici threading.Thread qui contient une méthode run)
        super(ScrollBuffer, self).__init__()

        ## Charge les variables
        self.root = root
        self.buffer = buffer
        self.continuer = True # Variable contrôlant le thread (si False, sort de la boucle infinie)
        self.lines = lines
        self.n = n
        self.speed = speed
        if self.n <= len(self.lines):
            self.line = self.lines[self.n]
        else:
            self.line = ""

    def update_buffer(self, texte):
        """ Met à jour le buffer

        - texte : Texte à mettre dans le buffer (remplace l'ancien texte)
        """
        ## Met à jour le buffer
        self.buffer.set_text(texte)

        ## Fait défiler le text
        adj = self.root.get_vadjustment()
        adj.set_value( adj.upper - adj.page_size )
        
        ## Retourne False pour gobject (???)
        return False

    def run(self):
        """ Lance le Thread (ré-écriture de la méthode inhérente à threading.Thread)
        """
        ## Boucle 'infinie'
        while self.continuer:
            ## Met à jour le buffer
            gobject.idle_add(self.update_buffer, self.line)
            
            ## Incrémente n (lecteur de ligne dans le fichier)
            self.n = self.n + 1
            if self.n >= len(self.lines):
                self.n = 0
                ## Pour le moment il reste un saut quand le bufer a plus de 100 linges
                self.line = "\n".join(self.line.split('\n')[-100:])
            
            ## Ajout de la ligne suivante
            self.line = self.line + self.lines[self.n]
            
            ## Attend avant la ligne suivante
            time.sleep(self.speed)

    def set_speed(self, speed):
        """ Change la vitesse de défilement

        - speed : Délai entre l'affichage de chaque ligne en seconde
        """
        self.speed = speed

    def quit(self):
        """ Quitte proprement le thread
        """
        ## Permet de sortir de la boucle while infinie
        self.continuer = False

        ## Renvoie self.n afin de recommencer au même endroit
        return self.n


class ScrollText(gtk.ScrolledWindow):
    """ Classe permettant de faire défiler du text indéfiniment
    """
    def __init__(self, filename=os.path.join(os.getcwd(), __file__.replace('.pyc', '.py')), speed=0.1):
        """ Initialisation de la classe
        
        - filename : Fichier à faire défiler (defaut le code lui même)
        - speed    : Vitesse de défilement (temps entre chaque ligne en seconde : (defaut 0.1))
        """
        ## Initialisation des variables
        self.filename = filename    # Fichier à faire défiler
        self.launch = False         # Permet de contrôler si le texte défile
        self.buffertext = 0         # Position de lecture lors de l'arrêt du défilement
        self.speed = speed          # Vitesse de défilement

        ## Initialisation de gtk.ScrolledWindow
        gtk.ScrolledWindow.__init__(self)
        
        ## Initialisation de gtk.ScrolledWindow pour contenir un gtk.TextView
        self.get_vscrollbar().set_child_visible(False) # Cache la barre verticale
        self.get_hscrollbar().set_child_visible(False) # Cache la barre horizontale
        
        ## Initialisation de gtk.TextView()
        self.textview = gtk.TextView()
        self.textview.set_editable(False)       # TextView inéditable
        self.textview.set_cursor_visible(False) # Curseur invible
        
        ## Récupération de gtk.Buffer
        self.buffer = self.textview.get_buffer()
        
        ## Ajout de TextView à ScrolledWindow
        self.add(self.textview)

        ## Init ScrollBuffer
        self.scroll_buffer = ScrollBuffer(self, self.buffer) # Necessaire pour pouvoir connecter la fonction set_speed

        
    def loadfile(self, *parent):
        """ Charge un fichier et fait défiler son contenu
        """
        ## Lit le fichier à faire défiler
        f = open(self.filename, 'r')
        lines = f.readlines()
        f.close()

        ## Revnoie le contenu du fichier
        return lines

    def scroll(self, *parent):
        """ Fait défiler le text
        """
        if not self.launch:
            lines = self.loadfile()
            ## Reset ScrollBuffer
            self.scroll_buffer = ScrollBuffer(self, self.buffer, lines=lines, n=self.buffertext, speed=self.speed)
            ## Charge les lignes à faire défiler
            self.scroll_buffer.lines = lines
            ## Lance le défilement
            self.scroll_buffer.start()
            self.launch = True
        else:
            ## Stop le défilement et du coup le thread et récupère le numéro de ligne actuel
            self.buffertext = self.scroll_buffer.quit()
            self.launch = False
        
    def set_speed(self, speed):
        """ Change la vitesse de défilement

        - speed : Délai entre l'affichage de chaque ligne en seconde
        """
        self.speed = speed
        self.scroll_buffer.set_speed(self.speed)

    def quit(self):
        """ Quitte proprement
        """
        if self.launch:
            self.scroll()

class ScrollTextBox(gtk.VBox):
    """ Conteneur pour la classe ScrollText (gtk.VBox)
        
    - filename : Fichier à faire défiler (defaut le code lui même)
    - speed    : Vitesse de défilement (temps entre chaque ligne en seconde : (defaut 0.1))
    """

    def __init__(self, filename=os.path.join(os.getcwd(), __file__.replace('.pyc', '.py')), speed=0.1, forcebutton=True):
        """ Initialisation de la classe
        """
        ## Inititalisation de la class gtk.VBox (conteneur)
        gtk.VBox.__init__(self)

        ## Affichage optionnel des bouttons
        if forcebutton:
            ## HBox avec le boutton de chargement
            load = gtk.Button(stock=("gtk-media-play"))
            self.pack_start(load, True, True, 0)

            ## HBox (Label+HScale | Boutton)
            hbox = gtk.HBox()

            ## VBox (Label - HScale)
            vbox = gtk.VBox()

            ## Label
            label = gtk.Label("Vitesse en ms")
            vbox.pack_start(label, True, True, 0)

            ## Ajustement
            adj = gtk.Adjustment(1.00, 0.01, 10.0, 0.01, 0.1, 1.0)
            
            ## HScale
            hscale = gtk.HScale(adj)
            hscale.set_digits(2)                # Change la précision (defaut: 1)
            hscale.set_value_pos(gtk.POS_RIGHT) # Change la posisition de la valeur (POS_RIGHT, POS_TOP, POS_BOTTOM, POS_LEFT)
            vbox.pack_start(hscale, True, True, 0)

            ## Pack vbox
            hbox.pack_start(vbox, True, True, 0)

            ## Boutton ouvrir
            boutton = gtk.Button(stock=("gtk-open"))
            hbox.pack_start(boutton, True, True, 0)

            ## Pack hbox
            self.pack_start(hbox, True, True, 0)
        
        ## Charge ScrollText
        self.scrolltext = ScrollText()
        self.pack_start(self.scrolltext, True, True, 0)

        ## Connexion
        if forcebutton:
            ## Défilement Start/stop
            load.connect("clicked", self.scroll)
            ## Récupération de la vitesse
            adj.connect("value_changed", lambda w: self.update(hscale))
            ## Ouvrir un nouveau fichier
            boutton.connect("clicked", self.open)

    def scroll(self, *parent):
        """ Lance le défilement
        """
        self.scrolltext.scroll()

    def open(self, parent):
        """ Ouvrir un fichier grâce à un explorateur de fichier
        """
        dialog = gtk.FileChooserDialog("Choisit un fichier", gtk.Window(), gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.connect("destroy", lambda w: dialog.destroy())
        statut = dialog.run()
        if statut == gtk.RESPONSE_OK:
            self.set_filename(dialog.get_filename().replace(' ', '\ '))
        dialog.destroy()

    def update(self, hscale):
        """ Met à jour la valeur de la vitesse gràce à HScale barre

        - hscale : gtk.HScale instance
        """
        self.set_speed(hscale.get_value()/10.)

    def set_speed(self, speed):
        """ Change la vitesse de défilement (pourra être connectée au shell)

        - speed : Délai entre l'affichage de chaque ligne en seconde
        """
        self.scrolltext.set_speed(speed)

    def set_filename(self, filename):
        """ Permet de changer le fichier à faire défiler

        - filename : Nom du fichier à lire
        """
        ## Arrêt du défilement s'il est lancé
        self.quit()
        self.scrolltext.filename = filename
        self.buffertext = 0
        self.scroll()

    def quit(self, *parent):
        """ Quitte proprement
        """
        ## Arrêt du défilement et du thread associé
        self.scrolltext.quit()
 

class RootWindows():
    """ Fenêtre principale pour tester ScrollText
    """
    def __init__(self):
        """ Initialise la fenêtre et chareg ScrollText
        """
        ## Charge gobject
        gobject.threads_init()

        ## Créer la fenêtre principale
        self.root = gtk.Window()
        self.root.set_title(__file__)
        self.root.set_default_size(500, 400)
        self.root.set_position(gtk.WIN_POS_CENTER)
        self.root.connect("destroy", self.quit)
        
        ## ScrollTextBox
        self.scrolltextbox = ScrollTextBox()
        
        ## On attache le tout à root
        self.root.add(self.scrolltextbox)
        
        ## On affiche tout
        self.root.show_all()

       
    def quit(self, *parent):
        """ Fonction qui permet de quitter proprement
        """
        ## Ferme ScrollTextBox
        self.scrolltextbox.quit()

        ## On quitte l'application
        gtk.main_quit()
        
    def loop(self):
        """ Boucle principale
        """
        gtk.main()

if __name__ == "__main__":
    r = RootWindows()
    r.loop()
