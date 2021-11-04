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
    conn.commit()
