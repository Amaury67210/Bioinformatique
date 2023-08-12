import os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtGui import QTextCursor

from worker import Worker


# TODO REMOVE THIS CLASS, all is useless now
class TreeWidget(QtWidgets.QTreeWidget):
    """
    La classe tree widget permet d'afficher les fichiers à gauche.
    Une tree widget organise ses éléments en arbre. Attention, les éléments sont organisés selon leur numéro dinodes
    et non leur nom. Ainsi, deux fichiers peuvent avoir le meme nom meme sil sont frères dans l'arbre.
    A noter que trier les éléments avec la méthode de trie modifie les numéros dinodes... C assez perturbant,
    j'essaie de voir si y a pas moyen de les conserver.
    Je crois quil y a un moyen de trouver un fichier par son nom mais jai pas trop compris encore. Sinon on peut
    faire un hmap pour conserver les infos.

    Il faudra écrire une fonction qui permet de charger la filetree à partir de nos fichier déjà traités.
    Ainsi, si l'organisme Bactérie/Osef/reosef/ornagisme a déjà été traité, il faudra lajouter dans la filetree
    dès linitialisation ! Il faut donc lire récursivement larborescence. Une autre solution possible et
    plus intelligente est de gérer un fichier toto qui contiendra larborescence des organismes présent sur l'OS.
    Cela suppose que ce fichier possède ne structure -> fichier binaire ? Sinon plus simple, faire une bdd.
    """

    def __init__(self, central_widget, gridLayout):
        super().__init__()
        # Le thread pour init_arbo, si une autre fonction souhaite profiter de ce thread, il faut dabord vérifier
        # si le thread n'est pas déjà utilisé (avec isRunning)
        self.worker = Worker()
        self.thread = QThread()

        self.lastClickedItem = QtWidgets.QTreeWidgetItem()
        # on déclare mnt un tree widget -> elle contiendra l'arborescence des fichiers
        self.treeWidget = QtWidgets.QTreeWidget(central_widget)
        # La police est la facon dont la widget est censé réagir quand la mainWindow est resize.
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setAnimated(True)  # petit effet sympa quand on déroule les fichiers
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.setAlternatingRowColors(True)

        # on place la tree view en 0,0. Il fait 4 de hauteurs et 1 de largeur
        #gridLayout.addWidget(self.treeWidget, 0, 0, 4, 1)
        _translate = QtCore.QCoreApplication.translate
        self.treeWidget.headerItem().setText(0,
                                             _translate("MainWindow", "Arborescence"))  # on met les noms des columnes
        #self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Dernière modif"))
        self.treeWidget.setColumnWidth(0, 150)
        # self.treeWidget.headerItem().setSizeHint(1, QSize(1000, 20))
        # self.treeWidget.header().setSectionResizeMode(0, QHeaderView.Interactive)
        # self.treeWidget.header().setSectionResizeMode(1, QHeaderView.Fixed)
        # self.treeWidget.setColumnWidth(0,100)
        # self.treeWidget.header().setSectionResizeMode(QHeaderView.Stretch)


    def connectItemsToTextArea(self, regionBox, textArea):
        # connecte tous les items a une fonction.
        self.treeWidget.itemClicked.connect(
            lambda: self.printOrganisme(self.treeWidget.currentItem(), regionBox, textArea))
        self.treeWidget.itemActivated.connect(
            lambda: self.printOrganisme(self.treeWidget.currentItem(), regionBox, textArea))

    def getLastClickedItem(self):
        return self.lastClickedItem

    # TODO

    def printOrganisme(self, item: QtWidgets.QTreeWidgetItem, regionBox: QtWidgets.QComboBox, textArea):
        """
        Cette fonction doit afficher le texte dans le widget "information". Elle est DEJA connectée aux items.
        Modifier cette fonction a donc des effets immédiats, si on sélectionne un item, cette fonction est automatiquement
        appelée.
        :param regionBox:
        :param textArea : la zoone de texte où on affiche les données.
        :param item: litem sélectionner par lutilisteur
        Ici path contient à la fin le chemin compliqué. Attention, le prof est sur Windows et cette fonction
        ne fonctionnera pas sur Windows -> utiliser join
        :return:
        """

        path = ""
        item_copy = item

        if item_copy.childCount() == 0: # on vérifie que notre item est un noeud
            while item_copy:
                path = os.path.join(item_copy.text(0), path)
                item_copy = item_copy.parent()

            file_path = os.path.join(path, regionBox.currentText() + ".txt")

            if os.path.exists(file_path):
                with open(file_path, "r", errors="ignore") as f:
                    textArea.clear()
                    textArea.setAlignment(Qt.AlignCenter)
                    """
                    de base, TextArea est une zone de texte éditable avec un curseur. Là, c en lecture seule mais 
                    le curseur est toujours là (invisible). Donc setAlignement ne fait que changer l'alignement à 
                    partir de la position actuelle du curseur
                    """
                    textArea.append("Organisme : " + item.text(0) + "\n")
                    textArea.setAlignment(Qt.AlignLeft)
                    textArea.append(f.read())
                    textArea.moveCursor(QTextCursor.Start)
                    # f.close() Si le fichier est ouvert avec with, il est fermé automatiquement à la sortie du with

            else:
                textArea.clear()
                textArea.setAlignment(Qt.AlignCenter)
                textArea.append("Organisme : " + item.text(0) + "\n")
                textArea.setAlignment(Qt.AlignLeft)
                textArea.append("La zone " + regionBox.currentText() + " est indisponible pour cet organisme")

            # C'est important de garder le dernier item clické parce que qt ne le fait pas. En fait qt donne le current
            # item et envoie un signal quand on clique sur un item
            # On en aura besoin pour afficher la région sélectionné et connecter les SIGNALS AND SLOTS SANDIE
            self.lastClickedItem = item  # NE PAS SUPPRIMER CETTE LIGNE

