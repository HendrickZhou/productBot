'use strict'
const blessed = require('neo-blessed');
const socket = require("socket.io-client")(
    process.argv[2] || 'http://localhost:5500'
);
// const BlessedTabContainer = require('blessed-tab-container');
// const blessedContrib = require('blessed-contrib');
// const colors = require('colors');


/////// Global ////////
const screen = blessed.screen({
    smartCSG: true,
    debug: true,
    tile: 'productBotDemo',
});
screen.enableInput();
var can_send = true;

/////// Const ///////
const role_map = {
    1: 'Saul',
    2: 'You',
};
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

/////// Function ////////

function swith_session(cur_session, next_session) {

}

function on_init() {
    // setup connection to backend and render first chatbot message
    socket.emit('test');
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
    }
    message_area.scrollTo(message_area.items.length+1);
    screen.render();
}

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

function send_message() {
    
}

function input_link() {
    
}

function main() {
    on_init();
    socket.on('new message', (msg) => {
        new_bot_message(msg, message_area);
        can_send = true
    });

    var banner = blessed.box({
        top:'-10%',
        width: '100%',
        height: 10,
        left: 0,

        content: banner_string,
    });

    screen.append(banner);

    /////////////////////////////////////////////////
    // session tab definition

    var tab_top = 5;
    var width = '20%';
    var tab_height = 2;

    var unselected_style= {
        bg: 'magenta',
        hover: {
            bg: 'green'
        }
    };
    var selected_style = {
        bg: 'green'
    }

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
        style: {...selected_style},
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

    screen.append(box_session_QNA);
    screen.append(box_session_Recomend);
    screen.append(box_session_Chat);

    /////////////////////////////////////////////////
    // session switch logic

    var cur_session = 0; // 0 unassigned, 1 chat, 2 qna, 3 recommend

    box_session_Chat.on('click', (data) => {
        if(cur_session == 1) return;
        box_session_Chat.style = {...selected_style};
        box_session_QNA.style = {...unselected_style};
        box_session_Recomend.style = {...unselected_style};
        swith_session(cur_session,1);
        cur_session = 1;
        screen.render();
    });
    box_session_QNA.on('click', (data) => {
        if(cur_session == 2) return;
        box_session_QNA.style = {...selected_style};
        box_session_Chat.style = {...unselected_style};
        box_session_Recomend.style = {...unselected_style};
        swith_session(cur_session,2);
        cur_session = 2;
        screen.render();
    });
    box_session_Recomend.on('click', (data) => {
        if(cur_session == 3) return;
        box_session_Recomend.style = {...selected_style};
        box_session_QNA.style = {...unselected_style};
        box_session_Chat.style = {...unselected_style};
        swith_session(cur_session,3);
        cur_session = 3;
        screen.render();
    });


    /////////////////////////////////////////////////
    // message area definition
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
    screen.append(message_area);

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
        if(!can_send) {
            return;
        }
        can_send = false;
        var message = this.getValue();
        try {
            socket.emit('message', message);
        } catch (err) {
          // error handling
        } finally {
          input.clearValue();
          input.focus();
          new_my_message(message, message_area);
        }
      });
  
      // Append our box to the screen.
      screen.key(['escape', 'q', 'C-c'], () => {
        return process.exit(0);
      });

      screen.append(input)

    // var test_block = blessed.ScrollableText({
    //     top: 'center',
    //     left: 'center',
    //     width: '40%',
    //     height: '10%',
    //     content: 'Hello {bold}world{/bold}! Letlasdfkaslfkjlasjfkljaslfjlskjflksajkfljsklfgnkldfglk'
    //     +'lsalfs;default;sdlf',
    //     tags: true,
    //     border: {
    //       type: 'line'
    //     },
    //     // scrollable: true,

    //     style: {
    //       fg: 'white',
    //       bg: 'magenta',
    //       border: {
    //         fg: '#ffffff'
    //       },
    //       hover: {
    //         bg: 'green'
    //       }
    //     }
    // });
    // test_block.noOverflow=false;
    // screen.append(test_block);
    // console.log(test_block.lpos)
    // var el_lpos =  test_block.lpos
    // var new_height = test_block.getScrollHeight();
    
    // test_block.height = new_height

      screen.render();
      input.focus();
}

main();