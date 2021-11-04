from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QScrollArea, QFormLayout, QWidget, QLabel, QFrame, QVBoxLayout, \
    QPushButton
from new_project import Ui_Dialog as NewProjectDialog
import sql_work as sw
import random

Form, Window = uic.loadUiType("octopus_gui.ui")
app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)

class DialogNewProject(QDialog, NewProjectDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.accept_data)
    def accept_data(self):
        new_project_name = self.lineEdit.text()
        print(new_project_name)
        sw.new_project_in_base(new_project_name, 'описание')

def on_exit():
    exit()

def openDialog():
    new_dialog = DialogNewProject()
    new_dialog.show()
    new_dialog.exec()


def add_text_label_in_tab():
    prefix = str(random.randint(3, 100000))
    label_name = "label" + prefix
    form.label.setText(label_name)

    form.label_name = QtWidgets.QLabel(form.scrollAreaWidgetContents)
    form.label_name.setObjectName(label_name)
    form.verticalLayout_4.addWidget(form.label_name)
    form.label_name.setText(label_name)




# СИГНАЛЫ В ПУНКТАХ МЕНЮ
form.actionNew_project.triggered.connect(openDialog)  # Открыть новую форму
form.actionExit.triggered.connect(on_exit)  # выход из приложения


# КЛИК НА КНОПКЕ
form.pushButton.clicked.connect(add_text_label_in_tab)  # выход из приложения



# scroll = QScrollArea()
# scroll.setWidgetResizable(True) # CRITICAL
#
#
# inner = QFrame(scroll)
# inner.setLayout(QVBoxLayout())
#
# scroll.setWidget(inner) # CRITICAL
#
# for i in range(40):
#     b = QPushButton(inner)
#     b.setText(str(i))
#     inner.layout().addWidget(b)
#
# scroll.show()


window.show()
app.exec()