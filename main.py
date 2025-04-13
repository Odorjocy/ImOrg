import os
import shutil
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAbstractItemView , QWidget, QLabel, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QInputDialog, QStatusBar, QMainWindow, QFileDialog, QAction, QToolBar, QMessageBox, QApplication


class Collection():
    def __init__(self,name):
        self.name = name
        self.images = []

    def add_image(self,image_path):
        self.images.append(image_path)


    def remove_image(self, image_path):
        self.images.remove(image_path)


    def check_image(self, image_path):
        if image_path not in self.images:
            return False
        else:
            return True


class Image():
    def __init__(self,path):
        self.path = path
        self.image = QPixmap(path)
        self.assigned_collections = []


    def assign_collection(self,collection_name):
        self.assigned_collections.append(collection_name)


    def unassign_collection(self,collection_name):
        self.assigned_collections.remove(collection_name)


class ImorgApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ImOrg")
        self.resize(800, 600)
        self.current_image_index = 0
        self.last_image_index = 0
        self.collections = {}
        self.pictures = []
        self.optionable_items = []
        self.working_directry = ""
        
        main_bar = QToolBar("Main toolbar")
        main_bar.setIconSize(QSize(16,16))
        self.addToolBar(main_bar)

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

        open_action = QAction(QIcon("./icons/open.png"),"&Open",self)
        open_action.triggered.connect(self.open)
        main_bar.addAction(open_action)

        finish_action = QAction(QIcon("./icons/finish.png"),"&Finish",self)
        self.optionable_items.append(finish_action)
        finish_action.triggered.connect(self.finish)
        main_bar.addAction(finish_action)
        
        close_action = QAction(QIcon("./icons/close.png"),"&Close",self)
        self.optionable_items.append(close_action)
        close_action.triggered.connect(lambda: self.reset(True))
        main_bar.addAction(close_action)

        exit_action = QAction(QIcon("./icons/exit.png"),"&Exit",self)
        exit_action.triggered.connect(self.exit)
        main_bar.addAction(exit_action)

        for item in self.optionable_items:
            item.setEnabled(False)

    def reset(self, interactive):
        if interactive:
            answer = QMessageBox.question(self,"Close", "Do you really want to close this session?") 
        else:
            answer = 16384

        if answer == 16384:
            collection_menu.clear()

            self.collections = {}
            self.pictures = []
            self.current_image_index = 0
            self.working_directry = ""
            image_label.setPixmap(QPixmap())
            self.setStatusTip("")


            for item in self.optionable_items:
                item.setEnabled(False)


    def initialize(self):
        for file in os.listdir(self.working_directry):
            if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".png"):
                image_full_path = os.path.join(self.working_directry, file)
                self.pictures.append(Image(image_full_path))

        if len(self.pictures) > 0:
            self.last_image_index = len(self.pictures) - 1
            self.display_image()
            next_image.clicked.connect(self.next_image)
            previous_image.clicked.connect(self.previous_image)
        else:
            QMessageBox.warning(self,"No image found", "There is no picture in the selected folder, please choose a folder with pictures(The supported extensions are: jpg, png)")

        for item in self.optionable_items:
            item.setEnabled(True)


    def open(self):
        folder = QFileDialog.getExistingDirectory(self, "Select a directory")
        if folder != "":
            if None != self.pictures:
                self.reset(False)
            self.working_directry = folder
            self.setStatusTip(folder)
            self.initialize()

    def exit(self):
        if QMessageBox.question(self,"Exit", "Are you sure you want to exit?") == 16384:
            ImorgApp.close(self)


    def next_image(self):
        if self.current_image_index == self.last_image_index:
            self.current_image_index = 0
        else:
            self.current_image_index += 1
        self.display_image()


    def previous_image(self):
        if self.current_image_index == 0:
            self.current_image_index = self.last_image_index
        else:
            self.current_image_index -= 1
        self.display_image()


    def display_image(self):
        image_label.hide()
        image = self.pictures[self.current_image_index]
        for collection in collection_menu.selectedItems():
            collection.setSelected(False)


        for collection in image.assigned_collections:
            list_entry = collection_menu.findItems(collection, Qt.MatchExactly)[0]
            list_entry.setSelected(True)

        image = image.image
        iw, ih = image.width(), image.height()
        lw, lh = image_label.width(), image_label.height()
        if (iw > lw or ih > lh):
            image = image.scaled(lw,lh, Qt.AspectRatioMode.KeepAspectRatio)
        else:
            image = image.scaled(iw,ih, Qt.AspectRatioMode.KeepAspectRatio)
        


        image_label.setPixmap(image)
        image_label.show()


    def add_collection(self, collection_name):
        while True:
            collection_name = QInputDialog.getText(add_collection_button, "Adding new collection","Enter a name")

            if not collection_name[1]:
                break
            elif collection_name[0] in self.collections:
                QMessageBox.warning(self,"Warning", "This collection is already exist!")
            elif collection_name[0] == '':
                QMessageBox.warning(self,"Warning", "Please provide a name!")
            else:
                collection_menu.addItem(collection_name[0])
                self.collections[collection_name[0]] = Collection(collection_name[0])
                break
            


    def assign_image_to_collection(self, collection_name, image):
        image_full_path = os.path.join(self.working_directry,image.path)
        if self.collections[collection_name].check_image(image_full_path):
            self.collections[collection_name].remove_image(image_full_path)
            image.unassign_collection(collection_name)
        else:
            self.collections[collection_name].add_image(image_full_path)
            image.assign_collection(collection_name)

    
    def finish(self):
        if len(self.collections) == 0:
            QMessageBox.warning(self,"No collection", "No collection has been created, nothing to proceed with.")
        elif QMessageBox.question(self,"Finish", "Are you sure you want to finish this session?") == 16384:
            try:
                for collection in self.collections:
                    collection_path = os.path.join(self.working_directry,collection)
                    os.mkdir(collection_path)
                    for image in self.collections[collection].images:
                        new_path = os.path.join(collection_path, image.split("/")[-1])
                        shutil.copy(image, new_path)

                QMessageBox.information(self,"Info", "The collections have been created!")
                self.reset(False)
            except:
                QMessageBox.warning(self,"Warning", "Something went wrong when finalyzing the pictures...")


