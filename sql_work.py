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


def img_in_base(elem, th_url, show_url):
    data_insert = (elem, th_url, show_url)
    sqlite_param = """INSERT INTO pics(name, thumb, show) 
       VALUES(?, ?, ?);"""
    cur.execute(sqlite_param, data_insert)
    conn.commit()


def zip_in_base(name, size):
    data_insert = (name, size)
    sqlite_param = """INSERT INTO zips(name, size) 
       VALUES(?, ?);"""
    cur.execute(sqlite_param, data_insert)
    conn.commit()

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


def select_all():
    project_id = 20
    sql_select_query = """select * from threads where project_id = ?"""
    cur.execute(sql_select_query, (project_id,))
    records = cur.fetchall()
    print(records)
    return records

def add_new_post(folder_date, folder_name, work_folder, photo_date, file_date, file_names):
    connn = sqlite3.connect('links.db')
    curr = connn.cursor()
    print(str(folder_date), str(folder_name))
    data_insert = (folder_date, folder_name, work_folder, photo_date, file_date, file_names)
    sqlite_param = """INSERT INTO post(folder_date, folder_name, work_folder, photo_date, file_date, files_name)
       VALUES(?, ?, ?, ?, ?, ?);"""
    curr.execute(sqlite_param, data_insert)
    connn.commit()

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





