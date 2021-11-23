import math
import os
from ftplib import FTP

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication, QDialog, QScrollArea, QFormLayout, QWidget, QLabel, QFrame, QVBoxLayout, \
    QPushButton, QMessageBox
from PyQt5.uic.properties import QtGui

import logins
from new_project import Ui_Dialog as NewProjectDialog
import random
import sql_work as sw
import unzip_unrar as uu
import main
import time
import img_upload
import sys
from bs4 import BeautifulSoup

Form, Window = uic.loadUiType("octopus_gui.ui")

app = QApplication(sys.argv)

window = Window()
form = Form()
form.setupUi(window)

CURRENT_PROJECT = False
PROJECT_ID = 20


class LinkThread(QThread):  # ЕЩЕ ОДИН ПОТОК ДЛЯ ПОИСКА ССЫЛОК НА ФАЙЛХОСТЕ
    def __init__(self):
        super().__init__()
        self.project_id = 20

    def run(self):
        counter = 0
        for row in range(20):
            for column in range(20):

                item = QtWidgets.QTableWidgetItem()
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                form.tableWidget.setItem(row, column, item)


        while form.checkBox_11.isChecked():
            self.link_search()
            counter += 1
            print('Запрос номер ', counter)
            time.sleep(40)
        else:
            self.link_search()

    def link_search(self):



        all_threads = sw.select_all(self.project_id)
        print(all_threads)
        counter = 0
        zip_uploaded_yes = 0

        for elem in all_threads:
            folder = str(elem[2]) + str(elem[3])
            zip_file = folder + '.zip'



            # print(sw.check_thread_in_posts(folder))

            if uu.dir_exist(folder) and sw.check_zip_file(zip_file):

                print('запрос c папкой ', folder)
                post_info = sw.select_info_from_post(folder)
                zip_info = sw.select_info_from_zip(zip_file)
                print('+++++++++++++')
                print(post_info)
                print(zip_info)
                print('Тред есть и готов к постингу')



                print('counter = ',counter)
                try:
                    haystack = img_upload.login_host()


                    if zip_file in haystack:
                        print('zip найден в ответе сервера')
                        soup = BeautifulSoup(haystack, features="html.parser")

                        for link in soup.find_all('a', {'title': zip_file}):
                            zip_link = link.get('href')
                            if zip_link:
                                print(zip_link)
                                sw.insert_zip_link(zip_link, zip_file)

                        item = form.tableWidget.item(counter, 4)
                        item.setText('YES')
                        zip_uploaded_yes += 1

                    else:
                        item = form.tableWidget.item(counter, 4)
                        item.setText('NO')

                except:
                    print('Проблема с доступом к файл-хосту!')

                try:

                    item = form.tableWidget.item(counter, 0)
                    item.setText(str(elem[1]))
                    item = form.tableWidget.item(counter, 1)
                    item.setText(folder)
                    item = form.tableWidget.item(counter, 2)
                    size = str(round((int(zip_info[0][2]))/1048576, 2))

                    item.setText(str(post_info[0][10])+' pics,     '+size+' Mb')
                    item = form.tableWidget.item(counter, 3)
                    item.setText(str(zip_info[0][0])+',  '+str(elem[0])+',  '+str(post_info[0][0]))
                    print('успешно!')
                except:
                    print('не удалось обработать пост № '+str(post_info[0][0]))


                counter += 1

            # elif uu.dir_exist(folder) and sw.check_thread_in_posts(folder):
            #     print('Тред есть и постинг выполнен')
            #     print('Обновляем счетчик starting_id')
            #     sw.starting_id(elem[2], elem[3])



        if counter == 0 or zip_uploaded_yes == counter:
            form.checkBox_11.setChecked(False)



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
        self.thread = 50

    def run(self):
        print('self.project_id=', self.project_id)
        all_threads = sw.select_all(self.project_id)
        form.groupBox_5.setTitle(str(PROJECT_ID))
        print(all_threads)

        for elem in all_threads:
            current_dir = str(elem[2]) + str(elem[3])
            self.thread = elem[0]
            if uu.dir_exist(current_dir) and uu.check_dir(current_dir):
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
                        self.file_names_str = self.file_names[2] + '  ' + self.file_names[3] + '  ' + self.file_names[4]

                        print(self.file_names_str)
                        self.post_id = sw.add_new_post(self.set_date, self.set_main, self.folder, self.photo_date,
                                                       self.file_date, self.file_names_str, self.thread)
                    except:
                        print('В БД ничего не записано...')
                    fill_thread.target = 20
                    fill_thread.start()
                    print('self.post_id=', self.post_id)

                    try:
                        quantity, otbor = img_upload.select_and_send_pics(path)
                        print('Количество картинок - ' + str(quantity))
                        print(otbor)
                        fill_thread.target = 32
                        fill_thread.start()
                    except:
                        print('Отбор картинок провален!!!')

                    # считываем каркас поста из текстового файла
                    ut_text = ''
                    try:
                        with open('upload-test.txt', 'r') as ut:
                            ut_text = ut.read()


                    except:
                        print('Невозможно прочитать файл upload-test.txt')


                    for elem in otbor:
                        to_python = img_upload.upload_img(elem, path)
                        print(to_python)
                        print('загружаю ' + elem)
                        fill_thread.target += 7
                        fill_thread.start()
                        sw.img_in_base(elem, to_python['th_url'], to_python['show_url'], self.post_id)

                        ut_text = ut_text.replace('show_url'+elem, to_python['show_url'])
                        ut_text = ut_text.replace('th_url' + elem, to_python['th_url'])

                    print(ut_text)
                    sw.save_message(self.post_id, ut_text)





                time.sleep(1)
                print('Формируем архив')
                file_name = uu.pack_and_del(path)
                # проверка: в папке 1 zip с размером не менее 1Мб, созданный не более минуты назад
                size = uu.check(path)
                print(file_name, ' size= ', size)

                fill_thread.target = 100
                fill_thread.start()


                if size > 1:
                    print('ЗДЕСЬ')
                    try:
                        size = os.path.getsize(file_name)
                        ftp = FTP(logins.FTP_HOST)
                        response = ftp.login(logins.FTP_LOGIN, logins.FTP_PASS)

                        print(response)
                        with open(file_name, 'rb') as f:
                            ftp.storbinary('STOR ' + os.path.split(file_name)[1], f, 262144, progress(size / 262144))
                        print("конец загрузки файла", file_name)
                    except:
                        print('Проблемы со связью по FTP')

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


