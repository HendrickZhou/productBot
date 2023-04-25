"use strict"
const express = require('express');
const { Server } = require('socket.io');
const http = require('http');

const app = express();
const server = http.createServer(app);
const io = new Server(server)

io.on('connection', (socket) =>  {
    console.log('User connected');
    socket.on('disconnect', () => {
        console.log('user disconnected');
      });

    socket.on('test', (socket) => {
        console.log('test!');
    });

    socket.on('message', (data) => {
        console.log('new message from user!'+ data);
        socket.broadcast.emit('py_message', data);
    });

    socket.on('py_message', (data) => {
        console.log('received python message');
        console.log(data);
        socket.broadcast.emit('new message', data);
    })

    socket.on('py_test', (data) => {
        console.log(data);
    })
})



// user sending the message
app.post('/send', async (req, res) => {
    const {message} = req.body;
});

app.get('/', async (req, res)=> {
    socket.emit('py_setup_chat');
    socket.on('py_setup_chat', (data) => {
        console.log('python setup chat done');
        // parse gpt return data into string
        first_sentence = data;
        // do sth with response
    });
});

// user select chat session
app.post('/chat/:cur_session', async (req, res) => {
    //
    var cur_session = req.params['cur_session'];
});

// user select qna session
app.post('/qna', async (req, res) => {
    //
});

// user select recommendation session
app.post('/recommend', async (req, res) => {
    //
});

// user submit product website
app.post('/url', async (req, res) => {
    //
;})

server.listen(process.env.PORT || 5500, ()=> {
    const {port} = server.address();
    console.log(`Server running on PORT ${port}`);
});