# from openai.embeddings_utils import distances_from_embeddings, cosine_similarity
import openai
import scrapping.logging_config as logging_config
import logging
import tiktoken
import time

MIN_BATCH_TOKEN_NUM = 4000

def num_tokens_from_string(string: str, encoding_name: str="cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def num_tokens_from_string_fast(str_len: int) -> int:
    """return the estimated number of tokens in a text string but fast
    The magic number is calculated by this:
    average English word length: 4.7
    each word on average generate 4/3 tokens (100 tokens->75 words)
    so for a string of length x, consider the space/tab/newline, the average word
    length is 5.7
    the total token should be x/5.7*(4/3) ~= x/4.3
    """
    magic_number = 4.3
    return int(str_len/magic_number)

def safe_wrapper(
    func,
    wait_second: float=3.5,
    bound_delay: float=5
):
    """
    timer reference: https://stackoverflow.com/questions/24862545/assure-minimal-wait-between-calls-with-decorators
    openai exception: https://help.openai.com/en/articles/6897213-openai-library-error-types-guidance

    function should accept a deque as the first non-kw argument
    The behaviour: 
        this function will try to call the openai api, but the function is ganranteed to only
        be called as least 3 seconds in between

        this is a blocking function! it's single thread safe
        
        with following exception case:
        1. if it's RateLimitError, retry it after waiting 5 seconds
        2. if after two retry it's still RateLimitError, raise the error
        3. if it's any other error, raise the error and stop the function
    """
    last_time = [0]
    def inner(q, **kwargs):
        time_diff = time.time() - last_time[0]
        if time_diff<wait_second:
            time.sleep(1-time_diff)
        last_time[0] = time.time()

        # higher bound
        retry_num = 2
        while True:
            if retry_num < 0:
                raise Exception("RateLimit error retry 2 times, still failed")
            try:
                return func(q, **kwargs)
            except openai.error.RateLimitError:
                print("hitting per miniute limit, sleep")
                time.sleep(bound_delay)
            except Exception as e: # any other errors
                logging.error(f"Openai API error: {e}")
                raise e
    return inner

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