import socketio
import api

sio = socketio.Client()

the_sio = None
@sio.on('py_message')
def on_py_message(data):
    print('received')
    sio.emit('py_message', api.just_chat(data))

@sio.event
def connect():
    sio.emit('py_test','test string')
    print('connected')

if __name__=="__main__":
    sio.connect('http://localhost:5500')
    sio.wait()



