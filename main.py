import os
import random
import shutil
import time
import zipfile
from PIL import Image

import cv2

import sql_work as sw
import unzip_unrar as uu
import re
import datetime
import img_upload
from logins import ROOT_DIR, YEAR_IN_THE_PAST, BACKUP_DIR

now = datetime.datetime.now()


def reset_data():
    print('Clear data in ', ROOT_DIR)
    if os.path.isdir(ROOT_DIR):
        shutil.rmtree(ROOT_DIR)
    time.sleep(0.05)
    if not os.path.isdir(ROOT_DIR):
        os.mkdir(ROOT_DIR)
        folders_in_project = sw.select_folders_in_current_project()
        for elem in folders_in_project:
            full_path = os.path.join(ROOT_DIR, elem[0] + str(elem[1]))
            os.mkdir(full_path)
    print('Working folder update.....SUCCESS!')



def clear_all(home):
    for root, dirs, files in os.walk(home):
        for elem in files:  # ищем архив и переносим его в корень
            source = os.path.join(root, elem)
            if '.zip' in elem:
                print('Есть зип архив ' + elem)
                target = os.path.join(home, elem)
                try:
                    os.rename(source, target)
                    print('Архив перемещен!')
                except:
                    print('файл архива не перемещен!')
                time.sleep(1)
            else:  # удаляем все кроме zip-ов
                time.sleep(0.02)
                os.remove(source)


def get_date_from_zip(arc_file):
    date_from_zip = []
    file_zip = zipfile.ZipFile(arc_file)
    for file in file_zip.namelist():
        if '.jpg' in file.lower() or '.jpeg' in file.lower():
            all_file_info = file_zip.getinfo(file)
            date_from_zip.append(all_file_info.date_time[0:3])
        time.sleep(0.01)
    file_zip.close()
    returned_date = ''
    if len(date_from_zip):
        date_from_zip.sort()
        x = date_from_zip[0]
        if x[1] < 10:
            month = '0' + str(x[1])
        else:
            month = str(x[1])
        if x[2] < 10:
            day = '0' + str(x[2])
        else:
            day = str(x[2])
        year_temp = str(x[0])
        year = str(year_temp[2:4])
        returned_date = month + '/' + day + '/' + year
    print(returned_date)
    return returned_date


def search_date_in_name(may_be_date):
    # нужен формат даты 01/24/16
    year = ""
    if len(may_be_date) == 8:  # найдена дата из 8 цифр
        for i in range(YEAR_IN_THE_PAST, now.year + 1, 1):
            if str(i) in may_be_date:
                year = str(i)[2:4]
                may_be_date = may_be_date.replace(str(i), '')
                if int(may_be_date[0:2]) < 13 and int(may_be_date[2:4]) < 32:
                    return may_be_date[0:2] + "/" + may_be_date[2:4] + "/" + year
                elif int(may_be_date[2:4]) < 13 and 32 > int(may_be_date[0:2]) > 12:
                    return may_be_date[2:4] + "/" + may_be_date[0:2] + "/" + year
                else:
                    print("Валидная дата не обнаружена...")
                    return "Валидная дата не обнаружена..."

        else:
            print("Валидный год не обнаружен...")
            return "Валидный год не обнаружен..."
    else:
        return "No data"


