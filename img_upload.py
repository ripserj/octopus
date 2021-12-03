import math
import requests
import os
from PIL import Image
import random
import json
import time
from random import randint
from ftplib import FTP
import sql_work as sw
import logins
from bs4 import BeautifulSoup

ROOT_DIR = 'Resourse'


def login_host():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        'Accept-Encoding': "gzip, deflate, sdch",
    }

    auth = {
        'email': logins.FILE_HOST_LOGIN,
        'password': logins.FILE_HOST_PASS,
        'op': 'login',
        'redirect': '',
        'rand': '',

    }

    session = requests.Session()
    session.headers = headers

    response = session.post(logins.FILE_HOST_URL, data=auth, headers=headers)
    # print(response.text)

    time.sleep(randint(10, 15))
    print("=================================================================")

    r = session.get(
        logins.FILE_HOST_GET,
        headers=headers)
    # print(r.text)
    return r.text


# login_host()   # функция логина рабочая!!!

def progress(all_blocks):
    all_blocks = math.ceil(all_blocks)

    def callback(block):
        callback.blocks_uploaded += 1
        callback.uploaded += len(block)

        print(f'Загружено {round(100 * callback.blocks_uploaded / all_blocks)} %')

    callback.blocks_uploaded = 0
    callback.uploaded = 0
    return callback


def ftp_upload(file_name):
    size = os.path.getsize(file_name)
    ftp = FTP(logins.FTP_HOST)
    response = ftp.login(logins.FTP_LOGIN, logins.FTP_PASS)

    print(response)
    with open(file_name, 'rb') as f:
        ftp.storbinary('STOR ' + os.path.split(file_name)[1], f, 262144, progress(size / 262144))
    print("конец загрузки файла", file_name)


# ftp_upload('1.mp4')

# ftp_upload()  функция рабочая, можно допилить прогресс загрузки


def upload_img(elem, path):
    img_path = os.path.join(path, elem)
    url = logins.IMG_HOST
    payload = {'content_type': '0',
               'max_th_size': '300'}
    files = {
        'img': (elem, open(img_path, 'rb')),
        'content_type': '0',
        'max_th_size': '300'
    }
    headers = {}

    response = requests.request("POST", url, data=payload, files=files)

    to_python = json.loads(response.text)
    return to_python


def make_text_links(otbor, variant, mode='w'):
    pics_block = ""
    counter = 1
    for elem in otbor:
        if counter % variant == 0:
            pics_block = pics_block + ' [URL=show_url' + elem + '][IMG]th_url' + elem + '[/IMG][/URL]\n'
        else:
            pics_block = pics_block + ' [URL=show_url' + elem + '][IMG]th_url' + elem + '[/IMG][/URL]'
        counter += 1
    file_txt = "upload-test.txt"
    with open(file_txt, mode) as f:
        f.write(pics_block)


def check_pics(path):
    for file_name in os.listdir(path):
        file_low = file_name.lower()
        if ".jpg" not in file_low and ".gif" not in file_low and ".jpeg" not in file_low and ".png" not in file_low:
            time.sleep(0.1)
            os.remove(os.path.join(path, file_name))


def select_and_send_pics(path):
    check_pics(path)
    counter = len(os.listdir(path))
    all_pics_hor, all_pics_vert, otbor = [], [], []

    for file_name in os.listdir(path):
        im = Image.open(os.path.join(path, file_name))
        sizes = im.size
        if sizes[0] / sizes[1] < 0.9:
            all_pics_vert.append((file_name))
        elif sizes[0] / sizes[1] > 1.3:
            all_pics_hor.append((file_name))

    num_hor, num_vert = len(all_pics_hor), len(all_pics_vert)

    print(f"Всего картинок {counter}, вертикальных: {num_vert}, горизонтальных: {num_hor}")

    if num_vert + num_hor < 16:
        if num_vert > 6:
            random.shuffle(all_pics_vert)
            otbor = all_pics_vert[0:6]
            make_text_links(otbor, variant=3)


        elif num_vert <= 6 and num_hor >= 4:
            random.shuffle(all_pics_hor)
            otbor = all_pics_hor[0:4]
            make_text_links(otbor, variant=2)

    else:
        if num_hor / (num_hor + num_vert) >= 0.7:
            random.shuffle(all_pics_hor)
            otbor = all_pics_hor[0:6]
            make_text_links(otbor, variant=2)

        elif num_vert / (num_hor + num_vert) >= 0.7:
            random.shuffle(all_pics_vert)
            otbor = all_pics_vert[0:9]
            make_text_links(otbor, variant=3)
        else:
            print("НАДО МЕШАТЬ!")
            if num_hor > num_vert:

                random.shuffle(all_pics_hor)
                otbor = all_pics_hor[0:4]
                make_text_links(otbor, variant=2)
                random.shuffle(all_pics_vert)
                make_text_links(all_pics_vert[0:3], variant=3, mode='a')
                otbor.extend(all_pics_vert[0:3])
            else:
                random.shuffle(all_pics_hor)
                otbor = all_pics_hor[0:2]
                make_text_links(otbor, variant=2)
                random.shuffle(all_pics_vert)
                make_text_links(all_pics_vert[0:6], variant=3, mode='a')
                otbor.extend(all_pics_vert[0:6])



    return counter, otbor

def login_on_place(url, body_post, info_for_login):
    auth = dict()
    for elem in info_for_login:
        login_url = elem[2]
        login_data = elem[4]
        userid = elem[5]

    for elem in login_data.split(','):
        elem = elem.replace('\n', '')
        elem = elem.replace(' ', '')
        elem = elem.replace("'", '')
        print(type(elem))
        y = elem.split(':')
        print(y)
        auth[y[0]] = y[1]


    print(auth)

    print('Пробуем войти на ресурс: ', url)
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
        'Accept-Encoding': "gzip, deflate, sdch",
    }

    session = requests.Session()
    session.headers = headers

    response = session.post(login_url, data=auth)
    time.sleep(randint(1, 5))

    r = session.get(url, headers=headers)

    with open('log.html', 'w', encoding="utf-8") as f:
        f.write(r.text)
    f.close()

    soup = BeautifulSoup(r.text, features="html.parser")
    token = ''

    for x in soup.find_all('input', {'name': 'securitytoken'}):
        token = x.get('value')
        print(token)
    post_num = url.split('p=')


    payload = {'securitytoken': token, 's': '', 'do': 'postreply', 't': '', 'p': post_num[1],
               'specifiedpost': '0', 'posthash': '', 'poststarttime': '', 'loggedinuser': userid,
               'multiquoteempty': '', 'wysiwyg': '0', 'message': body_post}



    print(payload)
    print(url)

    response = session.post(url, data=payload, headers=headers)
    print(response)


##  НЕ ДОПИСАЛ ДАЛЕЕ
