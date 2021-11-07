import math
import os
from ftplib import FTP

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication, QDialog, QScrollArea, QFormLayout, QWidget, QLabel, QFrame, QVBoxLayout, \
    QPushButton, QMessageBox

import logins
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
PROJECT_ID = 20


class LinkThread(QThread):   # ЕЩЕ ОДИН ПОТОК ДЛЯ ПОИСКА ССЫЛОК НА ФАЙЛХОСТЕ
    def __init__(self, value):
        super().__init__()

    def run(self):
        pass




class CThread(QThread):
    valueChanged = pyqtSignal([int])

    def __init__(self, value):
        super().__init__()
        self.completed = value
        self.target = 0

    def run(self):
        while self.completed < self.target:
            self.completed += 1
            self.msleep(20)
            self.valueChanged.emit(self.completed)

    def reset(self):
        self.completed = 0
        self.valueChanged.emit(self.completed)


class ContentCheckAndUpload(QThread):
    def __init__(self):
        self.project_id = 20
        super().__init__()

        self.folder = ''
        self.set_date = ''
        self.set_main = ''
        self.photo_date = ''
        self.file_date = ''
        self.file_names = ''
        self.file_names_str = ''
        self.post_id = ''

    def run(self):
        print('self.project_id=', self.project_id)
        all_threads = sw.select_all(self.project_id)
        form.groupBox_5.setTitle(str(PROJECT_ID))
        print(all_threads)



        for elem in all_threads:
           if uu.dir_exist(str(elem[2]) + str(elem[3])):
                fill_thread.reset()
                fill_thread2.reset()
                print('Устанавливаем имя ' + elem[1])
                form.groupBox_5.setTitle(elem[1])
                fill_thread.target = 2
                fill_thread.start()
                time.sleep(1)
                self.folder = elem[2] + str(elem[3])

                ready, path = main.check_data_in_folder(self.folder)
                fill_thread.target = 5
                fill_thread.start()

                if not ready:
                    mistake = 'ОШИБКА! В папке ' + self.folder + ' некорректные данные!'
                    print(mistake)
                    form.label_25.setText(mistake)
                    break
                else:
                    form.label_24.setText("...   " + path + ".....folder checked!")

                    old_text = form.label_24.text()
                    self.set_date, self.set_main = main.set_name_search(path)
                    form.label_24.setText(
                        old_text + "      ||Date found:...   " + self.set_date + "   ||Set name:...   " + self.set_main)
                fill_thread.target = 7
                fill_thread.start()


                if sw.work_folder_in_base(self.folder):
                    print('Такая рабочая папка уже есть в БД!')
                    break
                else:
                    try:
                        self.photo_date, self.file_date, self.file_names = main.unpack(path)
                        print(self.photo_date, self.file_date, self.file_names)
                    except:
                        print('Распаковка сломалась!')
                    try:
                        self.file_names_str = self.file_names[2]+'  '+self.file_names[3]+'  '+self.file_names[4]

                        print(self.file_names_str)
                        self.post_id = sw.add_new_post(self.set_date, self.set_main, self.folder, self.photo_date, self.file_date, self.file_names_str)
                    except:
                        print('В БД ничего не записано...')
                    fill_thread.target = 20
                    fill_thread.start()
                    print('self.post_id=',self.post_id)

                    try:
                        quantity, otbor = img_upload.select_and_send_pics(path)
                        print('Количество картинок - '+str(quantity))
                        print(otbor)
                        fill_thread.target = 32
                        fill_thread.start()
                    except:
                        print('Отбор картинок провален!!!')

                    for elem in otbor:
                        to_python = img_upload.upload_img(elem, path)
                        print(to_python)
                        print('загружаю '+elem)
                        fill_thread.target += 7
                        fill_thread.start()
                        sw.img_in_base(elem, to_python['th_url'], to_python['show_url'], self.post_id)


                time.sleep(1)
                print('Формируем архив')
                file_name = uu.pack_and_del(path)
                # проверка: в папке 1 zip с размером не менее 1Мб, созданный не более минуты назад
                size = uu.check(path)
                print(file_name, ' size= ', size)

                fill_thread.target = 100
                fill_thread.start()

                if size > 1:
                    size = os.path.getsize(file_name)
                    ftp = FTP(logins.FTP_HOST)
                    response = ftp.login(logins.FTP_LOGIN, logins.FTP_PASS)

                    print(response)
                    with open(file_name, 'rb') as f:
                        ftp.storbinary('STOR ' + os.path.split(file_name)[1], f, 262144, progress(size / 262144))
                    print("конец загрузки файла", file_name)

                    temp_name = file_name.split('\\')
                    name = temp_name[len(temp_name) - 1]
                    zip_id = sw.zip_in_base(name, str(size))
                    sw.update_post_info(self.post_id, zip_id, quantity)


                else:
                    print("Программа прервана, проверьте папку " + path)




fill_thread = CThread(form.progressBar_5.value())
fill_thread.valueChanged.connect(form.progressBar_5.setValue)
fill_thread2 = CThread(form.progressBar_6.value())
fill_thread2.valueChanged.connect(form.progressBar_6.setValue)

ContentCheckAndUpload_instance = ContentCheckAndUpload()


def progress(all_blocks):
    all_blocks = math.ceil(all_blocks)

    def callback(block):
        callback.blocks_uploaded += 1
        callback.uploaded += len(block)
        uploaded = round(100 * callback.blocks_uploaded / all_blocks)
        fill_thread2.target = uploaded
        fill_thread2.start()

        print(f'Загружено {round(100 * callback.blocks_uploaded / all_blocks)} %')

    callback.blocks_uploaded = 0
    callback.uploaded = 0
    return callback


def tab_load_data():
    ContentCheckAndUpload_instance.start()
    # fill_thread.target = 10
    # fill_thread.start()


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

        print(uu.dir_exist(str(elem[2]) + str(elem[3])))

        print(elem)
        item = QtWidgets.QListWidgetItem()
        if uu.dir_exist(str(elem[2]) + str(elem[3])):
            item.setCheckState(QtCore.Qt.Checked)
            thread_info = elem[1] + ' ||  WORK folder:  ' + str(elem[2]) + str(elem[3]) + '  ||'
            item.setText(thread_info)
            form.listWidget.addItem(item)
            counter += 1
        else:
            print('Нет рабочей папки - ' + str(elem[2]) + str(elem[3]))


def project_threads_load():
    add_new_thread_in_project_list(PROJECT_ID)

def check_table():
    all_threads = sw.select_all_threads_in_project(PROJECT_ID)
    print(all_threads)
    for elem in all_threads:
        folder = str(elem[2]) + str(elem[3])
        if uu.dir_exist(folder) and not sw.check_thread_in_posts(folder):
            print('Тред есть и готов к постингу')
            haystack = img_upload.login_host()




        elif uu.dir_exist(folder) and sw.check_thread_in_posts(folder):
            print('Тред есть и постинг выполнен')




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

form.pushButton_8.clicked.connect(check_table)

form.pushButton_9.clicked.connect(tab_load_data)

# form.tabWidget.tabBarClicked[int].connect(tab_load_data)

window.show()
app.exec()
