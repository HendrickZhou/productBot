import agent

cur_session = None

def update_link(link):
    global cur_session
    if cur_session.session_id != 'qna':
        return
    return cur_session.update_link(link)

def setup_session(session):
    global cur_session
    sessino_cls = agent.SessionFactory().new_session(session)
    cur_session = sessino_cls()
    return cur_session.intro()

def continue_session(session):
    global cur_session
    sessino_cls = agent.SessionFactory().new_session(session)
    cur_session = sessino_cls()
    if session == 'qna':
        return cur_session.intro()

def reply(msg):
    return cur_session.reply(msg)


def get_cur_session():
    global cur_session
    if cur_session is None:
        return 'unassigned'
    else:
        return cur_session.session_id
    


