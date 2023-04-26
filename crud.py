"""
table 1: Product
product_id, product_details_raw, product_details, average_rate

table 2: Review
review_id, user_avatar_raw, user_avatar, rate, user_review_description

table 3: relation
(product_id) (review_id)
"""
import sqlite3
import numpy as np
import io
from util import run_once
import logging
import logging_config

DB_NAME = "pdp.db"

def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)
# Converts np.array to TEXT when inserting
sqlite3.register_adapter(np.ndarray, adapt_array)

# Converts TEXT to np.array when selecting
sqlite3.register_converter("array", convert_array)

@run_once
def connect():
    con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
    return con

def get_connect():
    con = sqlite3.connect(DB_NAME, detect_types=sqlite3.PARSE_DECLTYPES)
    return con

def create_error_db():
    """
    """
    con = sqlite3.connect(DB_NAME)
    query = """
    CREATE TABLE error_case(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    code TEXT
    );
    """
    con.execute(query)
    con.close()

def create_db():
    """
    For product table, product_details etc could be null
    if it's sold out
    """
    con = sqlite3.connect(DB_NAME) 
    queries = []
    queries.append("""
    PRAGMA foreign_keys = ON;
    """)
    queries.append("""
    CREATE TABLE product(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    product_details_raw TEXT,
    product_details TEXT,
    average_rate REAL,
    UNIQUE(product_id) ON CONFLICT IGNORE
    );
    """)
    queries.append("""
    CREATE TABLE review(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    p_id INT NOT NULL,
    user_avatar TEXT NOT NULL,
    user_avatar_raw TEXT NOT NULL,
    review_content TEXT NOT NULL,
    FOREIGN KEY(p_id) REFERENCES product(id)
    );
    """)
    try:
        with con:
            for query in queries:
                con.execute(query)
    except Exception as e:
        print("creatation failed")

    con.close()
    create_error_db()

def ADD_ERROR_URL(con, url, error_code):
    query = """
    INSERT INTO error_case (url,code) VALUES (?,?)
    """
    try:
        with con:
            con.execute(query, (url, error_code))
    except:
        logging.error("failed to add error case to database")

def ADD_PRODUCT(con, product_id, product_details_raw, product_details, average_rate):
    """
    """
    query = """
    INSERT INTO product (product_id, product_details_raw, product_details, average_rate) VALUES (?,?,?,?)
    """
    try:
        with con:
            con.execute(query, (product_id, product_details_raw, product_details, average_rate))
    except:
        logging.error("fail to add product into database")

def ADD_REVIEW(con, p_id, user_avatar, user_avatar_raw, review_content):
    """
    """
    # import pdb;pdb.set_trace()
    query = """
    SELECT id FROM product WHERE product_id = ?
    """
    try:
        cursor = con.execute(query, (p_id,))
        the_real_id, = cursor.fetchone()
    except:
        logging.error("fail to find product id from review")
        return
    query = """
    INSERT INTO review (p_id, user_avatar, user_avatar_raw, review_content) VALUES (?,?,?,?)
    """
    try:
        with con:
            con.execute(query, (the_real_id, user_avatar, user_avatar_raw, review_content))
    except:
        logging.error("fail to insert review info into database")

def GET_PD(con,product_id):
    """
    """
    query = '''
    SELECT product_details FROM product WHERE product_id = ?
    '''
    try:
        with con:
            cursor = con.execute(query,(product_id,))
            details, = cursor.fetchone()
    except:
        logging.error("couldn't find product")
        raise
    else:
        if(len(details)==0):
            raise Exception("didn't find item")
        return details

def UPDATE_PRODUCT_EMBED(con, product_id, embedding_val):
    try:
        with con:
            con.execute('''
            UPDATE product SET product_embedding=:embedding_val 
            WHERE product_id=:pid
            ''',
            {'embedding_val':embedding_val, 'pid': product_id})
    except:
        logging.exception("fail to update product embedding value")
        raise

def UPDATE_USER_EMBED(con, uid, embedding_val):
    try:
        with con:
            con.execute('''
            UPDATE review SET user_embedding=:embedding_val 
            WHERE id=:uid
            ''',
            {'embedding_val':embedding_val, 'uid': uid})
    except:
        logging.exception("fail to update user embedding values")
        raise