app = QApplication([])
main_window = ImorgApp()
main_widget = QWidget()

add_collection_button = QPushButton("New collection")
add_collection_button.setEnabled(False)
main_window.optionable_items.append(add_collection_button)
add_collection_button.clicked.connect(main_window.add_collection)
collection_menu = QListWidget()
collection_menu.setSelectionMode(QAbstractItemView.MultiSelection)
collection_menu.setMinimumWidth(250)
collection_menu.itemPressed.connect(lambda: main_window.assign_image_to_collection(collection_menu.currentItem().text(), main_window.pictures[main_window.current_image_index]))
image_label = QLabel()
image_label.setAlignment(Qt.AlignCenter)
status_bar_layout = QHBoxLayout()

main_layout = QVBoxLayout()

main_row = QHBoxLayout()

collection_layout = QVBoxLayout()
collection_layout.addWidget(collection_menu)
collection_layout.addWidget(add_collection_button)

image_layout = QHBoxLayout()
previous_image = QPushButton()
previous_image.setEnabled(False)
previous_image.setFixedSize(QSize(40,200))
previous_image.setIcon(QIcon("./icons/previous.png"))
main_window.optionable_items.append(previous_image)
next_image = QPushButton()
next_image.setEnabled(False)
next_image.setFixedSize(QSize(40,200))
next_image.setIcon(QIcon("./icons/next.png"))
main_window.optionable_items.append(next_image)
image_layout.addWidget(previous_image)
image_layout.addWidget(image_label)
image_layout.addWidget(next_image)


main_row.addLayout(collection_layout, 10)
main_row.addLayout(image_layout, 80)
main_layout.addLayout(main_row)
main_layout.addLayout(status_bar_layout)

main_widget.setLayout(main_layout)
main_window.setCentralWidget(main_widget)


main_window.show()
app.exec()
