from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication, QDialog, QScrollArea, QFormLayout, QWidget, QLabel, QFrame, QVBoxLayout, \
    QPushButton, QMessageBox
from new_project import Ui_Dialog as NewProjectDialog
import random
import sql_work as sw
import unzip_unrar as uu
import main
import time
import img_upload
import sys





Form, Window = uic.loadUiType("octopus_gui.ui")

app = QApplication(sys.argv)


window = Window()
form = Form()
form.setupUi(window)

CURRENT_PROJECT = False
PROJECT_ID = False


class CThread(QThread):
    valueChanged = pyqtSignal([int])
    def __init__(self,value):
        super().__init__()
        self.completed = value

    def run(self):
        while self.completed < 100:
            self.completed += 1
            self.msleep(100)
            self.valueChanged.emit(self.completed)

fill_thread = CThread(form.progressBar_6.value())
fill_thread.valueChanged.connect(form.progressBar_6.setValue)


def tab_load_data():
    # ContentCheckAndUpload_instance.start()
    fill_thread.start()




class ContentCheckAndUpload(QThread):
    def __init__(self):
        self.project_id = PROJECT_ID
        super().__init__()

        self.folder = ''
        self.set_date = ''
        self.set_main = ''
        self.photo_date = ''
        self.file_date =''
        self.file_names = ''
        self.file_names_str=''

    def run(self):
        global PROJECT_ID
        all_threads = sw.select_all

        form.groupBox_5.setTitle(str(PROJECT_ID))
        print(all_threads)
        for elem in all_threads:

            if uu.dir_exist(str(elem[2]) + str(elem[3])):
                print('Устанавливаем имя ' + elem[1])
                form.groupBox_5.setTitle(elem[1])
                self.folder = elem[2] + str(elem[3])
                ready, path = main.check_data_in_folder(self.folder)
                if ready:
                    form.label_24.setText("...   " + path + ".....folder checked!")
                    old_text = form.label_24.text()
                    self.set_date, self.set_main = main.set_name_search(path)
                    form.label_24.setText(
                        old_text + "      ||Date found:...   " + self.set_date + "   ||Set name:...   " + self.set_main)

                    if sw.work_folder_in_base(self.folder):
                        print('Такая рабочая папка уже есть в БД!')
                    else:
                        try:
                            self.photo_date, self.file_date, self.file_names = main.unpack(path)
                            print(self.photo_date, self.file_date, self.file_names)
                        except:
                            print('Распаковка сломалась!')
                        try:
                            self.file_names_str = self.file_names[2]+'  '+self.file_names[3]+'  '+self.file_names[4]

                            print(self.file_names_str)
                            sw.add_new_post(self.set_date, self.set_main, self.folder, self.photo_date, self.file_date, self.file_names_str)
                        except:
                            print('В БД ничего не записано...')

                        # try:
                        #     img_upload.select_and_send_pics(path)
                        #
                        # except:
                        #     print('Загрузка картинок не удалась!')

                time.sleep(1)






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

        print(uu.dir_exist(str(elem[2])+str(elem[3])))


        print(elem)
        item = QtWidgets.QListWidgetItem()
        if uu.dir_exist(str(elem[2])+str(elem[3])):
            item.setCheckState(QtCore.Qt.Checked)
            thread_info = elem[1] + ' ||  WORK folder:  ' + str(elem[2]) + str(elem[3]) + '  ||'
            item.setText(thread_info)
            form.listWidget.addItem(item)
            counter += 1
        else:
            print('Нет рабочей папки - '+str(elem[2])+str(elem[3]))


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

# ContentCheckAndUpload_instance = ContentCheckAndUpload()

# ProgressBarThread_instance = ProgressBarThread()
#
# def tab_load_data():
#     # ContentCheckAndUpload_instance.start()
#     ProgressBarThread_instance.start()


    # main.load_data_main()




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

form.pushButton_9.clicked.connect(tab_load_data)





# form.tabWidget.tabBarClicked[int].connect(tab_load_data)

window.show()
app.exec()

