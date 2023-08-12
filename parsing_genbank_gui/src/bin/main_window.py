
from functools import partial

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt, QThread

from src.bin.gui_widget import MenuBar, ToolBar, Label, Button
from src.worker import Worker
from src.bin.treeFile import TreeWidget


class Ui_MainWindow(object):

    def __init__(self, MainWindow):
        self.worker = Worker()
        self.thread = QThread()
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)

        # IMPORTANT : on déclare une grid -> voir le readme pour comprendre comment fonctionne grid
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)

        # on divise notre espace en deux. La zone est redimenssionnable
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")

        # on déclare notre premiere frame à gauche sur laquelle on place nos éléments
        # horizontalement
        self.frame = QtWidgets.QFrame(self.splitter)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tree = TreeWidget(self.frame, self.horizontalLayout)
        # self.tree.setObjectName("treeWidget")
        self.horizontalLayout.addWidget(self.tree.treeWidget)

        # on déclare notre frame2
        self.frame_2 = QtWidgets.QFrame(self.splitter)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        # cette fois, les éléments seront placés dans une grid pour plus de flexibilité
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName("gridLayout_2")

        # le nom de notre organisme
        self.label = Label(self.centralwidget, "label")
        self.label.setObjectName("label")
        self.label.setText("Organisme")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.gridLayout_2.addWidget(self.label, 1, 0, 1, 1)

        # la progress bar en haut a droite
        self.progressBar = QtWidgets.QProgressBar(self.frame_2)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout_2.addWidget(self.progressBar, 5, 0, 1, 2)

        # la combobox en haut à droite
        self.combobox = QtWidgets.QComboBox(self.frame_2)
        self.combobox.setObjectName("comboBox")
        self.gridLayout_2.addWidget(self.combobox, 1, 1, 1, 1)

        # passons a la zone dinformation
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 6, 0, 1, 2)
        self.gridLayout.addWidget(self.splitter, 0, 1, 1, 1)

        # la zone de texte informatif en bas a droite
        self.textEdit = QtWidgets.QTextEdit(self.frame_2)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.gridLayout_2.addWidget(self.textEdit, 8, 0, 1, 2)

        # le push button en haut a droite
        self.downloadButton = Button(self.frame_2, self.progressBar, self.textEdit)
        self.downloadButton.button.setObjectName("pushButton")
        self.gridLayout_2.addWidget(self.downloadButton.button, 4, 0, 1, 2)

        # la progress bar principale si on lance le téléchargement de tout le monde
        self.progressBar_2 = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar_2.setProperty("value", 24)
        self.progressBar_2.setObjectName("progressBar_2")
        self.gridLayout.addWidget(self.progressBar_2, 1, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.menuBar = MenuBar(MainWindow)
        self.menuBar.setObjectName("menubar")

        self.toolBar = ToolBar(main_window=MainWindow)
        self.toolBar.setObjectName("toolBar")
        self.downloadButton.button.setEnabled(False)
        self.init_arbo()


    def setupUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        # donner un nom a la window principale
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

        # on donne un nom a  notre grid
        self.gridLayout.setObjectName("gridLayout")

        # on ajoute des items a notre combobox
        self.combobox.addItem("Toutes")
        self.combobox.addItem("CDS")
        self.combobox.addItem("centromere")
        self.combobox.addItem("intron")
        self.combobox.addItem("mobile_element")
        self.combobox.addItem("ncRNA")
        self.combobox.addItem("rRNA")
        self.combobox.addItem("telomere")
        self.combobox.addItem("tRNA")
        self.combobox.addItem("3'UTR")
        self.combobox.addItem("5'UTR")

        # on voit mnt tout lintéret des noms donné aux objets. On pourra gérer les événements grce a leur noms
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.downloadButton.button.setText("Fetch And Parse")
        self.progressBar.hide()


    def connectSignalsAndSlots(self):
        # self.combobox.activated.connect(lambda: self.tree.printOrganisme(self.tree.getLastClickedItem(),
        #                                                                 self.combobox,
        #                                                                 self.textAreaUp.textArea))
        # self.tree.connectItemToLabel(self.combobox, self.textAreaUp.textArea)
        self.tree.treeWidget.itemClicked.connect(self.update_item)
        self.downloadButton.button.clicked.connect(lambda: self.downloadButton.connect(self.tree.lastClickedItem,
                                                                                       self.combobox,
                                                                                       self.progressBar))
        # la fonction start_thread lance la fonction en deuxième argument sur un thread
        self.toolBar.recharger.triggered.connect(partial(self.toolBar.connect_recharger, self.tree.treeWidget))

    def update_item(self):
        self.tree.lastClickedItem = self.tree.treeWidget.currentItem()
        if self.tree.lastClickedItem.childCount()==0:
            self.label.setText(self.tree.lastClickedItem.text(0))

    def setDark(self, app):
        self.toolBar.setDark(app)

    def setDarkMenuBar(self, app):
        self.menuBar.setDarkMenuBar(app)

    def init_arbo(self):
        self.thread.setObjectName("init_arbo")
        self.worker.moveToThread(self.thread)  # Step 4: Move worker to the thread
        self.thread.started.connect(partial(self.worker.init_arbo,self.tree.treeWidget))  # Step 5: Connect signals and slots
        self.worker.progress.connect(self.step_progress)
        self.worker.set_max_bottom_bar.connect(self.set_max_bottom_bar)

        self.worker.print_log.connect(self.print_log)
        self.worker.add_log.connect(self.add_log)
        self.worker.clear_log.connect(self.clear_log)

        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.show_all_ui)
        self.worker.finished.connect(self.hide_bottom_bar)
        # Step 6: Start the thread
        self.thread.start()

    def step_progress(self, a):
        self.progressBar_2.setValue(a)

    def set_max_bottom_bar(self, max):
        self.progressBar_2.setMaximum(max)

    def hide_bottom_bar(self):
        self.progressBar_2.setHidden(True)

    def show_all_ui(self):
        self.toolBar.recharger.setEnabled(True)
        self.downloadButton.button.setEnabled(True)

    def print_log(self, str):
        self.textEdit.setText(str)

    def add_log(self, log):
        self.textEdit.append(log)

    def clear_log(self):
        self.textEdit.clear()