# def select_theme():
#     form.pushButton.setEnabled(True)


def add_new_thread_in_project_list(project_id):
    all_threads = sw.select_all_threads_in_project(project_id)
    print(all_threads)

    counter = 0
    form.listWidget.clear()
    for elem in all_threads:
        current_dir = str(elem[2]) + str(elem[3])

        print(uu.dir_exist(current_dir))

        print(elem)
        item = QtWidgets.QListWidgetItem()
        print(uu.check_dir(current_dir))

        if uu.dir_exist(current_dir):
            if uu.check_dir(current_dir):
                item.setCheckState(QtCore.Qt.Checked)
                thread_info = elem[1] + ' ||  WORK folder:  ' + str(elem[2]) + str(elem[3]) + 20*' . '+'READY!'
                item.setText(thread_info)
                form.listWidget.addItem(item)
                counter += 1
            else:
                item.setCheckState(QtCore.Qt.Unchecked)
                thread_info = elem[1] + ' ||  WORK folder:  ' + str(elem[2]) + str(elem[3]) + 50*' . '+'empty!'
                item.setText(thread_info)
                form.listWidget.addItem(item)
                counter += 1
                print('Папка '+current_dir+' пуста!')

        else:
            print('Нет рабочей папки - ' + str(elem[2]) + str(elem[3]))

def save_place_thread():
    if form.comboBox_2.currentIndex() and form.comboBox_3.currentIndex() and form.lineEdit_17.text().strip():
        thread_id = form.comboBox_2.currentData()
        place_id = form.comboBox_3.currentData()
        link_url = form.lineEdit_17.text().strip()
        sw.save_place_thread(thread_id[0], place_id[0], link_url)
        print(form.comboBox_2.currentData())
        print(form.comboBox_3.currentData())
    else:
        print('Need more information!')
        form.label_38.setText('Need more info!')




def places_for_post_load(project_id):
    places = sw.select_data_from_forums(project_id)
    form.comboBox.clear()
    form.comboBox.addItem('Not selected', 0)
    form.comboBox_3.clear()
    form.comboBox_3.addItem('Not selected', 0)
    form.comboBox_2.clear()
    form.comboBox_2.addItem('Not selected', 0)

    for elem in places:
        form.comboBox.addItem(elem[1], elem)
        form.comboBox_3.addItem(elem[1], elem)

    all_threads = sw.select_all_threads_in_project(project_id)

    for elem in all_threads:
        form.comboBox_2.addItem(elem[1], elem)





def project_threads_load():
    add_new_thread_in_project_list(PROJECT_ID)
    places_for_post_load(PROJECT_ID)



zip_link_search = LinkThread()


def check_table():
    zip_link_search.start()




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


def load_current_place():
    x = form.comboBox.currentData()

    print(x)
    if x:
        print(x[1])
        form.label_34.setText(str(x[0]))
        form.lineEdit_14.setText(str(x[1]))
        form.lineEdit_15.setText(str(x[2]))
        form.lineEdit_16.setText(str(x[5]))
        form.textEdit_3.setText(str(x[4]))
    else:
        form.lineEdit_14.setText('')
        form.lineEdit_15.setText('')
        form.textEdit_3.setText('')
        form.label_34.setText('')
        form.lineEdit_16.setText('')

