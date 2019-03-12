import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from pprint import pprint
import json
from threading import Thread

def todo_list_maker(chat_id):
    r = requests.get('http://127.0.0.1:4000/data/user', params={'chat_id': chat_id})
    response = json.loads(r.text)

    inlline_keyboard = lambda text, cb_data: InlineKeyboardButton(text=text, callback_data=cb_data)
    todo_list = InlineKeyboardMarkup(inline_keyboard=[
        [inlline_keyboard(title, 'temp'), inlline_keyboard('X', 'done {}'.format(id))] for id, title in response['item']['todos']
    ])
    return todo_list


def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    if content_type == 'text':

        if msg['text'][0] == '/':
            command = msg['text'][1:]

            if command == 'register':
                r = requests.post('http://127.0.0.1:4000/data/user', data={'chat_id':chat_id, 'action':'create'})
                response = json.loads(r.text)
                bot.sendMessage(chat_id, response['message'])

            elif command == 'my':
                r = requests.get('http://127.0.0.1:4000/data/user', params={'chat_id':chat_id})
                response = json.loads(r.text)
                if response['status'] == 200:
                    todo_list = todo_list_maker(chat_id)
                    bot.sendMessage(chat_id, 'TODO LIST', reply_markup=todo_list)
            elif command == 'config':
                pass
            elif command == 'help' or command == 'start':
                msg_text = "명령어:\n/register : 가장 먼저 눌러주세요!(아이디 등록)\n/my : 남아있는 할일 보기\n/config : 알림 설정\n/help : 도움말\n그 외: 할 일로 등록 됨"
                bot.sendMessage(chat_id, msg_text)
            else:
                pass
        else:
            r = requests.post('http://127.0.0.1:4000/data/todo',
                              data={'chat_id': chat_id, 'action': 'create', 'title': msg['text']})
            todo_list = todo_list_maker(chat_id)
            bot.sendMessage(chat_id, 'TODO LIST', reply_markup=todo_list)

def on_callback_query(msg):
    query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, chat_id, query_data)
    bot.answerCallbackQuery(query_id, text='Got it')
    prefix = query_data.split()[0]

    if prefix == 'done':
        todo_id = query_data.split()[1]
        r = requests.post('http://127.0.0.1:4000/data/todo',
                          data={'chat_id': chat_id, 'action': 'done', 'todo_id':todo_id})
        pprint(json.loads(r.text))

        todo_list = todo_list_maker(chat_id)
        bot.sendMessage(chat_id, 'TODO LIST', reply_markup=todo_list)

def thread_schedule():
    while 1:
        tm = time.gmtime(time.time())
        if tm.tm_hour in [0, 4, 10, 14] and tm.tm_min == 00:
            todo_list = todo_list_maker('9999999')
            bot.sendMessage('9999999', 'TODO LIST', reply_markup=todo_list)
        time.sleep(60)

def thread_keepalive():
    while 1:
        bot.getMe()
        time.sleep(59)

if __name__ == '__main__':
    with open('token.json','r') as f:
        TOKEN = json.loads(f.read())['token']
    bot = telepot.Bot(TOKEN)
    MessageLoop(bot, {'chat': on_chat_message,
                      'callback_query': on_callback_query}).run_as_thread()
    print('Listening ...')

    t1 = Thread(target=thread_schedule)
    t2 = Thread(target=thread_keepalive)
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()

    while 1:
        time.sleep(10)