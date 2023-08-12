# -*- coding: utf-8 -*-

import os
import shutil
# Form implementation generated from reading ui file 'gui_designer2.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!
# lien du tuto pour les thread : https://realpython.com/python-pyqt-qthread/
from datetime import datetime
from functools import partial
from pathlib import Path

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtWidgets import QFileDialog

from worker import Worker


def paletteDark(app):
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(40, 40, 40))
    palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ToolTipBase, QColor(40, 40, 40))
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)


def paletteWhite(app):
    palette = QPalette()
    app.setPalette(palette)


class ToolBar(QtWidgets.QToolBar):
    """
    La ToolBar est la barre supérieur en dessous de la barre de menu où il y a écrit "recharger".
    En général on met des icônes mais pour l'instant, on mettra du texte.
    """

    def __init__(self, main_window):
        """
        On initialise la ToolBar. Comme la ToolBar fait partie de la mainWindow, on en a besoin pour la suite
        :param main_window:
        """
        super(ToolBar, self).__init__()  # on appelle le constructeur de la classe mère
        self.region = main_window.combobox
        self.tree = main_window.tree.treeWidget
        self.thread = QThread()
        self.textEdit = main_window.textEdit
        _translate = QtCore.QCoreApplication.translate
        self.toolBar = QtWidgets.QToolBar(main_window)  # on crée une instance de toolbar
        self.toolBar.setObjectName("toolBar")  # on lui donne un nom. Je crois que c'est une sorte d'identifiant
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        main_window.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)  # on ajoute la barre a notre window

        self.recharger = QtWidgets.QAction(main_window)  # on ajoute une action possible, ici recharger
        self.autre = QtWidgets.QAction(main_window)  # une autre

        _translate = QtCore.QCoreApplication.translate
        # pour la tool bar
        self.recharger.setObjectName(
            "recharger")  # on donne des noms a nos actions. ATTENTION, ce ne sont pas les noms afficher !
        self.recharger.setEnabled(False)
        self.autre.setVisible(False)
        self.autre.setObjectName("autre")

        self.toolBar.addAction(self.recharger)  # on ajoute les actions à notre toolbar
        self.toolBar.addAction(self.autre)

        self.autre.setText(_translate("MainWindow", "Autre"))  # on met le texte à afficher sur la toolbar.
        self.recharger.setText(_translate("MainWindow", "Fetch_Parse_All"))

        self.progress_bar = main_window.progressBar_2

    def setDark(self, app):
        pass

    def init_thread_worker(self):
        self.thread = QThread()

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)

    def set_max_bar(self, max):
        self.progress_bar.setMaximum(max)

    def hide_bar(self):
        self.progress_bar.setHidden(True)

    def show_bar(self):
        self.progress_bar.setHidden(False)

    def connect_recharger(self, tree):
        if not self.thread.isRunning():
            worker = Worker()
            # Move worker to the thread
            worker.moveToThread(self.thread)
            # Connect signals and slots
            self.thread.started.connect(partial(worker.update_tree, ".cache_Genbank", self.region))  # on connecte le signal started du thread a un slot


            worker.hide_bar.connect(self.hide_bar)
            worker.set_max_bar.connect(self.set_max_bar)
            worker.show_bar.connect(self.show_bar)
            worker.progress.connect(self.update_progress_bar)
            worker.checked_itm.connect(self.checked_itm)

            worker.print_log.connect(self.print_log)
            worker.add_log.connect(self.add_log)
            worker.clear_log.connect(self.clear_log)

            worker.finished.connect(self.thread.quit)
            # worker.finished.connect(self.thread.deleteLater)
            # worker.finished.connect(worker.deleteLater)
            # self.thread.finished.connect(self.init_thread_worker)
            # Step 6: Start the thread
            self.thread.start()
        else:
            print("Thread is runnning")

    def print_log(self, str):
        self.textEdit.setText(str)

    def add_log(self, log):
        self.textEdit.append(log)

    def clear_log(self):
        self.textEdit.clear()

    def checked_itm(self, item_path :str):
        print("path :", item_path)
        files = Path(item_path).parts  # donne un tuple
        #print("files :",files)
        idx_f = 1  # on prend pas la racine je crois
    #    print("files :", files, "idx_f :", idx_f)
        existe, item, idx_f = self.parcourt_tree(self.tree.invisibleRootItem(), files, idx_f)
        if not existe:
            while idx_f < len(files):
                # ajoute un enfant à item qui a comme texte files[idx_f]
                child = QtWidgets.QtTreeWidgetItem(item, files[idx_f])
                item = child
                idx_f += 1
            item.setIcon(0, QIcon(":/check"))

        # On cherche quel enfant match le dossier/fichier si il y en a un (True)
        # Marche pas s'il faut insérer le noeud au milieu et pas en bout
    def parcourt_tree(self, item: QtWidgets.QTreeWidgetItem, files, idx_f):
        # LES ARGUMENTS DANS LES FONCTIONS DE LA CLASSE WORKER SERONT BIENTÖT  TOUS SUPPRIMES, IL FAUDRA UTILISER LES SIGNAUX POUR METTRE A JOUR LINTERFACE
        nb_children = item.childCount()
        if idx_f == len(files):  # cas d'arrêt : le fichier existe
            item.setIcon(0, QIcon(":/check"))
            return True, item, idx_f  # idx_f et item servent à rien là
        elif nb_children == 0:  # cas d'arret : il faut créer les dossiers restant
            return False, item, idx_f
        else: # on continue de parcourir
            for i in range(nb_children):
                child = item.child(i)
                if child.text(0) == files[idx_f]:
                    idx_f += 1
                    #print("child :", child.text(0), "files :", files, "idx_f :", idx_f)
                    return self.parcourt_tree(child, files, idx_f)


