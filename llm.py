# from openai.embeddings_utils import distances_from_embeddings, cosine_similarity
import openai
import logging_config
import logging

def organize_product_detail(text):
    # TODO if token over length, truncate it
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "You are a helpful assistant with a e-commerce product."},
            {"role": "user", "content": "I'll give you a detail description text of a product, please generate a structured output with all the information you know about this product"},
            {"role": "assistant", "content": "Yes, please give me the text."},
            {"role": "user", "content": text}
        ]
    )

    answer = completion.choices[0].message.content
    # import pdb;pdb.set_trace()
    logging.info("openai answer to product details:")
    logging.info(answer)
    return answer

def get_user_avatar(text)->str:
    # TODO if token over length, truncate it
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "You are a helpful assistant with a e-commerce product."},
            {"role": "user", "content": "I'll give you some html code of a buyer, please give m a list with all the information you know about this user. Please only give me the list"},
            {"role": "assistant", "content": "Yes, please give me the code."},
            {"role": "user", "content": text}
        ]
    )
    answer = completion.choices[0].message.content
    logging.info("openai answer to user avatar:")
    logging.info(answer)
    return answer