def check_and_rename(current_dir):
    folder = ROOT_DIR + '\\' + current_dir
    type_of_file = ''
    files = os.listdir(folder)
    for elem in files:  # ищем видео и переименовываем в соответствии с названием папки
        extensions = ['.mp4', '.wmv', '.avi']
        if any(x in elem.lower() for x in extensions):
            type_of_file = elem[-3:].upper()

            current_file = os.path.join(folder, elem)

            size_in_bts = os.path.getsize(current_file)
            size = round(size_in_bts / 1048576, 1)

            new_file = os.path.join(folder, current_dir + '.' + type_of_file)
            os.rename(current_file, new_file)
            cap = cv2.VideoCapture(new_file)
            length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            duration = round(length / fps)
            hours = '0' + str(int(duration // 3600))
            duration = duration - 3600 * int(duration // 3600)

            if int(duration / 60) < 10:
                minutes = '0' + str(int(duration / 60))
            else:
                minutes = str(int(duration / 60))
            if int(duration % 60) < 10:
                seconds = '0' + str(int(duration % 60))
            else:
                seconds = str(int(duration % 60))

            print(f'всего кадров:{length}, разрешение: {width}х{height}, FPS: {fps}')
            print(f'длительность: {hours}:{minutes}:{seconds}')

            if width > height:
                num_of_screens = 6
                pics_in_row = 2
            else:
                num_of_screens = 6
                pics_in_row = 3
            step = int(length / (num_of_screens + 1))
            images = []
            counter = 0
            for x_frame in range(step, length - 20, step):
                counter += 1
                x_frame = x_frame + random.randint(-50, 50)
                cap.set(1, x_frame)
                ret, frame = cap.read()
                jpg_name = str(counter) + "_" + str(x_frame) + ".jpg"
                jpg_path = os.path.join(folder, jpg_name)
                images.append(jpg_name)
                cv2.imwrite(jpg_path, frame)
            cap.release()
            # двлее из полученных фоток делаем скринлист

            # beetwen_pics = int(width / 200)
            # total_width = width * pics_in_row + beetwen_pics * (pics_in_row + 1)
            # max_height = height * (int(num_of_screens / pics_in_row)) + beetwen_pics * (
            #         int(num_of_screens / pics_in_row) + 1)
            #
            # x_offset = beetwen_pics
            # y_offset = beetwen_pics
            # new_im = Image.new('RGB', (total_width, max_height), (255, 255, 255))
            # counter = 0
            # for image in images:
            #     im = Image.open(image)
            #     new_im.paste(im, (x_offset, y_offset))
            #     x_offset += im.size[0] + beetwen_pics
            #     counter += 1
            #     if counter % pics_in_row == 0:
            #         y_offset += height + beetwen_pics
            #         x_offset = beetwen_pics
            #
            # jpg_path = os.path.join(folder, current_dir + "_scr.jpg")
            # new_im.save(jpg_path)

    return type_of_file, f'{hours}:{minutes}:{seconds}', f'{width}х{height}', f'{fps}', f'{size} Mb', folder, elem, images, new_file, size_in_bts, pics_in_row


# params = []
# params = check_and_rename('vd_fmdinl1000')
# for elem in params:
#     print(elem)


def rename_files(path, file_name, zip=0):
    date_from_pic_info_set = []
    date_from_file_info_set = []
    some_file_names = []
    for path_files, directories, files in os.walk(path):
        files.sort()
        counter = 0

        for file in files:
            counter += 1
            some_file_names.append(file)
            current_file_name = os.path.join(path_files, file)
            expansion = file.split(".")
            new_file_name = "2_" + str(counter) + "." + expansion[1]
            destination_file_name = os.path.join(path, new_file_name)
            if '.jpg' in current_file_name.lower():

                if zip == 0:
                    try:
                        t = os.path.getmtime(current_file_name)
                        date_from_file_info = datetime.date.fromtimestamp(t)
                        if date_from_file_info:
                            date_from_file_info_set.append(date_from_file_info)
                    except:
                        print("не удалось считать дату файла")

                    try:
                        date_from_pic_info = Image.open(current_file_name)._getexif()[36867]

                        if date_from_pic_info:
                            date_temp = date_from_pic_info.strip().split(' ')
                            date_from_pic_info_set.append(date_temp[0])
                    except:
                        pass
                elif zip == 1:
                    try:
                        date_from_pic_info = Image.open(current_file_name)._getexif()[36867]
                        if date_from_pic_info:
                            date_temp = date_from_pic_info.strip().split(' ')
                            date_from_pic_info_set.append(date_temp[0])
                    except:
                        pass

            time.sleep(0.01)
            os.rename(current_file_name, destination_file_name)
            time.sleep(0.01)
    date_from_pic_info_set.sort()
    date_from_file_info_set.sort()
    returned_date_from_pic_info = ''
    returned_date_from_file_info = ''
    if date_from_pic_info_set:
        temp_date = date_from_pic_info_set[0].split(':')
        returned_date_from_pic_info = temp_date[1] + '/' + temp_date[2] + '/' + temp_date[0][2:4]
    # print(f"ДАТА НАЙДЕНАЯ В ЗАГОЛОВКАХ ФОТО  - {returned_date_from_pic_info}")

    if date_from_file_info_set and zip == 0:
        if date_from_file_info_set[0].month < 10:
            month = '0' + str(date_from_file_info_set[0].month)
        else:
            month = str(date_from_file_info_set[0].month)
        if date_from_file_info_set[0].day < 10:
            day = '0' + str(date_from_file_info_set[0].day)
        else:
            day = str(date_from_file_info_set[0].day)
        year = str(date_from_file_info_set[0].year)
        returned_date_from_file_info = month + '/' + day + '/' + year[2:4]

        # print(f"ДАТА НАЙДЕНАЯ В ИНФО-ФАЙЛОВ  - {returned_date_from_file_info}")

    time.sleep(0.01)
    delete_path = os.path.join(path, file_name)
    time.sleep(0.01)
    shutil.rmtree(delete_path)
    return returned_date_from_pic_info, returned_date_from_file_info, some_file_names


def check_data_in_folder(folder):
    path = os.path.join(ROOT_DIR, folder)
    if len(os.listdir(path)) == 1:  # В целевой папке один файл или папка
        return True, path
    else:
        return False, path


def set_name_search(path):
    set_name = ""
    set_date = ""
    for file_name in os.listdir(path):
        set_name = ''.join(re.findall('[a-zA-Z _-]', file_name)).replace('-', ' ').replace('_', ' ').strip()
        may_be_date = ''.join(re.findall('[\d]', file_name))
        set_date = search_date_in_name(may_be_date)
        set_name = set_name.replace("zip", "")
    return set_date, set_name


def unpack(path):
    file_names = []
    photo_date, file_date = '', ''
    for file_name in os.listdir(path):
        if '.zip' in file_name.lower():

            print('Есть zip архив. Попытка вытащить даты из файлов архива...', os.path.join(path, file_name))
            date_from_file_info = get_date_from_zip(os.path.join(path, file_name))
            print(f"ФАЙЛЫ ВНУТРИ АРХИВА ИМЕЮТ ДАТУ: {date_from_file_info}")

            print('Есть zip архив. Приступаю к распаковке...', os.path.join(path, file_name))

            path = uu.unpack_zip(os.path.join(path), file_name)

            file_name = file_name[0:-4]
            print('Распаковка завершена...')

            print("Архив удален, проверяю наличие вложенных папок...")
            photo_date, file_date, file_names = rename_files(path, file_name, zip=1)
            file_date = date_from_file_info
            # num_of_pics = img_upload.select_and_send_pics(path)

        else:

            print("Архивов в папке нет, проверяю наличие вложенных папок...")
            print(path, file_name)

            photo_date, file_date, file_names = rename_files(path, file_name)
            # num_of_pics = img_upload.select_and_send_pics(path)

    return photo_date, file_date, file_names


def load_data_main():
    for elem in os.listdir(ROOT_DIR):

        path = os.path.join(ROOT_DIR, elem)
        if os.path.isdir(path):  # является ли путь в корне папкой, если да, то заходим внутрь, если нет - то игнорим
            print('===================================================================================================')
            print("Папка в обработке:  ", path)
        else:
            continue
        set_name = ""
        set_date = ""
        num_of_pics = ""
        info = ""

        for file_name in os.listdir(path):

            if len(os.listdir(path)) == 1:  # В целевой папке один файл или папка

                set_name = ''.join(re.findall('[a-zA-Z _-]', file_name)).replace('-', ' ').replace('_', ' ').strip()
                may_be_date = ''.join(re.findall('[\d]', file_name))
                set_date = search_date_in_name(may_be_date)
                set_name = set_name.replace("zip", "")
                print(set_date)
                if len(set_name) < 4:
                    set_name = "NO"
                if set_name != "NO":
                    info = "Set: " + set_name + "\n"
                else:
                    info = ""
                if set_date != "No data":
                    info = info + "Date: " + set_date + "\n"

                if '.zip' in file_name.lower():

                    print('Есть zip архив. Попытка вытащить даты из файлов архива...', os.path.join(path, file_name))
                    date_from_file_info = get_date_from_zip(os.path.join(path, file_name))
                    print(f"ФАЙЛЫ ВНУТРИ АРХИВА ИМЕЮТ ДАТУ: {date_from_file_info}")

                    print('Есть zip архив. Приступаю к распаковке...', os.path.join(path, file_name))

                    path = uu.unpack_zip(os.path.join(path), file_name)

                    file_name = file_name[0:-4]
                    print('Распаковка завершена...')

                    print(ROOT_DIR, "----------", elem)

                    print("Архив удален, проверяю наличие вложенных папок...")
                    rename_files(path, file_name, zip=1)
                    num_of_pics = img_upload.select_and_send_pics(path)

                else:

                    print("Архивов в папке нет, проверяю наличие вложенных папок...")
                    print(path, file_name)
                    rename_files(path, file_name)
                    num_of_pics = img_upload.select_and_send_pics(path)
            else:
                print("В папке слишком много файлов! Проверьте контент!")

            print(set_name, set_date)

        arc_file = uu.pack_and_del(path)
        # проверка: в папке 1 zip с размером не менее 1Мб, созданный не более минуты назад
        size = uu.check(path)
        if size > 1:
            info = info + num_of_pics + "size: " + str(size) + "Mb\n\n"
            uu.upload_txt("upload-test.txt", info)

            img_upload.ftp_upload(arc_file)
            temp_name = arc_file.split('\\')
            name = temp_name[len(temp_name) - 1]
            sw.zip_in_base(name, str(size))
        else:
            print("Программа прервана, проверьте папку " + path)
    print('Запускаю очистку папок и создание бекапа!')
    clear_all(ROOT_DIR)