# TODO Remove, useless
class Label(QtWidgets.QLabel):
    # cette classe est utilisé pour afficher logs et informations
    def __init__(self, central_widget, label):
        """
        :param central_widget: La widget centrale sur laquelle on positionne nos élément.
        :param label: Le nom du label à afficher
        """
        super().__init__()
        self.name = label
        # on appelle le constructeur de label. Son widget parent sera la grid. La grid contient donc le label
        self.label = QtWidgets.QLabel(central_widget)
        # attention , le nom ici ,'est pas le nom affiché. Son nom affiché est géré après -> "logs"
        self.label.setObjectName(label)

    def set_label(self, grid, i, j, h, w):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", self.name))  # on lui donne le vrai nom à afficher
        grid.addWidget(self.label, i, j, h, w, QtCore.Qt.AlignHCenter)  # on le place que la grid


# TODO Remove, useless
class MenuBar(QtWidgets.QMenuBar):
    def __init__(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        super().__init__()
        # on ajoute une barre de menus ("file, importer...)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 895, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        # on déclare le premier menu. Ici c'est "file"
        self.menuFile = self.menubar.addMenu("&menufile")
        # meme chose pour menu affichage
        self.menuAffichage = self.menubar.addMenu('&Affichage')

        # Dark mode -> sous section de affichage
        self.actionDark_Mode = QtWidgets.QAction(MainWindow)
        self.actionDark_Mode.setCheckable(True)
        self.actionDark_Mode.setObjectName("actionDark_Mode")
        self.actionDark_Mode.setText(_translate("MainWindow", "Dark Mode"))

        # Importer
        self.actionImporter = QtWidgets.QAction(MainWindow)
        self.actionImporter.setObjectName("actionImporter")

        self.actionImporter2 = QtWidgets.QAction(MainWindow)
        self.actionImporter2.setObjectName("actionImporter2")

        # sous menus
        self.menuFile.addAction(self.actionImporter)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionImporter2)
        self.menuAffichage.addAction(self.actionDark_Mode)

        # on met les noms
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuAffichage.setTitle(_translate("MainWindow", "Affichage"))
        self.actionImporter.setText(_translate("MainWindow", "Exporter"))
        self.actionImporter2.setText(_translate("MainWindow", "Vider le cache"))

        self.actionImporter.triggered.connect(self.open_file_dialog)
        self.actionImporter2.triggered.connect(self.empty_cache)

    def setDarkMenuBar(self, app):
        self.actionDark_Mode.triggered.connect(lambda: self.setDarkWhitePalette(app))

    def open_file_dialog(self):
        # 'C:\\'
        dir = QFileDialog.getExistingDirectory(self, 'Select a folder', '/home', QFileDialog.ShowDirsOnly )
        copy_path = os.path.join(dir, "../Genbank")
        if os.path.exists(copy_path) : 
            shutil.rmtree(copy_path)
        try :
            shutil.copytree("../Genbank", os.path.join(dir, "Genbank"))
        except : 
            print("Error in open_file_dialog : couldn't export Genbank")
        print(dir)

    def setDarkWhitePalette(self, app):
            if self.actionDark_Mode.isChecked():
                paletteDark(app)
            else:
                paletteWhite(app)

    def empty_cache(self):
        try:
            shutil.rmtree("../.cache_Genbank")
        except:
            print ("error: could not clean cache.")
        pass


