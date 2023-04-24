var blessed = require('neo-blessed');

function main() {
    const screen = blessed.screen({
        smartCSG: true,
        tile: 'productBotDemo',
    });

    var box_session_Chat = blessed.box({
        // position 
        top: 0,
        width: '20%',
        height: '10%',
        left: 0,

        // text
        content: 'Casual Chat',
        tags: true,

        // style
        style: {
            bg: 'magenta',
            hover: {
                bg: 'green'
            }
        }
    });

    var box_session_QNA = blessed.box({
        // position 
        top: 0,
        width: '20%',
        height: '10%',
        left: '30%',

        // text
        content: 'Q&A on product',
        tags: true,

        // style
        style: {
            bg: 'magenta',
            hover: {
                bg: 'green'
            }
        }
    });

    var box_session_Recomend = blessed.box({
        // position 
        top: 0,
        width: '20%',
        height: '10%',
        left: '60%',

        // text
        content: 'Recommendation',
        tags: true,

        // style
        style: {
            bg: 'magenta',
            hover: {
                bg: 'green'
            }
        }
    });

    box_session_Chat.on('click', (data) => {
        box.setContent('Casual Chat ing');
        // change session
    });

    screen.append(box_session_QNA);
    screen.append(box_session_Recomend);
    screen.append(box_session_Chat);

    var message_area = blessed.list({
        // position
        align: 'left',
        width: '100%',
        height: '80%',
        top: '10%',
        left: 0,

        // interaction
        scrollbar: {
            ch: ' ',
            inverse: true,
        },
        mouse: true,
        keys: true,

        // content
        items: []
    });
    screen.append(message_area);

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
          screen.render();
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