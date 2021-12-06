import sqlite3

conn = sqlite3.connect('links.db')

cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS zips(
   zipid INT PRIMARY KEY,
   name TEXT,
   size TEXT,
   link TEXT);
   """)

cur.execute("""CREATE TABLE IF NOT EXISTS pics(
   picid INT PRIMARY KEY,
   name TEXT,
   thumb TEXT,
   show TEXT,
   post TEXT);   
   """)
cur.execute("""CREATE TABLE IF NOT EXISTS post(
   postid INT PRIMARY KEY,
   name TEXT,
   url TEXT,
   message TEXT);    
   """)

cur.execute("""CREATE TABLE IF NOT EXISTS projects(
   project_id INT PRIMARY KEY,
   name TEXT,
   date,
   about TEXT);    
   """)
conn.commit()

def update_post_info(post_id, zip_id, quantity):

    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    data_update = (quantity, zip_id, post_id)
    sqlite_param = """Update post set pics_quantity = ?, zip_id = ? where postid = ?"""
    cur.execute(sqlite_param, data_update)
    conn.commit()

def starting_id(prefix, starting_id):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    data_update = (starting_id+1, prefix, starting_id)
    sqlite_param = """Update threads set starting_id = ? where prefix = ?  and starting_id = ?"""
    cur.execute(sqlite_param, data_update)
    conn.commit()


def insert_zip_link(zip_link, zipfile):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    data_update = (zip_link, zipfile)
    sqlite_param = """Update zips set link = ? where name = ?"""
    cur.execute(sqlite_param, data_update)
    conn.commit()

def save_message(post_id, ut_text):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    data_update = (ut_text, post_id)
    sqlite_param = """Update post set message = ? where postid = ?"""
    cur.execute(sqlite_param, data_update)
    conn.commit()

def save_place_in_bd(name, login_url, inputs, userid, type_place, project_id):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    print(inputs)
    clear_string = ''
    for x in inputs.split(','):
        if clear_string:
            clear_string = clear_string+','+ x.strip()
        else:
            clear_string = x.strip()

    data_insert = (name, login_url, clear_string, userid, project_id, type_place)
    sqlite_param = """INSERT INTO forums(name, login_url, inputs, userid, project_id, type)
       VALUES(?, ?, ?, ?, ?, ?);"""
    cur.execute(sqlite_param, data_insert)
    conn.commit()


# r = dict()
# for elem in clear_string.split(','):
#     x = elem.split(':')
#     r[x[0]] = x[1]
# print(r)

def img_in_base(elem, th_url, show_url, postid):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    data_insert = (elem, th_url, show_url, postid)
    sqlite_param = """INSERT INTO pics(name, thumb, show, post) 
       VALUES(?, ?, ?, ?);"""
    cur.execute(sqlite_param, data_insert)
    conn.commit()


def zip_in_base(name, size):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    data_insert = (name, size)
    sqlite_param = """INSERT INTO zips(name, size) 
       VALUES(?, ?);"""
    cur.execute(sqlite_param, data_insert)
    last_id = cur.lastrowid
    conn.commit()
    return last_id

def new_project_in_base(name, about):
    data_insert = (name, about)
    sqlite_param = """INSERT INTO projects(name, about) 
       VALUES(?, ?);"""
    cur.execute(sqlite_param, data_insert)
    last_id = cur.lastrowid
    conn.commit()
    return last_id

def check_new_project_name(new_project_name):

    sql_select_query = """select * from projects where name like ?"""
    cur.execute(sql_select_query, (new_project_name,))
    records = cur.fetchall()
    if len(records)>0:
        return False
    else:
        return True

def new_thread(name, prefix, starting_id, project_id):
    data_insert = (name, prefix, starting_id, project_id)
    sqlite_param = """INSERT INTO threads(name, prefix, starting_id, project_id) 
       VALUES(?, ?, ?, ?);"""
    cur.execute(sqlite_param, data_insert)
    conn.commit()
    return True

def select_all_threads_in_project(project_id):
    sql_select_query = """select * from threads where project_id = ?"""
    cur.execute(sql_select_query, (project_id,))
    records = cur.fetchall()
    return records


def open_project():
    sql_select_query = """select * from projects LIMIT 1"""
    cur.execute(sql_select_query)
    records = cur.fetchall()
    print(records)
    for elem in records:
        project_id = elem[0]
    return project_id


def select_all(project_id):
    project_id = 20
    print(project_id)
    connn = sqlite3.connect('links.db')
    print(connn)
    curr = connn.cursor()
    print(curr)
    sql_select_query = """select * from threads"""
    curr.execute(sql_select_query)
    records = curr.fetchall()
    return records

def add_new_post(folder_date, folder_name, work_folder, photo_date, file_date, file_names, thread_id=50):
    connn = sqlite3.connect('links.db')
    curr = connn.cursor()
    print('ВЫзов на запись!')
    print(str(folder_date), str(folder_name))
    data_insert = (folder_date, folder_name, work_folder, photo_date, file_date, file_names, thread_id)
    sqlite_param = """INSERT INTO post(folder_date, folder_name, work_folder, photo_date, file_date, files_name, thread_id)
       VALUES(?, ?, ?, ?, ?, ?, ?);"""
    curr.execute(sqlite_param, data_insert)
    last_id = curr.lastrowid
    connn.commit()
    return last_id


def work_folder_in_base(folder):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()

    sql_select_query = """select * from post where work_folder = ?"""
    cur.execute(sql_select_query, (folder,))
    records = cur.fetchall()
    if len(records) > 0:
        return True
    else:
        return False

def check_thread_in_posts(folder):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select url from post where url not NULL and work_folder = ?"""
    cur.execute(sql_select_query, (folder,))
    records = cur.fetchall()
    if records:
        return True
    else:
        return False

