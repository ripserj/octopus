import time
import zipfile
import os

ROOT_DIR = 'Resourse'

def check_dir(current_dir):

    check_dir = os.path.join(ROOT_DIR, current_dir)
    return len(os.listdir(check_dir))


def dir_exist(folder):
    folder = ROOT_DIR+'\\'+folder
    if not os.path.isdir(folder):
        return False
    else:
        return True

def create_dir(folder):
    folder = ROOT_DIR+'\\'+folder
    if not os.path.isdir(folder):
        os.mkdir(folder)


def upload_txt(file_txt, header):
    with open(file_txt, 'r') as f:
        pics_block = f.read()
    with open(file_txt, 'w') as f:
        f.write(header)
        f.write(pics_block)


def unpack_zip(path, file_name):
    with zipfile.ZipFile(os.path.join(path, file_name), 'r') as z:
        z.extractall(os.path.join(path, file_name[0:-4]))
    z.close()

    time.sleep(0.2)
    print("Удаляю " + os.path.join(path, file_name))
    try:
        os.remove(os.path.join(path, file_name))
    except:
        print('Не удалилось!')
        exit()

    return os.path.join(path)


def pack_and_del(path):
    arc_file_name = path.split("\\")
    arc_file = os.path.join(path, arc_file_name[len(arc_file_name) - 1] + ".zip")
    with zipfile.ZipFile(arc_file, 'w') as myzip:
        for root, dirs, files in os.walk(path):  # Список всех файлов и папок в директории folder
            for file_name in files:
                if ".zip" not in file_name:
                    temp_file_name = os.path.join(path, file_name)
                    myzip.write(temp_file_name, file_name)
                    time.sleep(0.02)

    return arc_file


def check(path):
    target_zip = os.path.split(path)[1] + '.zip'

    if target_zip in os.listdir(path):
        elem_path = os.path.join(path, target_zip)
        size = os.path.getsize(elem_path)
        size = round(size / 1048576, 1)
        print(f'Архив с именем {target_zip} найден, размер - {size}Mb')
        return size
    else:
        print("Архива с верным именем НЕ ОБНАРУЖЕНО!")
        exit()
