'use strict'
const { response } = require('express');
const blessed = require('neo-blessed');
const socket = require("socket.io-client")(
    process.argv[2] || 'http://localhost:5500'
);


/////// Const ///////
const address ='http://localhost:5500';
const role_map = {
    1: 'Saul',
    2: 'You',
};
const session_map = {
    1 : 'chat',
    2 : 'qna',
    3 : 'recommend',
    0 : 'unassigned'
}

const banner_string_old = `
        _           _   _           _   
    ___| |__   __ _| |_| |__   ___ | |_ 
   / __| '_ \\ / _\` | __| '_ \\ / _ \\| __|
  | (__| | | | (_| | |_| |_) | (_) | |_ 
   \\___|_| |_|\\__,_|\\__|_.__/ \\___/ \\__|
`;

const banner_string = `
██████╗ ███████╗████████╗████████╗███████╗██████╗      █████╗ ███████╗██╗  ██╗    ███████╗ █████╗ ██╗   ██╗██╗     
██╔══██╗██╔════╝╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗    ██╔══██╗██╔════╝██║ ██╔╝    ██╔════╝██╔══██╗██║   ██║██║     
██████╔╝█████╗     ██║      ██║   █████╗  ██████╔╝    ███████║███████╗█████╔╝     ███████╗███████║██║   ██║██║     
██╔══██╗██╔══╝     ██║      ██║   ██╔══╝  ██╔══██╗    ██╔══██║╚════██║██╔═██╗     ╚════██║██╔══██║██║   ██║██║     
██████╔╝███████╗   ██║      ██║   ███████╗██║  ██║    ██║  ██║███████║██║  ██╗    ███████║██║  ██║╚██████╔╝███████╗
╚═════╝ ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝
`


/////// Global ////////
var cur_session = 0; // 0 unassigned, 1 chat, 2 qna, 3 recommend
var waiting_link = false;

const screen = blessed.screen({
    smartCSG: true,
    debug: true,
    tile: 'productBotDemo',
});
screen.enableInput();
var can_send = true;
var tab_top = 5;
var width = '20%';
var tab_height = 2;
var message_area_top = 6;
var message_area = blessed.list({
    // position
    align: 'left',
    width: '100%',
    // height: '70%',
    top: message_area_top,
    left: 0,
    bottom:2,

    // style
    border: {
        type: 'line',
    },
    // interaction
    scrollbar: {
        ch: ' ',
    },
    mouse: true,
    keys: true,

    // content
    items: []
});
var unselected_style= {
    bg: 'magenta',
    hover: {
        bg: 'green'
    }
};
var selected_style = {
    bg: 'green'
}
var banner = blessed.box({
    top:'-10%',
    width: '100%',
    height: 10,
    left: 0,

    content: banner_string,
});
var box_session_Chat = blessed.box({
    // position 
    top: tab_top,
    width: width,
    height: tab_height,
    left: 0,

    // text
    content: '{center}Casual Chat{/center}',
    tags: true,

    // style
    style: {...unselected_style},
});

var box_session_QNA = blessed.box({
    // position 
    top: tab_top,
    width: width,
    height: tab_height,
    left: '30%',

    // text
    content: '{center}Q&A on product{/center}',
    tags: true,

    // style
    style: {...unselected_style},
});

var box_session_Recomend = blessed.box({
    // position 
    top: tab_top,
    width: width,
    height: tab_height,
    left: '60%',

    // text
    content: '{center}Recommendation{/center}',
    tags: true,

    // style
    style: {...unselected_style},
});

/////// Function ////////
var first = [true, true, true];
function switch_session(next_session) {
    if(cur_session ==  next_session) return;
    var old_cur= cur_session;
    switch(next_session) {
        case 1: // just chat
            box_session_Chat.style = {...selected_style};
            box_session_QNA.style = {...unselected_style};
            box_session_Recomend.style = {...unselected_style};
            cur_session = 1;
            screen.render();
            break;
        case 2: // qna
            box_session_QNA.style = {...selected_style};
            box_session_Chat.style = {...unselected_style};
            box_session_Recomend.style = {...unselected_style};
            cur_session = 2;
            screen.render();
            waiting_link = true;
            break;
        case 3: // recommend
            box_session_Recomend.style = {...selected_style};
            box_session_QNA.style = {...unselected_style};
            box_session_Chat.style = {...unselected_style};
            cur_session = 3;
            screen.render();
            break;
    }
    switch_screen(old_cur, next_session);

    var content;
    if(first[next_session-1]){
        content = {
            cur : session_map[0],
            next : session_map[next_session],
        }
        first[next_session-1] = false;
    } else {
        content = {
            cur : session_map[old_cur],
            next : session_map[next_session],
        }
    }
    socket.emit('change_session', content);
}

function init_components() {
    
}

function msg_formatter(msg, role) {
    // role is int
    var formatted = `> ${role_map[role]}: ${msg}`;
    return formatted;
}

function adjust_row(formatted_msg, row_area){
    var num_newline = 0;
    for(var i=0;i<formatted_msg.length; i++) {
        var ch= formatted_msg[i];
        if(ch=='\n' || ch=='\r\n' || ch=='\r'){
            num_newline++;
        }
    }
    const chr_num = formatted_msg.length;
    const chr_max_len = row_area.width;
    var rought_line_num = Math.ceil(chr_num / chr_max_len);
    row_area.height += (rought_line_num+num_newline-1);
}

