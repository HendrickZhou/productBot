import openai
from urllib.parse import urlparse
import crud
import numpy as np

def INIT_agent():
    first_prompt = """
    Hello! this is your assistant in jcrew shopping site. \nAre you looking for some recommendation or do you want to know information on some specific product from the website?
    """
    manager_word = """You are a helpful assistant in a online shopping website,
    you need to lead your customer to only three types of conversation: 
    q&a on a speific item, recommendation, or just casual chat. 
    If a custom asks you to recommend something, make sure you get his/her figure information and his/her wanted item
    """
    messages=[
            {"role": "system", "content": manager_word},
            {"role": "user", "content": "When a buyer ask you questions, you should tell if they're asking for information of a product, or ask for recommendation of a product"},
            {"role": "assistant", "content": "Got it"},
            {"role": "assistant", "content": first_prompt}
        ]
    return messages, first_prompt

def user_input(text):
    completion = openai.Completion.create(
    model="text-davinci-003",
    prompt="Someone just say this:\n" + text + "\n Do you think is this person asking for information on a product, or asking for recommendation? If it's the former, say \"1\", otherwise, say \"0\"",
    max_tokens=1,
    ) 
    answer = completion.choices[0].text
    if(int(answer)==1): #ask for information
        pass
    elif(int(answer)==0): # ask for recommendation
        pass
    else:
        pass


##########
# product recommendation
##########
class RecoSession:
    def __init__(self) -> None:
        self.user_profile = ""
        self.product_profile = ""

    def update_reco(self):
        embed_val_user = np.array(openai.Embedding.create(input=self.user_profile, engine='text-embedding-ada-002')['data'][0]['embedding'])
        # find closest in database
        embed_val_product = np.array(openai.Embedding.create(input=self.product_profile, engine='text-embedding-ada-002')['data'][0]['embedding'])
        # find closest
        links = []
        return links

    def answer(self):
        self.handle_input()
        links = self.update_reco()
        # wrap with word (product and what else)
        return 

    def handle_input(self,text):
        # if it's user's information
        self.user_profile += text
        # if it's product's information
        self.product_profile += text


##########
# product q&a
##########
class QNASession:
    def __init__(self, link) -> None:
        self.context = build_qa_context(link)
    def answer(self, text):
        qna_with_context(text,self.context)

def build_qa_context(link):
    """
    function to call if there's specific link user want to know
    """
    id_ = extract_item_id(link)
    details = crud.GET_PD(id_)
    return {"content": details}

def extract_item_id(url):
    result = urlparse(url)
    return result.path.split('/')[-1]

def qna_with_context(text, context):
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system", "content": "A buyer is having a conversation with you regarding a product justed mentioned with you."},
            {"role": "user", "content": context},
            {"role": "user", "content": text}
        ]
    )
    return completion.choice[0].message.content

##########
# casul chat
##########
class ChatSession:
    pass

##########
# Keep all conversation consistent
##########
class Memory:
    """store the related information(user and his/her preference) based on all the conversations
    happened. 
    can be extended to support more powerful functionality!
    """
    def __init__(self) -> None:
        self.user_avatar