def load_current_place_thread():
    x = form.comboBox_2.currentData()
    y = form.comboBox_3.currentData()
    print('x:', type(x))
    print('y', type(y))
    if isinstance(x, tuple)  and isinstance(y, tuple):
        print('Это тюплы!')
        url_link = sw.select_current_place_thread(x[0], y[0])
        form.lineEdit_17.setText(url_link)
        print(url_link)


# СИГНАЛЫ В ПУНКТАХ МЕНЮ
form.actionNew_project.triggered.connect(openDialog)  # Открыть новую форму
form.actionOpen_project.triggered.connect(open_project)  # открытие существующего проекта
form.actionExit.triggered.connect(on_exit)  # выход из приложения

if CURRENT_PROJECT:
    form.tabWidget.setEnabled(True)

# КЛИК НА КНОПКЕ
# form.pushButton.clicked.connect(add_text_label_in_tab)  # выход из приложения

# form.comboBox.activated.connect(select_theme)

form.pushButton_6.clicked.connect(add_new_thread_folder)

form.pushButton_7.clicked.connect(project_threads_load)

form.pushButton_8.clicked.connect(check_table)

form.pushButton_9.clicked.connect(tab_load_data)

form.pushButton_100.clicked.connect(main.reset_data)

form.pushButton_save_ft.clicked.connect(save_place_thread)

form.comboBox.currentIndexChanged.connect(load_current_place)

form.comboBox_2.currentIndexChanged.connect(load_current_place_thread)
form.comboBox_3.currentIndexChanged.connect(load_current_place_thread)


def save_place():
    print('Save place')
    try:
        name = form.lineEdit_14.text().strip()
        login_url = form.lineEdit_15.text().strip()
        inputs = form.textEdit_3.toPlainText().strip()
        userid = form.lineEdit_16.text().strip()

        if name and login_url and inputs and userid:

            if form.label_34.text():
                sw.update_place_in_bd(name, login_url, inputs, userid, form.label_34.text())

            else:
                sw.save_place_in_bd(name, login_url, inputs, userid, PROJECT_ID)
        else:
            print('Неверные данные')


        print('Success save')
        places_for_post_load(PROJECT_ID)
    except:
        print('No save')


form.pushButton_save.clicked.connect(save_place)



def view_info_from_cell(row):


    try:
        item = form.tableWidget.item(row, 0)
        post_name = item.text()
        item = form.tableWidget.item(row, 1)
        folder = item.text()
        item = form.tableWidget.item(row, 2)
        size_nums = item.text()
        item = form.tableWidget.item(row, 3)
        all_id = item.text()


    except:
        print('вылет')

    try:
        form.lineEdit.setText(post_name)
        form.lineEdit_2.setText(folder)
        form.lineEdit_5.setText(size_nums)

        x = all_id.split(',')
        thread_id = x[1].strip()

        print(thread_id)
        checkbox_dict = dict()
        places_for_post = sw.select_places_for_thread(thread_id)
        print("places_for_post:", places_for_post)
        counter = 0
        for elem in places_for_post:
            counter += 1
            place_name = sw.select_name_from_places(elem[1])
            print(place_name[0])
            checkbox_name = "checkBox"+"_dynamic_"+str(counter)


            form.checkbox_name = QtWidgets.QCheckBox(form.verticalLayoutWidget_6)
            form.checkbox_name.setObjectName(checkbox_name)
            form.verticalLayout_9.addWidget(form.checkbox_name)

            form.checkbox_name.setText(place_name[0])
            form.checkbox_name.setChecked(True)
            checkbox_dict[checkbox_name] = elem
            print(form.checkbox_name.isChecked())


        form.line_v = QtWidgets.QFrame(form.verticalLayoutWidget_6)
        form.line_v.setFrameShape(QtWidgets.QFrame.VLine)
        form.line_v.setFrameShadow(QtWidgets.QFrame.Sunken)
        form.line_v.setObjectName("line_v")
        form.verticalLayout_9.addWidget(form.line_v)

        # print(checkbox_dict)
    except:
        pass





    try:
        full_post_info = sw.select_info_from_post(folder)
        form.lineEdit_3.setText(full_post_info[0][5])
        form.lineEdit_4.setText(full_post_info[0][6])
        form.lineEdit_6.setText(full_post_info[0][7])
        form.lineEdit_7.setText(full_post_info[0][8])
        form.lineEdit_8.setText(full_post_info[0][9])
        form.textEdit.setText(full_post_info[0][3])
    except:
        print('Что-то с БД')

    form.tabWidget.setCurrentIndex(3)
    return checkbox_dict

def view_cell(row, cell):
    print('Клик по клетке!', row, cell)
    checkbox_dict = dict()
    try:
        checkbox_dict = view_info_from_cell(row)
        print(form.checkBox_dynamic_1.isChecked())
    except:
        pass
    print('вернулся словарь: ',checkbox_dict)



form.tableWidget.cellDoubleClicked.connect(view_cell)


window.show()
app.exec()
