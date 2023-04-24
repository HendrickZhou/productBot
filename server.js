const express = require('express');

const app = express();

// user sending the message
app.post('/send', async (req, res) => {
    const {message} = req.body;
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

const server = app.listen(process.env.PORT || 5500, ()=> {
    const {port} = server.address();
    console.log('Server running on PORT ${port}');
});