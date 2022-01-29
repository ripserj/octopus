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

checkbox_dict = dict()


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
        counter = 0
        zip_uploaded_yes = 0
        for elem in all_threads:
            folder = str(elem[2]) + str(elem[3])
            zip_info = sw.check_zip_file(folder)

            if uu.dir_exist(folder) and zip_info:
                zip_file = zip_info[0][1]
                post_info = sw.select_info_from_post(folder)
                try:
                    haystack = img_upload.login_host()

                    if zip_file in haystack:
                        soup = BeautifulSoup(haystack, features="html.parser")

                        for link in soup.find_all('a', {'title': zip_file}):
                            zip_link = link.get('href')
                            if zip_link:
                                print(f'{zip_file} найден по ссылке: {zip_link}!')
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
                    size = str(round((int(zip_info[0][2])) / 1048576, 2))

                    item.setText(str(post_info[0][10]) + ' pics,     ' + size + ' Mb')
                    item = form.tableWidget.item(counter, 3)
                    item.setText(str(zip_info[0][0]) + ',  ' + str(elem[0]) + ',  ' + str(post_info[0][0]))
                except:
                    print('не удалось обработать пост № ' + str(post_info[0][0]))

                counter += 1


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
        self.checked_threads = []

    def check_existence_arch_on_server(self, arch_name):
        return img_upload.login_host(filename=arch_name + '.zip')

    def check_qlist_items(self):
        """
        # ВОЗВРАЩАЕТ СПИСОК id ВЫДЕЛЕННЫХ ГАЛОЧКОЙ ТРЕДОВ
        :return: checked_threads
        """
        self.checked_threads = []
        for index in range(form.listWidget.count()):
            if form.listWidget.item(index).checkState() == Qt.Checked:
                self.checked_threads.append(form.listWidget.item(index).text().split('||')[0])

    def search_doubles(self):
        if sw.work_folder_in_base(self.folder):
            print(f'Рабочая папка {self.folder} уже есть в БД! Работа прервана!')
            return True
        elif self.check_existence_arch_on_server(self.folder):
            print(f'Файл с названием {self.folder} уже есть на файловом хосте! Работа прервана!')
            return True
        else:
            return False

    def run(self):
        all_threads = sw.select_all(self.project_id)
        form.groupBox_5.setTitle(str(PROJECT_ID))
        self.check_qlist_items()
        if len(self.checked_threads) > 0:
            step_thread3 = int(100 / len(self.checked_threads))
        fill_thread3.reset()
        for elem in all_threads:
            if str(elem[0]) not in self.checked_threads:
                continue
            self.folder = str(elem[2]) + str(elem[3])
            self.thread = elem[0]
            self.folder
            if 'vd_' in self.folder and uu.dir_exist(self.folder) and uu.check_dir(self.folder):
                print('Папка с видео  - другая логика обработки!')
                if self.search_doubles():
                    break
                try:
                    fill_thread.reset()
                    fill_thread2.reset()
                    form.label_24.setText("...   " + self.folder + ".....folder checked!")

                    vid_info = main.check_and_rename(self.folder)
                    print(vid_info)
                    resolution = vid_info[2]
                    length = vid_info[1]
                    format_video = vid_info[0]
                    file_name = vid_info[8]
                    screens = vid_info[7]
                    size = vid_info[9]
                    size_mb = vid_info[4]
                    self.set_main = vid_info[6]
                    pics_in_row = int(vid_info[10])
                    fill_thread.target = 50
                    fill_thread.start()

                    img_upload.make_text_links(screens, variant=pics_in_row)
                    ut_text = ''
                    try:
                        with open('upload-test.txt', 'r') as ut:
                            ut_text = ut.read()
                    except:
                        print('Невозможно прочитать файл upload-test.txt')

                    for image in screens:
                        to_python = img_upload.upload_img(image, vid_info[5], max_th_size=420)
                        sw.img_in_base(image, to_python['th_url'], to_python['show_url'], self.post_id)
                        print(to_python)
                        ut_text = ut_text.replace('show_url' + image, to_python['show_url'])
                        ut_text = ut_text.replace('th_url' + image, to_python['th_url'])

                    print(ut_text)
                    ut_text = 'Resolution: ' + str(resolution) + '\nTime: ' + str(length) + '\nFormat: ' + str(
                        format_video) + '\nsize: ' + str(size_mb) + '\n\n' + ut_text

                    fill_thread.target = 100
                    fill_thread.start()
                    form.label_24.setText("...   Creating screens and uploading for " + self.folder + ".....success!")

                    ftp = FTP(logins.FTP_HOST)
                    response = ftp.login(logins.FTP_LOGIN, logins.FTP_PASS)

                    with open(file_name, 'rb') as f:
                        ftp.storbinary('STOR ' + os.path.split(file_name)[1], f, 262144, progress(size / 262144))
                    print("конец загрузки файла", file_name)
                    form.label_24.setText("...   Uploading vid from " + self.folder + ".....success!")

                    # ЗАПИСЬ В БД основы для поста и информации о видео-файле

                    self.post_id = sw.add_new_post(self.set_date, self.set_main, self.folder, self.photo_date,
                                                   self.file_date, 'video', self.thread)
                    sw.save_message(self.post_id, ut_text)
                    zip_id = sw.zip_in_base(file_name.split('\\')[-1], str(size))
                    sw.update_post_info(self.post_id, zip_id, 1)

                except:
                    print('с обработкой видео проблемы!')


            elif 'vd_' not in self.folder and uu.dir_exist(self.folder) and uu.check_dir(self.folder):
                fill_thread.reset()
                fill_thread2.reset()
                print('Working with thread: ' + elem[1])
                form.groupBox_5.setTitle(elem[1])
                fill_thread.target = 2
                fill_thread.start()
                time.sleep(0.05)
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

                if self.search_doubles():
                    break
                else:
                    try:
                        self.photo_date, self.file_date, self.file_names = main.unpack(path)
                        # print(self.photo_date, self.file_date, self.file_names)
                    except:
                        print('Распаковка сломалась!')
                    try:
                        self.file_names_str = self.file_names[2] + '  ' + self.file_names[3] + '  ' + self.file_names[4]

                        # print(self.file_names_str)
                        self.post_id = sw.add_new_post(self.set_date, self.set_main, self.folder, self.photo_date,
                                                       self.file_date, self.file_names_str, self.thread)


                    except:
                        print('В БД ничего не записано...')
                    fill_thread.target = 20
                    fill_thread.start()

                    try:
                        quantity, otbor = img_upload.select_and_send_pics(path)
                        # print('Количество картинок - ' + str(quantity))
                        # print(otbor)
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
                        try:
                            to_python = img_upload.upload_img(elem, path)
                        except:
                            print('Загрузка картинок на файл-хост не удалась.')
                            break
                        fill_thread.target += 7
                        fill_thread.start()
                        sw.img_in_base(elem, to_python['th_url'], to_python['show_url'], self.post_id)

                        ut_text = ut_text.replace('show_url' + elem, to_python['show_url'])
                        ut_text = ut_text.replace('th_url' + elem, to_python['th_url'])

                    print(ut_text)
                    sw.save_message(self.post_id, ut_text)

                time.sleep(0.1)
                file_name = uu.pack_and_del(path)
                # проверка: в папке 1 zip с размером не менее 1Мб, созданный не более минуты назад
                size = uu.check(path)
                fill_thread.target = 100
                fill_thread.start()

                if size > 1:
                    try:
                        size = os.path.getsize(file_name)
                        ftp = FTP(logins.FTP_HOST)
                        response = ftp.login(logins.FTP_LOGIN, logins.FTP_PASS)

                        print('Ответ FTP сервера:', response)
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
            fill_thread3.target = fill_thread3.target + step_thread3
            fill_thread3.start()
        if fill_thread3.target > 90:
            fill_thread3.target = 100
            fill_thread3.start()


