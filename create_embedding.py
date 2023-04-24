import crud
import openai
from llm import safe_wrapper, num_tokens_from_string_fast, MIN_BATCH_TOKEN_NUM
import numpy as np
from collections import deque

@safe_wrapper
def cal_embedding_safe(item_q:deque[tuple[str, str]], engine='text-embedding-ada-002', flush=False)->list[tuple[str, str]]:
    """
    itme_q is a deque of tuple, first element is the text, second is the id
    return list of tuple
    flush controls if we need to calculate all the item at once, useful for the tail items
    """
    # texts = [item[0] for item in item_q]
    # num_t = num_tokens_from_string(''.join(texts))
    str_len = [len(item[0]) for item in item_q]
    num_t = num_tokens_from_string_fast(sum(str_len))
    if num_t < MIN_BATCH_TOKEN_NUM and not flush:
        print("token not full")
        return -1
    
    text_list = []
    id_list = []
    while item_q:
        text_list.append(item_q[0][0])
        id_list.append(item_q[0][1])
        item_q.popleft()
    response = openai.Embedding.create(input=text_list, engine=engine)
    ans = []
    for data,tid in zip(response['data'],id_list):
        ans.append((np.array(data['embedding']),tid))
    return ans

def update_embed_product():
    # calculate product embedding
    product_q = deque()
    cursor = con.execute('''SELECT product_id, product_details, product_embedding FROM product''')
    all_details = cursor.fetchall()
    for details in all_details:
        product_id, detail_text, product_embedding = details
        if product_embedding is not None:
            print("product embed exist, skip")
            continue
        
        product_q.append((detail_text, product_id))
        try:
            result = cal_embedding_safe(product_q)
            if result == -1:
                continue
        except:
            raise

        for embed_val, pid in result:
            crud.UPDATE_PRODUCT_EMBED(con, pid, embed_val)
            print("product_id:"+str(pid) + " updated")
    
    if len(product_q) != 0:
        try:
            result = cal_embedding_safe(product_q, flush=True)
        except:
            raise
        for embed_val, pid in result:
            crud.UPDATE_PRODUCT_EMBED(con, pid, embed_val)
            print("product_id:"+str(pid) + " updated") 

def update_embed_review():
    # calculate user embedding
    review_q = deque()
    cursor = con.execute('''SELECT id, user_avatar, user_embedding FROM review''')
    all_user = cursor.fetchall()
    for user in all_user:
        uid, user_avatar,user_embedding = user
        if user_embedding is not None:
            print("user embed exist, skip")
            continue
        review_q.append((user_avatar, uid))
        try:
            result = cal_embedding_safe(review_q)
            if result == -1:
                continue
        except:
            raise
        
        for embed_val, nuid in result:
            crud.UPDATE_USER_EMBED(con, nuid, embed_val)
            print("user_id:"+str(nuid) + " updated")
    if len(review_q) != 0:
        try:
            result = cal_embedding_safe(review_q, flush=True)
        except:
            raise
        for embed_val, nuid in result:
            crud.UPDATE_USER_EMBED(con, nuid, embed_val)
            print("user_id:"+str(nuid) + " updated") 


if __name__ == "__main__":
    con = crud.connect()
    # con.execute('''ALTER TABLE product ADD COLUMN product_embedding array''')
    # con.execute('''ALTER TABLE review ADD COLUMN user_embedding array''')
    # update_embed_product()
    update_embed_review()
    con.close()