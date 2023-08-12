import os
import shutil
import sys
from datetime import datetime
from functools import partial

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow
)
import ressources

from worker import Worker


def palette_dark():
    app = QtWidgets.QApplication.instance()
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


def palette_white():
    app = QtWidgets.QApplication.instance()
    palette = QPalette()
    app.setPalette(palette)


class Window(QMainWindow):  # , Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.settings = QtCore.QSettings()
        uic.loadUi('src/gui.ui', self)  # Load the .ui file
        self.set_palette()  # set palette for windows that cant add palette on the fly
        self.cache = ".cache_Genbank"
        self.progressBar.hide()
        self.dialog = QtWidgets.QDialog()  # Fake object for threads
        self.worker = Worker()  # Thread for init arbo
        self.thread = QThread()
        self.last_clicked_item = None
        self.running_threads = []

        self.connect_signals()
        self.init_arbo()

        self.init_settings()

    def set_palette(self):
        if self.settings.contains("theme/dark_mode"):
            is_dark = int(self.settings.value("theme/dark_mode"))
            self.setDarkWhitePalette(is_dark)

    def init_settings(self):
        # Load settings

        # DARK MODE
        if self.settings.contains("theme/dark_mode"):
            is_dark = int(self.settings.value("theme/dark_mode"))
            self.actionDarkMode.setChecked(is_dark)
            self.setDarkWhitePalette(is_dark)

        # SOLVE PROBLEM
        if self.settings.contains("preferences/solve_problem"):
            solve_problem = int(self.settings.value("preferences/solve_problem"))
            self.actionR_soudre_les_Probl_mes.setChecked(solve_problem)

    def setDarkWhitePalette(self, is_dark):
        if is_dark:
            palette_dark()
            w = Worker()
            w.map_func_to_tree(self.treeWidget, w.update_icon, self.combobox.currentText())
            self.settings.setValue("theme/dark_mode", 1)
        else:
            palette_white()
            w = Worker()
            w.map_func_to_tree(self.treeWidget, w.update_icon, self.combobox.currentText())
            self.settings.setValue("theme/dark_mode", 0)

    def update_settings(self):
        # Solve problem
        if self.actionR_soudre_les_Probl_mes.isChecked():
            self.settings.setValue("preferences/solve_problem", 1)
        else:
            self.settings.setValue("preferences/solve_problem", 0)

        # Dark mode
        if self.actionDarkMode.isChecked():
            self.settings.setValue("theme/dark_mode", 1)
        else:
            self.settings.setValue("theme/dark_mode", 0)

    def connect_signals(self):
        self.actionR_soudre_les_Probl_mes.triggered.connect(self.solve_problem)
        self.actionDarkMode.triggered.connect(self.setDarkWhitePalette)
        self.emptyCache.triggered.connect(self.empty_cache)
        self.downloadButton.setEnabled(False)
        self.treeWidget.itemClicked.connect(self.update_item)
        self.downloadButton.clicked.connect(lambda: self.connect_download(self.last_clicked_item,
                                                                          self.combobox))
        self.combobox.currentIndexChanged.connect(self.update_icons)

        # Function to update settings
        self.actionR_soudre_les_Probl_mes.triggered.connect(self.update_settings)
        self.actionDarkMode.triggered.connect(self.update_settings)

    def update_icons(self):
        w = Worker()
        w.map_func_to_tree(self.treeWidget, w.update_icon, self.combobox.currentText())

    def solve_problem(self):
        # Call solve_problem only if the option has been checked
        if self.actionR_soudre_les_Probl_mes.isChecked():
            thread = QtCore.QThread()
            self.running_threads.append(thread)

            worker = Worker()
            worker.moveToThread(thread)
            thread.started.connect(worker.solve_problem_func)  # on connecte le signal started du thread a un slot
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            worker.finished.connect(self.download_finished)
            thread.start()

    def connect_download(self, item, combobox):
        self.download_started()
        self.currentItem = item
        thread = QtCore.QThread()
        self.running_threads.append(thread)
        worker = Worker()
        worker.set_solve_problem(self.actionR_soudre_les_Probl_mes.isChecked())
        worker.moveToThread(thread)
        thread.started.connect(
            partial(worker.downloadOrganism, item, combobox))  # on connecte le signal started du thread a un slot
        worker.finished.connect(thread.quit)

        worker.print_log.connect(self.print_log)
        worker.add_log.connect(self.add_log)
        worker.clear_log.connect(self.clear_log)
        worker.checked_itm.connect(self.checked_item)
        worker.progress.connect(self.setValue)
        worker.finished.connect(worker.deleteLater)
        worker.finished.connect(self.download_finished)
        thread.start()

    def download_started(self):
        self.downloadButton.hide()
        self.progressBar.show()

    def download_finished(self):
        self.update_icons()
        self.downloadButton.show()
        self.progressBar.hide()

    def empty_cache(self):
        try:
            shutil.rmtree(self.cache)
        except:
            print("error: could not clean cache.")
        pass

    def checked_item(self, item=None, state=None):
        is_dark = self.is_dark()
        if item is None:
            item = self.currentItem
        for i in range(item.childCount()):
            self.checked_item(item.child(i))
        if is_dark:
            if state == "check":
                item.setIcon(0, QIcon(":/check-dark"))
            else:
                item.setIcon(0, QIcon(":/cross"))
        else:
            if state == "check":
                item.setIcon(0, QIcon(":/check"))
            else:
                item.setIcon(0, QIcon(":/cross"))

    def is_dark(self):
        palette = QApplication.instance().palette()
        return palette.windowText().color().lightness() > palette.window().color().lightness()

    def setValue(self, value):
        self.progressBar.setValue(value)

    def update_item(self):
        self.last_clicked_item = self.treeWidget.currentItem()
        if self.last_clicked_item.childCount() == 0:
            self.label.setText(self.last_clicked_item.text(0))

    def setDark(self, app):
        self.toolBar.setDark(app)

    def setDarkMenuBar(self, app):
        self.menuBar.setDarkMenuBar(app)

    def init_arbo(self):
        self.worker.moveToThread(self.thread)  # Step 4: Move worker to the thread
        self.thread.started.connect(
            partial(self.worker.init_arbo, self.treeWidget))  # Step 5: Connect signals and slots
        self.worker.progress.connect(self.step_progress)
        self.worker.set_max_bottom_bar.connect(self.set_max_bottom_bar)

        self.worker.print_log.connect(self.print_log)
        self.worker.add_log.connect(self.add_log)
        self.worker.clear_log.connect(self.clear_log)

        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.show_all_ui)
        self.thread.start()

    def step_progress(self, a):
        self.progressBar_2.setValue(a)

    def set_max_bottom_bar(self, maximum):
        self.progressBar_2.setMaximum(maximum)

    def show_all_ui(self):
        self.downloadButton.setEnabled(True)
        self.progressBar_2.setHidden(True)

    def print_log(self, log):
        self.textEdit.setText(log)

    def add_log(self, log):
        self.textEdit.append(log)

    def clear_log(self):
        self.textEdit.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    path = os.path.join("src/flat.qss")
    with open(path) as flat_style:
        flat_style_str = flat_style.read()
    win = Window()
    win.show()
    sys.exit(app.exec())