def check_zip_file(zip_file):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select * from zips where name = ?"""     # убрал link is NULL and
    cur.execute(sql_select_query, (zip_file,))
    records = cur.fetchall()
    if records:
        return True
    else:
        return False


def check_ready_for_post(folder):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select url from post where work_folder = ?"""
    cur.execute(sql_select_query, (folder,))
    records = cur.fetchall()
    print(records[0][0])

    if records[0][0]:
        return True
    else:
        return False

def select_folders_in_current_project():
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select prefix, starting_id from threads where project_id = 20"""
    cur.execute(sql_select_query)
    records = cur.fetchall()
    print(records)
    return records


def select_info_from_post(folder):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select * from post where work_folder = ?"""
    cur.execute(sql_select_query, (folder,))
    records = cur.fetchall()
    print(records)
    return records

def select_info_from_zip(zip_file):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select * from zips where name = ?"""
    cur.execute(sql_select_query, (zip_file,))
    records = cur.fetchall()
    print(records)
    return records

def select_url_from_zip(zip_id):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select link from zips where zipid = ?"""
    cur.execute(sql_select_query, (zip_id,))
    records = cur.fetchone()
    print(records)
    return records


def select_data_from_forums(project_id):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select * from forums where project_id = ?"""
    cur.execute(sql_select_query, (project_id,))
    records = cur.fetchall()
    print(records)
    return records

def search_data_for_login(forum_id):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select * from forums where id = ?"""
    cur.execute(sql_select_query, (forum_id,))
    records = cur.fetchall()
    print(records)
    return records

def update_place_in_bd(name, login_url, inputs, userid, id, type_place):
    print(name, login_url, inputs, userid, id, type_place)

    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    data_update = (name, login_url, inputs, userid, type_place, int(id))
    sqlite_param = """Update forums set name = ?, login_url = ?, inputs = ?, userid = ?, type = ?  where id = ?"""
    cur.execute(sqlite_param, data_update)
    conn.commit()


def save_place_thread(thread_id, place_id, link_url, place_type):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select * from forums_threads where threads = ? AND forums = ?"""
    cur.execute(sql_select_query, (thread_id, place_id,))
    records = cur.fetchall()
    print('records:', records, place_type)
    if len(records) > 0:
        data_update = (link_url, place_type, place_id, thread_id)
        sqlite_param = """Update forums_threads set url = ?, type = ?  where forums = ? AND threads = ?"""
        cur.execute(sqlite_param, data_update)
        conn.commit()

    else:
        data_insert = (place_id, thread_id, link_url, place_type)
        sqlite_param = """INSERT INTO forums_threads (forums, threads, url, type) 
           VALUES(?, ?, ?, ?);"""
        cur.execute(sqlite_param, data_insert)
        last_id = cur.lastrowid
        conn.commit()
        return last_id

def select_current_place_thread(thread_id, place_id):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select * from forums_threads where threads = ? AND forums = ?"""
    cur.execute(sql_select_query, (thread_id, place_id,))
    records = cur.fetchall()
    if len(records) > 0:
        print('records22:', records)
        return records[0][3], records[0][4]

def select_places_for_thread(thread_id):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select * from forums_threads where threads = ?"""
    cur.execute(sql_select_query, (thread_id,))
    records = cur.fetchall()
    return records

def select_name_from_places(id):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """select name from forums where id = ? order by name"""
    cur.execute(sql_select_query, (id,))
    records = cur.fetchone()
    print('records:', records)
    return records

def delete_tfp(thread_id, place_id):
    conn = sqlite3.connect('links.db')
    cur = conn.cursor()
    sql_select_query = """delete from forums_threads where threads = ? and forums = ?"""
    cur.execute(sql_select_query, (thread_id, place_id,))
    conn.commit()
    print("Запись успешно удалена")
    cur.close()