fill_thread = CThread(form.progressBar_5.value())
fill_thread.valueChanged.connect(form.progressBar_5.setValue)
fill_thread2 = CThread(form.progressBar_6.value())
fill_thread2.valueChanged.connect(form.progressBar_6.setValue)
fill_thread3 = CThread(form.progressBar_7.value())
fill_thread3.valueChanged.connect(form.progressBar_7.setValue)

ContentCheckAndUpload_instance = ContentCheckAndUpload()


def progress(all_blocks):
    all_blocks = math.ceil(all_blocks)

    def callback(block):
        callback.blocks_uploaded += 1
        callback.uploaded += len(block)
        uploaded = round(100 * callback.blocks_uploaded / all_blocks)
        fill_thread2.target = uploaded
        fill_thread2.start()

        # print(f'Загружено {round(100 * callback.blocks_uploaded / all_blocks)} %')

    callback.blocks_uploaded = 0
    callback.uploaded = 0
    return callback


def tab_load_data():
    ContentCheckAndUpload_instance.start()


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


def add_new_thread_in_project_list(project_id):
    all_threads = sw.select_all_threads_in_project(project_id)
    form.listWidget.clear()
    content_type_list = {0: 'Pics', 1: 'Vids'}
    for elem in all_threads:
        current_dir = str(elem[2]) + str(elem[3])
        item = QtWidgets.QListWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEnabled)
        item.setCheckState(QtCore.Qt.Unchecked)

        if uu.dir_exist(current_dir):
            if uu.check_dir(current_dir):
                item.setCheckState(QtCore.Qt.Checked)
                item.setFlags(
                    QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsEnabled)
                thread_info = str(elem[0]) + '||     ' + elem[1] + '   ' + content_type_list[
                    elem[5]] + '    ||  WORK folder:  ' + str(elem[2]) + str(elem[3]) + 20 * ' . ' + 'READY!'
                item.setText(thread_info)
                form.listWidget.addItem(item)
            else:
                thread_info = str(elem[0]) + '||     ' + elem[1] + '   ' + content_type_list[
                    elem[5]] + '    ||  WORK folder:  ' + str(elem[2]) + str(elem[3]) + 50 * ' . ' + 'empty!'
                item.setText(thread_info)
                form.listWidget.addItem(item)
        else:
            thread_info = str(elem[0]) + '||     ' + elem[1] + '   ' + content_type_list[
                elem[5]] + '    ||  ' + 30 * ' .' + 'No folder ' + current_dir + ' in Resource'
            item.setText(thread_info)
            form.listWidget.addItem(item)


