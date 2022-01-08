import math
import requests
import os
from PIL import Image
import random
import json
import time
from random import randint
from ftplib import FTP
import logins
from bs4 import BeautifulSoup

ROOT_DIR = 'Resourse'


def login_host(filename=False):
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

    time.sleep(randint(3, 8))
    print("=================================================================")
    r = session.get(logins.FILE_HOST_GET, headers=headers)
    if filename:
        data = {
            'op': 'files',
            'key': filename,
        }
        response = session.post(logins.FILE_HOST_MAIN_URL, data=data, headers=headers)

        soup = BeautifulSoup(response.text, features="html.parser")
        if soup.find_all('a', {'title': filename}):
            return True
        else:
            return False
    else:
        return r.text


# login_host()   # функция логина-проверки на файл-хосте рабочая!!!

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


def get_token(text, token):
    soup = BeautifulSoup(text, features="html.parser")
    key = ''
    for x in soup.find_all('input', {'name': token}):
        key = x.get('value')
    return key


class LoginAndPosting():
    def __init__(self, url, body_post, info_for_login):
        self.url_for_post = url
        self.forum_type = 0
        self.login_url = None
        self.body_post = body_post
        self.info_for_login = info_for_login
        self.auth, self.login_url, self.forum_type, self.user_id = self.check_data(self.info_for_login)
        self.session = None

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            'Accept-Encoding': "gzip, deflate, sdch",
        }
    def dice_roll_and_sleep(self):
        time.sleep(randint(50, 250) * 0.01)

    def get_tok(self, text, token):
        soup = BeautifulSoup(text, features="html.parser")
        key = ''
        for x in soup.find_all('input', {'name': token}):
            key = x.get('value')
        return key

    def check_data(self, data):
        data_new = dict()
        for x in data[0][4].replace("'", "").split(','):
            y = x.split(':')
            data_new[y[0].strip()] = y[1].strip()
        print('data_new:', data_new)
        return data_new, data[0][2], int(data[0][7]), data[0][5]

    def connect_to(self):
        print('Attempt to login on: ', self.url_for_post)
        self.session = requests.Session()
        self.session.headers = self.headers
        if self.forum_type == 0:
            print('Its vBulletin type forum!', self.url_for_post )
            response = self.session.post(self.login_url, data=self.auth)
            print(response)
            self.dice_roll_and_sleep()
            r = self.session.get(self.url_for_post, headers=self.headers)
            token = self.get_tok(r.text, 'securitytoken')
            post_id = ''
            if 'p=' in self.url_for_post:
                post_num = self.url_for_post.split('p=')
                post_id = post_num[1]

            payload = {'securitytoken': token, 's': '', 'do': 'postreply', 't': '', 'p': post_id,
                       'specifiedpost': '0', 'posthash': '', 'poststarttime': '', 'loggedinuser': self.user_id,
                       'multiquoteempty': '', 'wysiwyg': '0', 'message': self.body_post}
            response = self.session.post(self.url_for_post, data=payload, headers=self.headers)  # Временно заблокировал постинг
            self.dice_roll_and_sleep()
            print('Posting answer:', response)

        elif self.forum_type == 1:
            print('Its XenForo type forum!')
            r = self.session.get(self.login_url, headers=self.headers)
            token = self.get_tok(r.text, '_xfToken')
            redirect = self.get_tok(r.text, '_xfRedirect')

            self.auth['_xfToken'] = token
            self.auth['_xfRedirect'] = redirect

            self.dice_roll_and_sleep()

            response = self.session.post(self.login_url, data=self.auth)
            self.dice_roll_and_sleep()

            r = self.session.get(self.url_for_post, headers=self.headers)
            token = self.get_tok(r.text, '_xfToken')
            redirect = self.get_tok(r.text, '_xfRedirect')  # Пока не требуется

            self.dice_roll_and_sleep()

            payload = {'_xfToken': token, 's': '', 'do': 'postreply', 't': '',
                       'specifiedpost': '0', 'posthash': '', 'poststarttime': '',
                       'multiquoteempty': '', 'wysiwyg': '0', 'message': body_post}

            response = self.session.post(self.url_for_post + "add-reply", data=payload, headers=self.headers)
            print(response)





        elif self.forum_type == 2:
            print('Its SMF type forum!')
            r = self.session.get(self.login_url, headers=self.headers)
            print(r.text)

    def post_to(self):
        pass


if __name__ == "__main__":
    new_1 = LoginAndPosting(1, 2, 3)


def login_on_place(url, body_post, info_for_login):
    auth = dict()
    for elem in info_for_login:
        login_url = elem[2]
        login_data = elem[4]
        userid = elem[5]
        place_type = elem[7]

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
    print(place_type)

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

    if place_type == '0':
        print('vBulletin type')
        response = session.post(login_url, data=auth)
        print(response)
        time.sleep(randint(1, 3))

        r = session.get(url, headers=headers)
        print(r)
        token = get_token(r.text, 'securitytoken')

        if 'p=' in url:
            post_num = url.split('p=')

        payload = {'securitytoken': token, 's': '', 'do': 'postreply', 't': '', 'p': post_num[1],
                   'specifiedpost': '0', 'posthash': '', 'poststarttime': '', 'loggedinuser': userid,
                   'multiquoteempty': '', 'wysiwyg': '0', 'message': body_post}

        print(payload)

        response = session.post(url, data=payload, headers=headers)  # Временно заблокировал постинг
        print(response)
        time.sleep(1, 4)



    elif place_type == '1':
        print('XenForo type')

        r = session.get(login_url, headers=headers)

        token = get_token(r.text, '_xfToken')
        redirect = get_token(r.text, '_xfRedirect')

        auth['_xfToken'] = token
        auth['_xfRedirect'] = redirect

        time.sleep(randint(1, 3))

        response = session.post(login_url, data=auth)
        time.sleep(randint(1, 3))
        r = session.get(url, headers=headers)
        token = get_token(r.text, '_xfToken')
        redirect = get_token(r.text, '_xfRedirect')  # Пока не требуется

        time.sleep(randint(1, 3))

        payload = {'_xfToken': token, 's': '', 'do': 'postreply', 't': '',
                   'specifiedpost': '0', 'posthash': '', 'poststarttime': '',
                   'multiquoteempty': '', 'wysiwyg': '0', 'message': body_post}

        response = session.post(url + "add-reply", data=payload, headers=headers)  # Временно заблокировал постинг
        print(response)

        ##  НЕ ДОПИСАЛ ДАЛЕЕ
