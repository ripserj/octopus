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


def upload_img(elem, path, max_th_size=300):
    img_path = os.path.join(path, elem)
    url = logins.IMG_HOST
    payload = {'content_type': '0',
               'max_th_size': max_th_size}
    files = {
        'img': (elem, open(img_path, 'rb')),
        'content_type': '0',
        'max_th_size': max_th_size
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
            time.sleep(0.02)
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
            # print("НАДО МЕШАТЬ!")
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
        self.edit_post_url = None

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            'Accept-Encoding': "gzip, deflate, sdch",
        }

    def dice_roll_and_sleep(self):
        time.sleep(randint(50, 150) * 0.01)

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
        # print('data_new:', data_new)
        return data_new, data[0][2], int(data[0][7]), data[0][5]

    def find_last_post_vbb(self):
        self.dice_roll_and_sleep()
        try:
            split_url = self.login_url.split('login')
            search_url = split_url[0] + 'search.php?do=finduser&u=' + self.user_id
            r = self.session.get(search_url, headers=self.headers)
            position_temp = r.text.split('#post')
            position_temp2 = position_temp[1].split('"')
            edit_url = split_url[0] + 'editpost.php?do=editpost&p=' + position_temp2[0]
        except:
            edit_url = None
        return edit_url

    def find_last_post_vbbmods(self):
        self.dice_roll_and_sleep()
        try:
            split_url = self.login_url.split('login')
            search_url = split_url[0] + 'members/' + self.user_id + '.html'
            # print(search_url)
            r = self.session.get(search_url, headers=self.headers)
            position_temp = r.text.split('#post')[1].split('"')[0]
            edit_url = split_url[0] + 'editpost.php?do=editpost&p=' + position_temp
            # print(edit_url)
        except:
            edit_url = None
        return edit_url

    def find_last_post_xfr(self):
        self.dice_roll_and_sleep()
        try:
            split_url = self.login_url.split('login')
            search_url = split_url[0] + 'search/member?user_id=' + self.user_id
            r = self.session.get(search_url, headers=self.headers)
            position_temp = r.text.split('post-')
            position_temp2 = position_temp[1].split('"')
            edit_url = split_url[0] + 'posts/' + position_temp2[0] + '/edit'
        except:
            edit_url = None
        # print(edit_url)
        return edit_url

    def find_last_post_phpbb(self):
        self.dice_roll_and_sleep()
        try:
            split_url = self.login_url.split('ucp')
            search_url = split_url[0] + 'search.php?author_id=' + self.user_id + '&sr=posts'
            r = self.session.get(search_url, headers=self.headers)
            position_temp = r.text.split('#p')
            position_temp2 = position_temp[1].split('"')
            position_temp3 = position_temp[0].split('.php?')
            # print('СМ сюда')
            # print(position_temp3[len(position_temp3) - 1])
            position_temp4 = position_temp3[len(position_temp3) - 1].split('&')
            # print(position_temp4[0])
            edit_url = split_url[0] + 'posting.php?mode=edit&' + position_temp4[0] + '&p=' + position_temp2[0]
        except:
            edit_url = None
        return edit_url

    def find_last_post_smf(self):
        self.dice_roll_and_sleep()
        try:
            split_url = self.login_url.split('index.php')
            search_url = split_url[0] + 'index.php?action=profile;area=showposts;u=' + self.user_id
            r = self.session.get(search_url, headers=self.headers)
            position_temp = r.text.split('#msg')
            position_temp2 = position_temp[1].split('"')
            # print(position_temp2[0])  # номер поста
            position_temp3 = position_temp[0].split('topic=')
            position_temp4 = position_temp3[len(position_temp3) - 1].split('.')
            # print(position_temp4[0])  # номер топика

            edit_url = split_url[0] + 'index.php?action=post;msg=' + position_temp2[0] + ';topic=' + position_temp4[0]
        except:
            edit_url = None
        # print(edit_url)
        return edit_url

    def find_last_post_smf2(self):
        self.dice_roll_and_sleep()
        try:
            split_url = self.login_url.split('index.php')
            search_url = split_url[0] + 'index.php?action=profile;area=showposts;u=' + self.user_id
            r = self.session.get(search_url, headers=self.headers)
            position_temp = r.text.split('#msg')
            position_temp2 = position_temp[1].split('"')[0]
            # print(position_temp2)  # номер поста
            topic_search = r.text.split('/topic,')[1].split('.')[0]
            # print(topic_search)  # номер топика
            edit_url = split_url[0] + 'index.php?action=post;msg=' + position_temp2 + ';topic=' + topic_search
        except:
            edit_url = None
        # print(edit_url)
        return edit_url


    def find_last_post_unknownbb(self, username):
        self.dice_roll_and_sleep()
        try:
            split_url = self.login_url.split('login')

            search_url = split_url[0] + 'userposts-' + username
            # print(search_url)
            r = self.session.get(search_url, headers=self.headers)
            position_temp = r.text.split('highlight=#')
            position_temp2 = position_temp[1].split('"')
            edit_url = split_url[0] + 'posting.php?mode=editpost&p=' + position_temp2[0]
        except:
            edit_url = None
        return edit_url

    def check_adding_new_post(self, zip_link):
        self.dice_roll_and_sleep()
        try:
            r = self.session.get(self.edit_post_url, headers=self.headers)
            if zip_link in r.text:
                return True
            else:
                return False
        except:
            print(f'Проблемы с соединением к url: {self.edit_post_url}')

    def connect_to(self):
        print('Attempt to login on: ', self.url_for_post)
        self.session = requests.Session()
        self.session.headers = self.headers
        if self.forum_type == 0:
            #print('Its vBulletin type forum!', self.url_for_post)
            response = self.session.post(self.login_url, data=self.auth)
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
            response = self.session.post(self.url_for_post, data=payload,
                                         headers=self.headers)  # Временно заблокировал постинг
            self.dice_roll_and_sleep()
            self.edit_post_url = self.find_last_post_vbb()

        elif self.forum_type == 1:
            #print('Its XenForo type forum!')
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
                       'multiquoteempty': '', 'wysiwyg': '0', 'message': self.body_post}

            response = self.session.post(self.url_for_post + "add-reply", data=payload, headers=self.headers)
            self.edit_post_url = self.find_last_post_xfr()

        elif self.forum_type == 2:
            #print('Its phpBB v3x type forum!')
            r = self.session.get(self.login_url, headers=self.headers)

            token = self.get_tok(r.text, 'sid')
            self.auth['sid'] = token

            response = self.session.post(self.login_url, data=self.auth)
            self.dice_roll_and_sleep()

            r = self.session.get(self.url_for_post, headers=self.headers)
            topic_cur_post_id = self.get_tok(r.text, 'topic_cur_post_id')
            lastclick = self.get_tok(r.text, 'lastclick')
            creation_time = self.get_tok(r.text, 'creation_time')
            form_token = self.get_tok(r.text, 'form_token')
            subject = self.get_tok(r.text, 'subject')
            self.dice_roll_and_sleep()

            payload = {'addbbcode20': 100, 'topic_cur_post_id': topic_cur_post_id, 'lastclick': lastclick,
                       'post': 'Submit', 'attach_sig': 'on', 'show_panel': 'options-panel',
                       'creation_time': creation_time, 'message': self.body_post,
                       'form_token': form_token, 'subject': subject,
                       }
            # print(payload)
            response = self.session.post(self.url_for_post, data=payload, headers=self.headers)
            self.edit_post_url = self.find_last_post_phpbb()


        elif self.forum_type == 3:
            #print('Its SMF type forum!')
            r = self.session.get(self.login_url, headers=self.headers)
            smf_session_id = r.text.split("hashLoginPassword(this, '")[1].split("'")[0]
            smf_random_input = r.text.split("<input type=\"hidden\" name=\"hash_passwrd\" value=\"\" />"
                                            "<input type=\"hidden\" name=\"")[1].split("\"")[0]

            self.auth[smf_random_input] = smf_session_id
            self.dice_roll_and_sleep()
            response = self.session.post(self.login_url + '2', data=self.auth)
            self.dice_roll_and_sleep()

            r = self.session.get(self.url_for_post, headers=self.headers)
            seqnum = self.get_tok(r.text, 'seqnum')
            additional_options = self.get_tok(r.text, 'additional_options')
            last_msg = self.get_tok(r.text, 'last_msg')
            message_mode = self.get_tok(r.text, 'message_mode')
            subject = self.get_tok(r.text, 'subject')
            topic = self.get_tok(r.text, 'topic')

            payload = {smf_random_input: smf_session_id,
                       'seqnum': seqnum,
                       'additional_options': additional_options,
                       'last_msg': last_msg,
                       'notify': '0',
                       'message_mode': message_mode,
                       'sel_color': '',
                       'sel_size': '',
                       'sel_face': '0',
                       'icon': 'xx',
                       'tags': '',
                       'topic': topic,
                       'subject': subject,
                       'message': self.body_post}

            response = self.session.post(self.url_for_post.replace('post', 'post2'), data=payload, headers=self.headers)
            self.dice_roll_and_sleep()
            self.edit_post_url = self.find_last_post_smf()

        elif self.forum_type == 4:
            # print('Its phpBB 2.x type forum WITH Cookies!!!', self.url_for_post)
            # print(self.login_url, self.auth)
            r = self.session.get(self.login_url, headers=self.headers)
            pbb_sid = r.cookies[self.auth['cookie']]
            self.dice_roll_and_sleep()
            # print(self.login_url+"?sid=" + pbb_sid)
            # print(self.auth)

            response = self.session.post(self.login_url+"?sid=" + pbb_sid, data=self.auth, cookies=r.cookies)
            self.dice_roll_and_sleep()
            # with open('test2.html', 'w', encoding="utf-8") as f:
            #     f.write(response.text)
            # f.close()
            r = self.session.get(self.url_for_post, headers=self.headers)
            sid = self.get_tok(r.text, 'sid')
            t = self.get_tok(r.text, 't')

            payload = {'subject': '',
                       'post_icon': '0',
                       'tags': '',
                       'addbbcode20': '#444444',
                       'addbbcode22': '0',
                       'helpbox': 'Font size: [size=x-small]small text[/size]',
                       'mode': 'reply',
                       'sid': sid,
                       't': t,
                       'post': 'Submit',
                       'message': self.body_post}
            self.dice_roll_and_sleep()
            response = self.session.post(self.url_for_post, data=payload,
                                         headers=self.headers)  # Временно заблокировал постинг
            # with open('test1.html', 'w', encoding="utf-8") as f:
            #     f.write(response.text)
            # f.close()
            self.dice_roll_and_sleep()
            self.edit_post_url = self.find_last_post_unknownbb(self.auth['username'])

        elif self.forum_type == 5:
            # print('Its SMF v2.0.8 type forum!')
            r = self.session.get(self.login_url, headers=self.headers)
            smf_session_id = r.text.split("hashLoginPassword(this, '")[1].split("'")[0]
            smf_random_input = r.text.split("hashLoginPassword(this, '")[1].split("\"")[0]

            self.auth[smf_random_input] = smf_session_id
            self.auth['hash_passwrd'] = smf_session_id
            self.dice_roll_and_sleep()
            response = self.session.post(self.login_url + '2', data=self.auth)
            self.dice_roll_and_sleep()

            r = self.session.get(self.url_for_post, headers=self.headers)
            seqnum = self.get_tok(r.text, 'seqnum')
            additional_options = self.get_tok(r.text, 'additional_options')
            last_msg = self.get_tok(r.text, 'last_msg')
            message_mode = self.get_tok(r.text, 'message_mode')
            subject = self.get_tok(r.text, 'subject')
            topic = self.get_tok(r.text, 'topic')
            smf_session_var = r.text.split("sSessionVar: '")[1].split("',")[0]
            smf_session_id = r.text.split("sSessionId: '")[1].split("',")[0]

            payload = {smf_random_input: smf_session_id,
                       'seqnum': seqnum,
                       'additional_options': additional_options,
                       'last_msg': last_msg,
                       'notify': '0',
                       'message_mode': message_mode,
                       'sel_color': '',
                       'sel_size': '',
                       'sel_face': '0',
                       'icon': 'xx',
                       'tags': '',
                       'topic': topic,
                       'subject': subject,
                       'message': self.body_post,
                       smf_session_var: smf_session_id,

                       }

            response = self.session.post(self.url_for_post.replace('post', 'post2'), data=payload, headers=self.headers)
            self.dice_roll_and_sleep()
            self.edit_post_url = self.find_last_post_smf2()

        if self.forum_type == 6:
            #print('Its vBulletin type forum!', self.url_for_post)
            response = self.session.post(self.login_url, data=self.auth)
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
            response = self.session.post(self.url_for_post, data=payload,
                                         headers=self.headers)  # Временно заблокировал постинг
            self.dice_roll_and_sleep()
            self.edit_post_url = self.find_last_post_vbbmods()

        return self.edit_post_url

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