function break_string(message, max_len) {
    var idx=0;
    var message_list = [];
    var cur_line_str='';
    while(idx<message.length){
        cur_line_str+=message[idx];
        if(message[idx]=='\n' || cur_line_str.length >= max_len) {
            // check if word breaks here
            if(idx==message.length-1) {
                message_list.push(cur_line_str);
                return message_list;
            }
            message_list.push(cur_line_str);
            cur_line_str='';
        }
        idx++;
    }
    if(idx == message.length) {
        message_list.push(cur_line_str);
    }
    return message_list;
}

function new_my_message(msg, message_area) {
    var formatted_msg = msg_formatter(msg, 2);
    var max_len = message_area.width - 3; // 3 as buffer
    var message_list = break_string(formatted_msg, max_len);
    for(var i=0; i<message_list.length; i++) {
        message_area.addItem(message_list[i]);
    }
    message_area.scrollTo(message_area.items.length+1);
    screen.render();
}

function new_bot_message(msg, message_area) {
    var formatted_msg = msg_formatter(msg, 1);
    var max_len = message_area.width - 3; // 3 as buffer
    var message_list = break_string(formatted_msg, max_len);
    for(var i=0; i<message_list.length; i++) {
        var new_row = message_area.addItem(message_list[i]);
        new_row.style.bg = '#343540';
        message_area.scrollTo(message_area.items.length+1);
        screen.render();
    }
}

var cache_msg_list = [[],[],[]];
function refill_message(msg_list) {
    while(msg_list.length != 0) {
        var msg = msg_list.shift();
        var row = message_area.addItem(msg[1]);
        row.style.bg = msg[0];
    }
    message_area.scrollTo(message_area.items.length+1);
    screen.render()
}

function switch_screen(cur, next) {
    if(cur==0) {
        return;
    }
    var cur_list = cache_msg_list[cur-1];
    var next_list = cache_msg_list[next-1];
    while(message_area.items.length!=0) {
        var ele = message_area.shiftItem()
        cur_list.push([ele.style.bg, ele.content]);
    }
    refill_message(next_list);
}

function on_init() {
    // setup connection to backend and render first chatbot message
    socket.emit('test');
    switch_session(1);
}

function main() {
    on_init();
    
    socket.on('intro', (msg) => {
        new_bot_message(msg, message_area);
        can_send = true;
    });
    socket.on('new message', (msg) => {
        new_bot_message(msg, message_area);
        can_send = true
    });
    socket.on('link_done', (msg) => {
        new_bot_message(msg, message_area);
        can_send = true;
        waiting_link = false;
    }); 
    socket.on('link_not_done', (msg)=> {
        new_bot_message(msg, message_area);
        can_send = true; 
    })

    screen.append(banner);
    screen.append(box_session_QNA);
    screen.append(box_session_Recomend);
    screen.append(box_session_Chat);
    screen.append(message_area);

    /////////////////////////////////////////////////
    // session switch logic
    box_session_Chat.on('click', () => {
        switch_session(1);
    });
    box_session_QNA.on('click', () => {
        switch_session(2)
    });
    box_session_Recomend.on('click', () => {
        switch_session(3);
    });

    /////////////////////////////////////////////////
    // typing area
    var input = blessed.textarea({
        bottom: 0,
        height: 3,
        inputOnFocus: true,
        padding: {
          top: 1,
          left: 2,
        },
        style: {
          fg: '#787878',
          bg: '#454545',
  
          focus: {
            fg: '#f6f6f6',
            bg: '#353535',
          },
        },
      });
  
      input.key('enter', async function() {
        // if(!can_send) {
        //     return;
        // }
        can_send = false;
        var message = this.getValue();
        try {
            if(waiting_link) {
                socket.emit('input_link',message);
            } else {
                socket.emit('message', message);
            }
        } catch (err) {
          // error handling
        } finally {
          input.clearValue();
          input.focus();
          new_my_message(message, message_area);
        }
      });
  
      screen.key(['escape', 'q', 'C-c'], () => {
        return process.exit(0);
      });
      screen.append(input);
      screen.render();
      input.focus();
}

main();



// deprecated
function new_my_message_old(msg, message_area) {
    var formatted_msg = msg_formatter(msg, 2);
    // var last_message = message_area.items[message_area.items.length-1];
    var all_row=0;
    for(var i=0;i<message_area.items.length; i++) {
        all_row+=message_area.items[i].height;
    }
    var new_row = message_area.addItem(formatted_msg);
    adjust_row(formatted_msg, new_row);
    // new_row.style.bg = '#444653';
    // new_row.position.top = message_area.itop-1 + all_row;
    // debugger
    message_area.scrollTo(message_area.items.length);
    screen.render();
}

function new_bot_message_old(msg, message_area) {
    var formatted_msg = msg_formatter(msg, 1);
    var all_row=0;
    for(var i=0;i<message_area.items.length; i++) {
        all_row+=message_area.items[i].height;
    }
    // var last_message = message_area.items[message_area.items.length-1];
    var new_row = message_area.addItem(formatted_msg);
    adjust_row(formatted_msg, new_row);
    new_row.style.bg = '#343540';
    // new_row.top = message_area.itop-1 + all_row;
    message_area.scrollTo(message_area.items.length);
    screen.render();
}