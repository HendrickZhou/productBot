import openai
from urllib.parse import urlparse
import numpy as np
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import crud

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

from abc import ABCMeta, abstractmethod
class Session(metaclass=ABCMeta):
    @property
    @abstractmethod
    def session_id(self):
        pass

    @abstractmethod
    def reply(self, text):
        pass

    @abstractmethod
    def intro(self):
        pass

##########
# product recommendation
##########
class RecoSession(Session):
    session_id = 'recommend'
    def __init__(self) -> None:
        super().__init__()
        self.user_profile = ""
        self.product_profile = ""

    def update_reco(self):
        embed_val_user = np.array(openai.Embedding.create(input=self.user_profile, engine='text-embedding-ada-002')['data'][0]['embedding'])
        # find closest in database
        embed_val_product = np.array(openai.Embedding.create(input=self.product_profile, engine='text-embedding-ada-002')['data'][0]['embedding'])
        # find closest
        links = []
        return links

    def reply(self, text):
        self.handle_input()
        links = self.update_reco()
        # wrap with word (product and what else)
        return 
    
    def intro(self):
        return """Hello
        """

    def handle_input(self,text):
        # if it's user's information
        self.user_profile += text
        # if it's product's information
        self.product_profile += text


##########
# product q&a
##########
class QNASession(Session):
    """This is a expensive session! since it need to know the details on product on every single conversation
    """
    session_id = 'qna'
    def __init__(self) -> None:
        super().__init__()
        self.context=None

    def update_link(self, link):
        self.link = link
        context, err = self._build_qa_context(link)
        
        if err == -1:
            return {
                "feedback" : context,
                "done" : 0
            }
        self.context = context
        feedback = """I got the link! Any questions on this product?"""
        return {
            'feedback': feedback,
            "done": 1
        }

    def reply(self, text):
        return self.qna_with_context(text, self.context)
    
    def intro(self):
        return """Hi there! This is Saul, you can ask me any questions on a product given the link!\n Please input the website link in the prompt!
        """

    @classmethod
    def _build_qa_context(cls,link):
        """
        function to call if there's specific link user want to know
        """
        try:
            id_ = cls._extract_item_id(link)
        except:
            print("fail to extract item id from url")
            return """This doesn't seem to be a valid url! Can you type it again?""",-1
        try:
            con = crud.connect()
            details = crud.GET_PD(con,id_)
            con.close()
        except:
            print("can't find this item id:" + str(id_))
            return """This doesn't seem to be a valid url! Can you type it again?""",-1
        print(details)
        return details, 0
    
    @staticmethod
    def _extract_item_id(url):
        result = urlparse(url)
        return result.path.split('/')[-1]

    @staticmethod
    def qna_with_context(text, context):
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "Your name is Saul. Here's a product details, please read and answer questions on this product.\n" + context},
                # {"role": "user", "content": context},
                {"role": "user", "content": text}
            ]
        )
        return str(completion['choices'][0]['message']['content'])

##########
# casul chat
##########
class ChatSession(Session):
    session_id = 'chat'
    def __init__(self) -> None:
        super().__init__()

    def intro(self):
        return """Hi! Saul here, anything you want to talk now?
        """
    def reply(self, text) -> str:
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message.content

class SessionFactory:
    session_map = {
        'chat': ChatSession,
        'qna' : QNASession,
        'recommend' : RecoSession
    }
    def new_session(self, session_id):
        return self.session_map[session_id]

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

    # def compress(self, )