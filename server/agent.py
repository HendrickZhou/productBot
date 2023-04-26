import openai
from openai.embeddings_utils import distances_from_embeddings
from urllib.parse import urlparse
import numpy as np
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import crud

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
##########å
class RecoSession(Session):
    session_id = 'recommend'
    def __init__(self) -> None:
        super().__init__()
        self.text = None
        self.message_list = [{
           "role": "system",
           "content": "You are a helpful assistant named Saul in an shopping website, a customer is asking for a recommendation. You need to get his/her figure information(age, height, body type only) and his/her wanted item." 
        }]

    def recommend(self):
        embed_val_product = openai.Embedding.create(input=self.text, engine='text-embedding-ada-002')['data'][0]['embedding']
        con = crud.get_connect()
        result = crud.GET_ALL_PD(con)
        if(len(result)==0):
            raise Exception("product select is broken")
        
        all_dist = []
        for pid, embedding in result:
            dist = distances_from_embeddings(embed_val_product, [embedding], distance_metric='cosine')
            all_dist.append((dist, pid))

        sorted_dist = sorted(all_dist, key=lambda tup: tup[0]) # ascending
        top_ten = sorted_dist[0:10]
        top_ten = [p[1] for p in top_ten]
        result = crud.GET_RATE(con, top_ten)
        if(len(result)==0):
            raise Exception("product select is broken 2")

        result = list(map(list,result))
        for i in range(len(result)):
            if result[i][1] is None:
                result[i][1] = -1
        
        top_three = sorted(result, key=lambda tup: tup[1], reverse=True) # descending
        top_three = top_three[0:3]
        top_three = [p[0] for p in top_three]
        result = crud.GET_PDS(con, top_three)
        return result
        # find 10 highest pdp
        # select the at most 3 with highest rate(if no rate, rate=-1)
        # if there're reviews, find the reviewer's closet avatar, and if the review is positive, attach it


    def reply(self, text):
        self.text = text
        result = self.recommend()
        pdps_str = ""
        for r in result:
            pdps_str += r[0] + '\n'
        system_prompt = [{
           "role": "system",
           "content": "Here're three product details:\n" + 
           pdps_str + 
           "\nHere's the customer's preference:\n"+
           text +
           "\n Now recommend these three product to a custom, be sure to include the item Id and recommendation reason for each item!"
        }]
        completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=system_prompt,
        )
        return str(completion['choices'][0]['message']['content'])
    
    def intro(self):
        # completion = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        # temperature = 0.7,
        # messages=self.message_list,
        # )
        # return str(completion['choices'][0]['message']['content'])
        return """Hello! I'm Saul, your shopping assistant. Before I can recommend an item for you, may I know your figure information such as age, height and body type? This will help me provide a more accurate suggestion for you. Thank you!

Once I have your figure information, may I know the item you are looking for?
        """

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
        id_ = None
        try:
            id_ = cls._extract_item_id(link)
        except:
            print("fail to extract item id from url")
            return """This doesn't seem to be a valid url! Can you type it again?""",-1
        
        con = crud.get_connect()
        try:
            # import pdb; pdb.set_trace()
            details = crud.GET_PD(con,id_)
        except:
            print("can't find this item id:" + str(id_))
            return """This doesn't seem to be a valid url! Can you type it again?""",-1
        else:
            print(details)
            return details, 0
        finally:
            con.close()
    
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