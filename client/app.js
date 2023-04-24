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
    tile: 'productBotDemo',
});
screen.enableInput();
var can_send = true;

/////// Const ///////
const role_map = {
    1: 'Saul',
    2: 'You',
};
const banner_string = `
        _           _   _           _   
    ___| |__   __ _| |_| |__   ___ | |_ 
   / __| '_ \\ / _\` | __| '_ \\ / _ \\| __|
  | (__| | | | (_| | |_| |_) | (_) | |_ 
   \\___|_| |_|\\__,_|\\__|_.__/ \\___/ \\__|
`;

/////// Function ////////

function swith_session(cur_session, next_session) {

}

function on_init() {
    // setup connection to backend and render first chatbot message
    socket.emit('socket connected');
}
function init_components() {
    
}

function msg_formatter(msg, role) {
    // role is int
    var formatted = `${role_map[role]}: ${msg}`;
    return formatted;
}

function new_my_message(msg, message_area) {
    var new_row = message_area.addItem(msg_formatter(msg, 2));
    new_row.style.bg = '#444653';
    message_area.scrollTo(message_area.items.length+1);
    screen.render();
}

function new_bot_message(msg) {
    var new_row = message_area.addItem(msg_formatter(msg, 1));
    new_row.style.bg = '#343540';
    message_area.scrollTo(message_area.items.length+1);
    screen.render();
}

function send_message() {
    
}

function input_link() {
    
}

function main() {
    on_init();
    socket.on('new message', (msg) => {
        new_bot_message(msg);
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
        height: '80%',
        top: message_area_top,
        left: 0,

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
        height: '10%',
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
        var message = this.getValue();
        try {
        //   await channel.sendMessage({
        //     text: message,
        //   });
            // to do send it to client side
            log(message)
        } catch (err) {
          // error handling
        } finally {
          this.clearValue();
          new_my_message(message, message_area);
          screen.render();
          can_send = false;
        }
      });
  
      // Append our box to the screen.
      screen.key(['escape', 'q', 'C-c'], function() {
        return process.exit(0);
      });

      screen.append(input)

      screen.render();
      input.focus();
}

main();