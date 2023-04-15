import crud
import openai
import numpy as np
import io
import sqlite3

con = crud.connect()
con.execute('''ALTER TABLE product ADD COLUMN product_embedding array''')
con.execute('''ALTER TABLE review ADD COLUMN user_embedding array''')

# calculate product embedding
cursor = con.execute('''SELECT product_details FROM product''')
all_details = cursor.fetchall()
for details in all_details:
    detail_text, = details
    embed_val = np.array(openai.Embedding.create(input=detail_text, engine='text-embedding-ada-002')['data'][0]['embedding'])
    con.execute('''
    INSERT INTO product (product_embedding) VALUES (?)
    ''', (embed_val,))

# calculate user embedding
cursor = con.execute('''SELECT user_avatar FROM review''')
all_user = cursor.fetchall()
for user in all_user:
    user_avatar, = user
    embed_val = np.array(openai.Embedding.create(input=user_avatar, engine='text-embedding-ada-002')['data'][0]['embedding'])
    con.execute('''
    INSERT INTO review (user_embedding) VALUES (?)
    ''', (embed_val,))
