from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QDialog, QScrollArea, QFormLayout, QWidget, QLabel, QFrame, QVBoxLayout, \
    QPushButton
from new_project import Ui_Dialog as NewProjectDialog
import random
import sql_work as sw
import unzip_unrar as uu

Form, Window = uic.loadUiType("octopus_gui.ui")
app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)

CURRENT_PROJECT = False
PROJECT_ID = False


class DialogNewProject(QDialog, NewProjectDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.accept_data)

    def accept_data(self):
        new_project_name = self.lineEdit.text()
        if sw.check_new_project_name(new_project_name):
            global CURRENT_PROJECT, PROJECT_ID

            PROJECT_ID = sw.new_project_in_base(new_project_name, 'описание')
            print(PROJECT_ID)
            CURRENT_PROJECT = new_project_name
            print('Новый проект добавлен!')

            form.tabWidget.setEnabled(True)
        else:
            print('Такой проект уже есть!')


def open_project():
    global PROJECT_ID
    try:

        PROJECT_ID = sw.open_project()
        form.tabWidget.setEnabled(True)
    except:
        print('Открыть существующий проект не удалось')


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


def select_theme():
    form.pushButton.setEnabled(True)


def add_new_thread_in_project_list(project_id):
    all_threads = sw.select_all_threads_in_project(project_id)
    print(all_threads)

    counter = 0
    form.listWidget.clear()
    for elem in all_threads:
        print(elem)
        item = QtWidgets.QListWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        thread_info = elem[1] + ' ||  WORK folder:  ' + str(elem[2])+str(elem[3]) + '  ||'
        item.setText(thread_info)
        form.listWidget.addItem(item)
        counter += 1


def project_threads_load():
    add_new_thread_in_project_list(PROJECT_ID)


def add_new_thread_folder():
    name = form.lineEdit_11.text().strip()
    prefix = form.lineEdit_12.text().strip()
    starting_id = form.lineEdit_13.text().strip()
    if name and prefix and starting_id:
        print('Что-то вводили')
        try:
            sw.new_thread(name, prefix, starting_id, PROJECT_ID)
            print('Новая запись добавлена!')
            try:
                uu.create_dir(prefix + str(starting_id))
                add_new_thread_in_project_list(PROJECT_ID)

            except:
                print('Создать папку для записи не удалось!')
        except:
            print('Ошибка записи в БД')

    else:
        print('Данных нет')


# СИГНАЛЫ В ПУНКТАХ МЕНЮ
form.actionNew_project.triggered.connect(openDialog)  # Открыть новую форму
form.actionOpen_project.triggered.connect(open_project)  # открытие существующего проекта
form.actionExit.triggered.connect(on_exit)  # выход из приложения

if CURRENT_PROJECT:
    form.tabWidget.setEnabled(True)

# КЛИК НА КНОПКЕ
# form.pushButton.clicked.connect(add_text_label_in_tab)  # выход из приложения

form.comboBox.activated.connect(select_theme)

form.pushButton_6.clicked.connect(add_new_thread_folder)

form.pushButton_7.clicked.connect(project_threads_load)

window.show()
app.exec()