def save_place_thread():
    if form.comboBox_2.currentIndex() and form.comboBox_3.currentIndex() and form.lineEdit_17.text().strip() \
            and form.lineEdit_18.text().strip():
        thread_id = form.comboBox_2.currentData()
        place_id = form.comboBox_3.currentData()
        place_type = form.comboBox_5.currentIndex()
        link_url = form.lineEdit_17.text().strip()
        description = form.lineEdit_18.text().strip()
        sw.save_place_thread(thread_id[0], place_id[0], link_url, place_type, description)

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
    form.lineEdit_17.setText('')
    form.lineEdit_18.setText('')

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
    existing_id = form.label_54.text().strip()
    content_type = form.comboBox_6.currentIndex()
    if name and prefix and starting_id:
        try:
            if existing_id:
                sw.update_thread(existing_id, name, prefix, starting_id, content_type)
            else:
                sw.new_thread(name, prefix, starting_id, PROJECT_ID, content_type)
            try:
                uu.create_dir(prefix + str(starting_id))
                add_new_thread_in_project_list(PROJECT_ID)
            except:
                print('Создать папку для записи не удалось!')
        except:
            print('Ошибка записи в БД')
    else:
        print('Данных недосточно!')


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
    z = form.comboBox_5.currentIndex()
    if isinstance(x, tuple) and isinstance(y, tuple):
        if sw.select_current_place_thread(x[0], y[0], z):
            url_link, place_type, description = sw.select_current_place_thread(x[0], y[0], z)
            form.lineEdit_17.setText(url_link)
            form.lineEdit_18.setText(description)
            if int(place_type) != z:
                form.lineEdit_17.clear()
                form.lineEdit_18.setText(x[1].replace(' ', '') + ' ' + 'Pics')
            else:
                form.comboBox_5.setCurrentIndex(int(place_type))
        else:
            form.lineEdit_17.clear()
            form.lineEdit_18.setText(x[1].replace(' ', '') + ' ' + 'Pics')
    elif isinstance(x, tuple):
        form.lineEdit_18.setText(x[1].replace(' ', '') + ' ' + 'Pics')


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
form.comboBox_5.currentIndexChanged.connect(load_current_place_thread)


def save_place():
    print('Save place')
    try:
        name = form.lineEdit_14.text().strip()
        login_url = form.lineEdit_15.text().strip()
        inputs = form.textEdit_3.toPlainText().strip()
        userid = form.lineEdit_16.text().strip()
        type_place = form.comboBox_4.currentIndex()
        if name and login_url and inputs and userid:

            if form.label_34.text():
                sw.update_place_in_bd(name, login_url, inputs, userid, form.label_34.text(), type_place)

            else:
                sw.save_place_in_bd(name, login_url, inputs, userid, type_place, PROJECT_ID)
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
        zip_id = x[0].strip()
        post_id = x[2].strip()

        form.label_44.setText(thread_id)
        form.label_46.setText(zip_id)
        form.label_42.setText(post_id)

        zip_url = sw.select_url_from_zip(zip_id)
        form.label_48.setText(zip_url[0])

        places_for_post = sw.select_places_for_thread(thread_id)

        place_names = []
        type_place_dict = dict()
        for elem in places_for_post:
            place_name = sw.select_name_from_places(elem[1])
            place_name = str(place_name[0]) + ': ' + str(elem[5])
            place_names.append(place_name)
            type_place_dict[place_name] = elem[4]

        place_names.sort()
        counter = 0
        for elem in place_names:
            checkbox_name = 'checkBox_u' + str(counter)
            obj = getattr(form, checkbox_name)  # !!
            obj.setText(elem)
            obj.setChecked(True)
            obj.show()

            if type_place_dict[elem] == 0:
                obj.setChecked(True)
            else:
                obj.setChecked(False)
            counter += 1
            checkbox_dict[elem] = checkbox_name
        for x in range(counter, 29):  # Прячем лишние чекбоксы
            checkbox_name = 'checkBox_u' + str(x)
            obj = getattr(form, checkbox_name)
            obj.hide()
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
    checkbox_dict = dict()
    try:
        checkbox_dict = view_info_from_cell(row)
    except:
        pass
    return checkbox_dict


