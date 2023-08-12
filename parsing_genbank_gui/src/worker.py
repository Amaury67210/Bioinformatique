import os
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QTreeWidgetItem, QApplication
from PyQt5.QtGui import QIcon
from utils.Genbank_API import Genbank_API
import ressources  # DONT REMOVE
from API import efetch
from genbank_manager import manager
from Write_NC import *


class Worker(QObject):
    # emit this signal to check the item selected by the user and there children
    checked_itm = pyqtSignal(QTreeWidgetItem, str)
    # Erase log and print log
    print_log = pyqtSignal(str)
    # Add a log
    add_log = pyqtSignal(str)
    # Clear log area
    clear_log = pyqtSignal()
    # Emit this everytime a job is finished
    finished = pyqtSignal()
    # Update the progress bar
    progress = pyqtSignal(int)
    set_max_bar = pyqtSignal(int)

    # Deprecated
    set_max_bottom_bar = pyqtSignal(int)

    # This list of files represents all the files that should not be
    # printed in the Genbank GUI
    leaf_files = ["CDS", "centromere", "intron", "mobile_element", "ncRNA",
                  "rRNA", "telomere", "tRNA", "3'UTR", "5'UTR", "source", "gene",
                  "exon", "NC.txt", "repeat_region"]

    def __init__(self):
        super().__init__()
        self.solve_problem = False

    def set_solve_problem(self, solve_problem):
        self.solve_problem = solve_problem

    def init_arbo(self, tree):
        """
        Cette fonction devra initialiser notre arborescence dans notre application. Par exemple, si les données sont stockées
        dans data, alors cette fonction devra lire récursivement data. Elle est appelé à chaque fois qu'on
        lance l'application !!

        La fonction devra mettre un état (via une icone) si l'organisme a déjà été entièrement traité. Il faut
        pour cela chercher le fichier .meta qui est crée à chaque foi quun organisme a bien été traité. .meta contient
        la date du dernier update.
        :return:
        """

        self.print_log.emit("Starting... please wait.")
        self.set_max_bottom_bar.emit(100)
        bar = self.progress.emit
        bar(0)

        if not os.path.exists("Genbank") or not os.path.exists(".cache_Genbank"):
            from utils.pretraitement import pretraitement
            pretraitement()

        self.create_tree_recursivly("Genbank", tree)
        self.map_func_to_tree(tree, self.update_icon, "Toutes")  # update icon, default is Toutes.
        self.clear_log.emit()
        self.finished.emit()

    def create_tree_recursivly(self, root, tree):
        for el in os.listdir(root):
            path = os.path.join(root, el)

            if os.path.isdir(path):
                if el in self.leaf_files:
                    continue
                itm = QTreeWidgetItem(tree, [os.path.basename(el)])
                self.create_tree_recursivly(path, itm)

    def map_func_to_tree(self, tree: QtWidgets.QTreeWidget, callback, *args):
        """
        Cette fonction prend l'arbre, une callback et applique la callback à chaque élément de l'arbre.
        La callback doit prendre en argument l'item et le chemin. Elle peut également prendre des arguments
        supplémentaires qui avec *args.
        Exemple :
        map_func_to_tree(tree, callback, arg1, arg2) appelera dans le code callback(item, path, arg1, arg2).
        :param tree: L'arbre
        :param callback: La callback appliquée à chaque item.
        :param args: Les arguments supplémentaires optionnels pour la callback.
        :return:
        """

        def aux(item, root):
            nb_children = item.childCount()
            for i in range(nb_children):
                child = item.child(i)
                path = os.path.join(root, child.text(0))
                callback(child, path, *args)  # appeler la callback
                aux(child, path)

        for i in range(tree.topLevelItemCount()):
            aux(tree.topLevelItem(i), tree.topLevelItem(i).text(0))

    # Notre callback pour la fonction ci dessus.
    def update_icon(self, itm, path, region):
        # Met à jour l'icone d'un seul item en fonction de la région sélectionnée.
        gb = manager(path, region, verbose=False)
        state = gb.get_icon_type()
        if state == 0:
            self.set_icon(itm, "None")
        if state == 1:  # La région existe
            self.set_icon(itm, "check")
        if state == 2:  # La région n'existe pas
            self.set_icon(itm, "cross")
        if state == 3:  # La région est partielle
            self.set_icon(itm, "!")

    def is_dark(self):
        palette = QApplication.instance().palette()
        return palette.windowText().color().lightness() > palette.window().color().lightness()

    def set_icon(self, item=None, state=None):
        is_dark = self.is_dark()
        if item is None:
            item = self.currentItem
        for i in range(item.childCount()):
            self.set_icon(item.child(i))
        if is_dark:
            if state == "check":
                item.setIcon(0, QIcon(":/check-dark"))
            elif state == "!":
                item.setIcon(0, QIcon(":/exclamation-dark"))
            elif state == "cross":
                item.setIcon(0, QIcon(":/cross-dark"))
            else:
                item.setIcon(0, QIcon())
        else:
            if state == "check":
                item.setIcon(0, QIcon(":/check"))
            elif state == "!":
                item.setIcon(0, QIcon(":/exclamation"))
            elif state == "cross":
                item.setIcon(0, QIcon(":/cross"))
            else:
                item.setIcon(0, QIcon())

    def threatOrganism(self, path, ids, region, bar, log_type="print_log"):
        if log_type == "print_log":
            log = self.print_log
        if log_type == "add_log":
            log = self.add_log

        if self.solve_problem and manager(path, region, verbose=False).recovery_possible:
            manager(path, region, verbose=False).reset_organism()
            log.emit(f"Recovery Mode On: Attempting '{path}' download again...")

        if manager(path, region).path_in_genbank:
            if region == "Toutes":
                log.emit(f"'{path}' was already downloaded!")
            else:
                log.emit(f"Region '{region}' was already downloaded for '{path}'")
            manager(path, region, verbose=False).update_metadata()
            return
        if manager(path, region, verbose=False).unavailable_region:
            if manager(path, region, verbose=False).is_region_all:
                log.emit(f"There are no available regions for path '{path}' !")
            else:
                log.emit(f"Region '{region}' not available for path '{path}'.")
            manager(path, region, verbose=False).add_attempted_unavailable_regions()
            return
        if not manager(path, region, verbose=False).path_in_cache:
            # Loading from cache failed, downloading the sequences
            fasta_list, recovery = efetch(ids, log=self.add_log, bar=bar, use_twins=self.solve_problem)
            # NC() will add the unused files to cache and the wanted files to genbank
            nc_obj = NC(path, fasta_list, region, log=self.add_log)
            if not nc_obj.exists:
                log.emit(f"Region '{region}' not available for path '{path}'.")
                manager(path, region, verbose=False).add_attempted_unavailable_regions()
            if recovery is True:
                manager(path, region, verbose=False).add_recovery_possible()
        else:
            if manager(path, region, bar=bar, verbose=False).move_and_update():
                log.emit(f"Sucessfuly loaded '{path}' on region '{region}' from the Genbank database.")
            else:
                log.emit(f"Region '{region}' not available for path '{path}'.")

    def update_tree(self, root, region, bar):
        """
        Cette fonction  doit update le tree en allant chercher tous les nouveaux organismes sur internet.
        Elle devra alors créer les fichiers dans le dossier data puis pour chaque organisme nouveau, lajouter avec
        la fonction add_node_to_tree(tree, complete_path).
        Pour chaque organisme traité (et seulement quand on est sur que cela a été traité), on pourra écrire dans un
        fichier .meta lheure de la dernière mise à jour.
        :param tree: QtTreeWidget
        :return:
        """
        self.clear_log.emit()
        targets = {}

        # Fonction récursive qui parcourt le dossier choisi et ajoute chaque
        # NC au dictionaire targets. La clé est le path ou se trouve le NC.txt
        def parse_genbank_dir(root):
            targets[root] = []
            for el in os.listdir(root):
                path = os.path.join(root, el)

                if os.path.isdir(path) and path not in self.leaf_files:
                    parse_genbank_dir(path)

                if el == "NC.txt":
                    with open(path, "r") as f:
                        targets[root] += [nc for nc in f.read().split(";")[:-1]]

        parse_genbank_dir(os.path.join(".cache_Genbank", root))

        self.print_log.emit(f"Downloading sequences for group '{root}' on region '{region}'...")

        # On parcourt le dictionaire et on créer les séquences
        for path, ids in targets.items():
            if len(ids) == 0: continue
            path = path[len(".cache_Genbank/"):]
            self.threatOrganism(path, ids, region, bar, log_type="add_log")

    def downloadOrganism(self, item: QtWidgets.QTreeWidgetItem, combobox: QtWidgets.QComboBox):
        region = combobox.currentText()
        self.set_max_bar.emit(100)
        bar = self.progress.emit
        bar(0)

        # On cherche le chemin qui mène à cet organisme et ses NC
        path = ""
        item_copy = item

        # chemin
        while item_copy:
            path = os.path.join(item_copy.text(0), path)
            item_copy = item_copy.parent()
        cache_path = os.path.join(".cache_Genbank", path)

        if item is None:
            self.print_log.emit("Please select an organism or a family of organisms !")
            self.finished.emit()
            return

        if item.childCount() == 0:  # c'est un organisme pas un groupe
            try:
                with open(os.path.join(cache_path, "NC.txt"), "r") as f:
                    ids = [nc for nc in f.read().split(";")[:-1]]
            except:
                self.print_log.emit("Please select an organism or a family of organisms !")
                self.finished.emit()
                return

            self.set_max_bar.emit(100)
            self.print_log.emit(f"Downloading sequences for '{path}' on region '{region}'...")
            self.threatOrganism(path, ids, region, bar)

        else:  # c'est un groupe
            self.update_tree(path, region, bar)

        self.finished.emit()

    def solve_problem_func(self):
        pass