# TODO Remove, useless
class TextBrowser(QtWidgets.QTextBrowser):
    """
    Un container qui peut contein du texte. Bon je suis pas sur que ce soit très judicieux de prendre celui-là mais bon
    """

    def __init__(self, central_widget, name_object):
        super().__init__()
        self.textBrowser = QtWidgets.QTextBrowser(central_widget)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)

        self.textBrowser.setObjectName(name_object)

        self.name_object = name_object

    def set_text_browser(self, grid, i, j, h, w):
        grid.addWidget(self.textBrowser, i, j, h, w)


# TODO Remove, useless
class TextArea(QtWidgets.QTextEdit):
    def __init__(self, central_widget):
        super().__init__()
        self.textArea = QtWidgets.QTextEdit(central_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textArea.sizePolicy().hasHeightForWidth())
        self.textArea.setSizePolicy(sizePolicy)
        self.textArea.setReadOnly(True)

    def set_text_area(self, grid, i, j, h, w):
        grid.addWidget(self.textArea, i, j, h, w)


# TODO Remove, useless
class Button(QtWidgets.QPushButton):
    def __init__(self, parent, progressBar, logText):
        super().__init__()
        self.progressBar = progressBar
        self.worker = Worker()
        self.thread = QThread()
        self.button = QtWidgets.QPushButton(parent)
        self.dialog = QtWidgets.QDialog()
        self.logText = logText
        self.currentItem = QtWidgets .QTreeWidgetItem

    def connect(self, item, combobox, progressBar: QtWidgets.QProgressBar):
        self.currentItem = item
        # NE PAS IMPLEMENTER
        # if not self.thread.isRunning():
        # on recrée le thread
        thread = MyThread(self.dialog)
        thread.setObjectName("worker" + str(datetime.now().time()))
        # Step 3: Create a worker object, on crée le worker object qui est une classe définit plus bas, la classe
        # Worker hérite de QObkect et doit contenr une méthode ici run2
        # on recrée le worker
        worker = Worker()
        # Step 4: Move worker to the thread
        worker.moveToThread(thread)
        # Step 5: Connect signals and slots
        thread.started.connect(
            partial(worker.downloadOrganism, item, combobox,
                                            progressBar))  # on connecte le signal started du thread a un slot

        # self.thread.finished.connect(lambda: self.createNode(
        #    treeWidget))  # on connecte la fin du thread à une fonction. Ici c une fonction qui ajoute juste un fichier dans notre arborescence

        # quand le worker finit, on quitte le thred et on delete les objets alloués, c'est nous qui avons implémenté
        # le signal finished pour worker !!!!
        worker.finished.connect(thread.quit)
        worker.hide_bar.connect(lambda: progressBar.hide())
        worker.show_bar.connect(lambda: progressBar.show())
        worker.enable_download.connect(lambda: self.button.setEnabled(True))
        worker.disable_download.connect(lambda: self.button.setEnabled(False))

        worker.print_log.connect(self.print_log)
        worker.add_log.connect(self.add_log)
        worker.clear_log.connect(self.clear_log)
        worker.checked_itm.connect(self.checked_item)

        worker.progress.connect(self.setValue)
        worker.finished.connect(worker.deleteLater)
        # thread.finished.connect(self.free)

        # worker.progress.connect(fonction qui sexecute à chaque fois que le signal progress est émis)
        # Remarque : la clase thread contient déjà le signal finished mais pas notre classe Worker
        # dans laquelle on a crée le signal finished
        # Step 6: Start the thread
        thread.start()

    def checked_item(self, itm):
        self.currentItem.setIcon(0, QIcon(":/check"))

    def print_log(self, str):
        self.logText.setText(str)

    def add_log(self, log):
        self.logText.append(log)

    def clear_log(self):
        self.logText.clear()

    def setValue(self, value):
        self.progressBar.setValue(value)



class MyThread(QtCore.QThread):
    def output(self, txt):
        self.signal.emit(txt)
