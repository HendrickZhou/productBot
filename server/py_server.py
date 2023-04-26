import socketio
import api

sio = socketio.Client()

the_sio = None
@sio.on('py_message')
def on_py_message(data):
    print('received')
    the_reply = api.reply(data)
    sio.emit('py_message', the_reply)

@sio.on('py_input_link')
def update_link(link):
    print('update link')
    sio.emit('py_input_link', api.update_link(link))

@sio.event
def connect():
    sio.emit('py_test','test string')
    print('connected')

@sio.on('switch')
def switch(data):
    cur = data['cur']
    next = data['next']
    print('switching to' + next)
    print("cur: "+ cur)
    if cur == "unassigned":
        intro = api.setup_session(next)
        sio.emit('py_intro', intro)
    else:
        result = api.continue_session(next)
        if(result is not None):
            sio.emit('py_intro', result)
   

if __name__=="__main__":
    sio.connect('http://localhost:5500')
    sio.wait()



