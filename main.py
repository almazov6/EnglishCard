import random
import datebase_connect as database
import text

from telebot import types, TeleBot, custom_filters
from telebot.storage import StateMemoryStorage
from telebot.handler_backends import State, StatesGroup

from datebase_connect import random_word, translate_word, others_word, \
    count_words, is_word_in_database

print('Start telegram bot...')

state_storage = StateMemoryStorage()
token_bot = ''
bot = TeleBot(token_bot, state_storage=state_storage)

known_users = []
userStep = {}
buttons = []


def load_start_words(user_id):
    start_words = database.start_word()
    for i in range(len(start_words)):
        database.add_word_to_database(user_id, start_words[i][0],
                                      start_words[i][1])


def show_hint(*lines):
    return '\n'.join(lines)


def show_target(data):
    return f"Верно✅ {data['target_word']} -> {data['translate_word']}"


class Command:
    ADD_WORD = 'Добавить слово ➕'
    DELETE_WORD = 'Удалить слово🔙'
    NEXT = 'Дальше ⏭'


class MyStates(StatesGroup):
    target_word = State()
    translate_word = State()
    another_words = State()


def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        known_users.append(uid)
        userStep[uid] = 0
        print("New user detected, who hasn't used \"/start\" yet")
        return 0


@bot.message_handler(commands=['cards', 'start'])
def create_cards(message):
    cid = message.chat.id
    us_id = message.from_user.id
    if not database.user_id_in_database(cid):
        database.add_user(cid)
        load_start_words(cid)
        known_users.append(cid)
        userStep[cid] = 0
        bot.send_message(cid, text.welcome)
    markup = types.ReplyKeyboardMarkup(row_width=2)

    global buttons
    buttons = []
    target_word = random_word('english_word', us_id)  # брать из БД
    translate = translate_word(target_word)  # брать из БД
    target_word_btn = types.KeyboardButton(target_word)
    buttons.append(target_word_btn)
    others = others_word(target_word, us_id)  # брать из БД
    other_words_btns = [types.KeyboardButton(word) for word in others]
    buttons.extend(other_words_btns)
    random.shuffle(buttons)
    next_btn = types.KeyboardButton(Command.NEXT)
    add_word_btn = types.KeyboardButton(Command.ADD_WORD)
    delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
    buttons.extend([next_btn, add_word_btn, delete_word_btn])

    markup.add(*buttons)

    greeting = f"Выбери перевод слова:\n {translate}"
    bot.send_message(message.chat.id, greeting, reply_markup=markup)
    bot.set_state(message.from_user.id, MyStates.target_word, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['target_word'] = target_word
        data['translate_word'] = translate
        data['other_words'] = others


@bot.message_handler(func=lambda message: message.text == Command.NEXT)
def next_cards(message):
    create_cards(message)


@bot.message_handler(func=lambda message: message.text == Command.DELETE_WORD)
def delete_word(message):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        if (database.count_words(message.from_user.id) - 1) <= 5:
            bot.send_message(message.from_user.id,
                             f'Нельзя удалять последние 5 слов из словаря.')
        else:
            database.del_word_in_database(message.from_user.id,
                                          data['target_word'])
            bot.send_message(message.from_user.id,
                             f'Слово {data['target_word']} удалено.')


@bot.message_handler(func=lambda message: message.text == Command.ADD_WORD)
def add_word(message):
    cid = message.chat.id
    userStep[cid] = 1
    bot.reply_to(message,
                 'Введите слово на английском языке, которое хотите добавить, '
                 'а через пробел введите перевод')
    bot.register_next_step_handler(message, add_database)


def add_database(message):
    words = message.text.split()
    cid = message.from_user.id
    if is_word_in_database(cid, words[0]):
        bot.send_message(cid, f'Слово {words[0]} уже существует.')
    else:
        database.add_word_to_database(cid, words[0], words[1])
        bot.send_message(cid,
                         f'Слово {words[0]} добавлено. '
                         f'Слов в словаре: {database.count_words(cid)}')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def message_reply(message):
    text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        target_word = data['target_word']
        if text == target_word:
            hint = show_target(data)
            hint_text = ["Отлично!❤", hint]
            next_btn = types.KeyboardButton(Command.NEXT)
            add_word_btn = types.KeyboardButton(Command.ADD_WORD)
            delete_word_btn = types.KeyboardButton(Command.DELETE_WORD)
            buttons.extend([next_btn, add_word_btn, delete_word_btn])
            hint = show_hint(*hint_text)
        else:
            for btn in buttons:
                if btn.text == text:
                    btn.text = text + '❌'
                    break
            hint = show_hint("Допущена ошибка!",
                             f"Попробуй ещё раз вспомнить "
                             f"слово {data['translate_word']}")
    markup.add(*buttons)
    bot.send_message(message.chat.id, hint, reply_markup=markup)


bot.add_custom_filter(custom_filters.StateFilter(bot))

bot.infinity_polling(skip_pending=True)