def delete_thread_from_place():
    thread_id = form.comboBox_2.currentData()[0]
    place_id = form.comboBox_3.currentData()[0]
    sw.delete_tfp(thread_id, place_id)
    places_for_post_load(PROJECT_ID)


class CurrentPost():
    def __init__(self):
        self.zip_url = form.label_48.text()
        self.zip_id = form.label_46.text()
        self.post_id = form.label_42.text()
        self.thread_id = form.label_44.text()
        self.post_name = form.lineEdit.text()
        self.size_and_quality = form.lineEdit_5.text()
        self.date = form.lineEdit_9.text()
        self.pics_code = form.textEdit.toPlainText()
        self.body_post = ''
        self.folder_name = form.lineEdit_2.text()

    def view_info(self):
        print(self.pics_code)

    def lets_post(self, check_box_dict):
        places_for_post = sw.select_places_for_thread(self.thread_id)
        lucky_posts = 0
        thread_id = 0
        for elem in places_for_post:
            info_for_login = sw.search_data_for_login(elem[1])
            checkbox_name = check_box_dict[info_for_login[0][1] + ': ' + elem[5]]
            obj = getattr(form, checkbox_name)

            if obj.isChecked():  # Work with checked box only!
                print('Название места куда постим:', info_for_login[0][1])

                # img_upload.login_on_place(elem[3], self.body_post, info_for_login)  # РАБОЧИЙ ВЫЗОВ ФУНКЦИИ ЛОГИНА-ПОСТА!
                post = img_upload.LoginAndPosting(elem[3], self.body_post, info_for_login)
                edit_post_url = post.connect_to()

                if post.check_adding_new_post(self.zip_url):
                    good_news = f'++++++  Новый пост на {info_for_login[0][1]} найден успешно! ++++++'
                    print(good_news)
                    form.textEdit_4.setText(form.textEdit_4.toPlainText() + good_news)
                    if sw.insert_forum_post(elem[1], self.thread_id, self.post_id, self.zip_id, edit_post_url):
                        lucky_posts += 1
                        thread_id = elem[2]
                        print('запись о новом посте в БД совершена успешно!')
                    obj.setCheckState(QtCore.Qt.Unchecked)
                else:
                    bad_news = f'------  Пост на {info_for_login[0][1]} найти не удалось! ------'
                    print(bad_news)
                    form.textEdit_4.setText(form.textEdit_4.toPlainText() + bad_news)
        print(f'Всего: успешно размещено {lucky_posts} постов из {len(check_box_dict)}.')
        if lucky_posts > 0:
            sw.starting_id(thread_id, '20')

    def make_body(self):

        if 'vd_' in self.folder_name:
            self.body_post = 'Video: ' + self.post_name
            self.body_post = self.body_post + '\n' + self.pics_code + '\n [URL=' + self.zip_url + '][B]Download from ' + logins.FILE_HOST_NAME + '[/B][/URL]'


        else:
            if self.date.strip() != '':
                self.date = 'Date: ' + self.date + '\n'
            else:
                self.date = ''

            self.body_post = 'Set: ' + self.post_name + '\nPics, archive size: ' + self.size_and_quality
            self.body_post = self.body_post + '\n' + self.date + '\n' + self.pics_code + '\n [URL=' + self.zip_url + '][B]Download from ' + logins.FILE_HOST_NAME + '[/B][/URL]'


def send_post():
    current_post = CurrentPost()
    current_post.make_body()
    current_post.lets_post(checkbox_dict)


form.pushButton_4.clicked.connect(send_post)

form.pushButton_delete.clicked.connect(delete_thread_from_place)

form.tableWidget.cellDoubleClicked.connect(view_cell)


def load_thread_data_for_edit():
    itemNumber = form.listWidget.currentRow()
    item = form.listWidget.item(itemNumber)
    thread_id = item.text().split('||')[0]
    data = sw.select_one_thread_from_threads(thread_id)
    form.lineEdit_11.setText(data[0][1])
    form.lineEdit_12.setText(data[0][2])
    form.lineEdit_13.setText(str(data[0][3]))
    form.label_54.setText(str(data[0][0]))
    if data[0][5]:
        form.comboBox_6.setCurrentIndex(int(data[0][5]))
    else:
        form.comboBox_6.setCurrentIndex(0)


form.listWidget.itemDoubleClicked.connect(load_thread_data_for_edit)

window.show()
app.exec()
