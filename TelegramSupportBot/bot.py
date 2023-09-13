from telebot import types

import config
import core
import telebot
import random
import datetime
import markup
import sys
from telebot import apihelper



if config.PROXY_URL:
    apihelper.proxy = {'https': config.PROXY_URL}

bot = telebot.TeleBot(config.TOKEN, skip_pending=True)

@bot.message_handler(commands=['start'])
def start(message):
    if '/start agent' in message.text:
        # Здесь обрабатывайте логику для перехода в панель агента
        user_id = message.from_user.id
        if core.check_agent_status(user_id):
            bot.send_message(message.chat.id, '🔑 Ви авторизовані як Агент піддтримки', parse_mode='html',
                             reply_markup=markup.markup_agent())
        else:
            take_password_message = bot.send_message(message.chat.id,
                                                     '⚠️ Тебе немає в базі. Відправ одноразовий пароль доступу.',
                                                     reply_markup=markup.markup_cancel())
            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(take_password_message, get_password_message)
    else:
        bot.send_message(
            message.chat.id,
            '',
            parse_mode='html',
            disable_notification=True,
        )
        # Здесь обрабатывайте логику для остальных случаев
        user_id = message.chat.id
        markup_main = markup.markup_main(user_id)
        bot.send_message(message.chat.id,
                         '👋🏻 Привіт! Це бот для технічної підтримки абонентів.\nЯкщо у Вас є якісь питання - натисніть на кнопку <b>Надіслати запит</b> і ми якнайшвидше Вам відповімо!',
                         parse_mode='html', reply_markup=markup_main)


@bot.message_handler(commands=['agent'])
def agent(message):
    user_id = message.from_user.id

    if core.check_agent_status(user_id) == True: 
        bot.send_message(message.chat.id, '🔑 Вы авторизовані як Агент підтримки', parse_mode='html', reply_markup=markup.markup_agent())

    else:
        take_password_message = bot.send_message(message.chat.id, '⚠️ Тебе немає в базі. Відправ одноразовий пароль доступу.', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_password_message, get_password_message)


@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.from_user.id

    if str(user_id) == config.ADMIN_ID:
        bot.send_message(message.chat.id, '🔑 Вы авторизовані як Адмін', reply_markup=markup.markup_admin())
    else:
        bot.send_message(message.chat.id, '🚫 Ця команда доступна тільки адміністратору.')


@bot.message_handler(content_types=['text'])
def send_text(message):
    user_id = message.from_user.id

    if message.text == '✏️ Надіслати запит':
        take_new_request = bot.send_message(message.chat.id, 'Введіть свій запит і ми якнайшвидше Вам відповімо.', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_new_request, get_new_request)

    elif message.text == '✉️ Мої запити':
        markup_and_value = markup.markup_reqs(user_id, 'my_reqs', '1')
        markup_req = markup_and_value[0]
        value = markup_and_value[1]

        if value == 0:
            bot.send_message(message.chat.id, 'У вас пока що немає запитів.', reply_markup=markup.markup_main(user_id))
        else:
            bot.send_message(message.chat.id, 'Ваші запити:', reply_markup=markup_req, parse_mode='HTML')
    elif message.text == 'Повернутись до головного меню':
        # Здесь выполняется переход на /agent
        # Например, можно отправить пользователю ссылку на /agent
        agent_url = "https://t.me/Elancom_bot?start=agent"  # Замените на ваш URL
        bot.send_message(
            message.chat.id,
            f"Ви переходите до панелі агента. [/agent]({agent_url})",
            parse_mode='Markdown'
        )

    else:
        bot.send_message(message.chat.id, 'Ви повернулись до головного меню.', parse_mode='html', reply_markup=markup.markup_main(user_id))


def get_password_message(message):
    password = message.text
    user_id = message.from_user.id

    if password == None:
        send_message = bot.send_message(message.chat.id, '⚠️ Ви надсилаєте не текст. Спробуйте ще раз.', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(send_message, get_password_message)

    elif password.lower() == 'скасувати':
        bot.send_message(message.chat.id, 'Скасовано.', reply_markup=markup.markup_main(user_id))
        return

    elif core.valid_password(password) == True:
        core.delete_password(password)
        core.add_agent(user_id)

        bot.send_message(message.chat.id, '🔑 Ви авторизовані як Агент підтримкм', parse_mode='html', reply_markup=markup.markup_main(user_id))
        bot.send_message(message.chat.id, 'Оберіть розділ технічної панелі:', parse_mode='html', reply_markup=markup.markup_agent())

    else:
        send_message = bot.send_message(message.chat.id, '⚠️ Невірний пароль. Спробуй ещё раз.', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(send_message, get_password_message)


def get_agent_id_message(message):
    user_id = message.from_user.id
    agent_id = message.text

    if agent_id == None:
        take_agent_id_message = bot.send_message(message.chat.id, '⚠️ Ви надсилаєте не текст. Спробуйие ще раз.', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_agent_id_message, get_agent_id_message)

    elif agent_id.lower() == 'скасувати':
        bot.send_message(message.chat.id, 'Скасовано.', reply_markup=markup.markup_main(user_id))
        return

    else:
        core.add_agent(agent_id)
        bot.send_message(message.chat.id, '✅ Агент успішно доданий.', reply_markup=markup.markup_main(user_id))
        bot.send_message(message.chat.id, 'Оберіть розділ адмін панелі:', reply_markup=markup.markup_admin())


def get_new_request(message):
    request = message.text
    user_id = message.from_user.id
    check_file = core.get_file(message)

    #Если пользователь отправляет файл
    if check_file != None:
        file_id = check_file['file_id']
        file_name = check_file['file_name']
        type = check_file['type']
        request = check_file['text']

        if str(request) == 'None':
            take_new_request = bot.send_message(message.chat.id, '⚠️ Ви не ввели ваш запит. Спробуйте щё раз, відправте текст разом з файлом.', reply_markup=markup.markup_cancel())

            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(take_new_request, get_new_request)

        else:
            req_id = core.new_req(user_id, request)
            core.add_file(req_id, file_id, file_name, type)

            bot.send_message(message.chat.id, f'✅ Ваш запит за ID {req_id} створено. Подивитись поточні запити можна натиснувши <b>Мої поточні запити</b>', parse_mode='html', reply_markup=markup.markup_main(user_id))
    
    #Если пользователь отправляет только текст
    else:
        if request == None:
            take_new_request = bot.send_message(message.chat.id, '⚠️ Тип, що відпрвляється не підтримується в боті. Спробуйте ще раз відправити ваш запит, використавши один з доступних типів даних (текст, файли, фото, відео, аудіо, голосові повідомлення)', reply_markup=markup.markup_cancel())

            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(take_new_request, get_new_request)

        elif request.lower() == 'скасувати':
            bot.send_message(message.chat.id, 'Скасовано.', reply_markup=markup.markup_main(user_id))
            return

        else:
            req_id = core.new_req(user_id, request)
            bot.send_message(message.chat.id, f'✅ Ваш запит за ID {req_id} створено. Подивитись поточні запити можна натиснувши <b>Мої поточні запити</b>', parse_mode='html', reply_markup=markup.markup_main(user_id))
    send_notification_to_agents(req_id)
def send_notification_to_agents(req_id):
    # Получите список агентов с указанным номером страницы (например, первой страницы)
    agents = core.get_agents(1)

    for agent_tuple in agents:
        agent_id = agent_tuple[0]  # Извлекаем идентификатор агента из кортежа
        # Отправьте уведомление агенту о новом запросе
        bot.send_message(agent_id, f"Отримано новий запит за ID {req_id}.\nБудь-ласка, перевірте панель агента.")

def get_additional_message(message, req_id, status):
    user_id = message.from_user.id
    additional_message = message.text
    check_file = core.get_file(message)

    agent_id = core.get_agent_id_for_request(req_id)

    #Если пользователь отправляет файл
    if check_file != None:
        file_id = check_file['file_id']
        file_name = check_file['file_name']
        file_type = check_file['type']
        additional_message = check_file['text']

        core.add_file(req_id, file_id, file_name, file_type)

    if additional_message == None:
        take_additional_message = bot.send_message(chat_id=message.chat.id, text='⚠️ Тип, що відпрвляється не підтримується в боті. Спробуйте ще раз відправити ваш запит, використавши один з доступних типів даних (текст, файли, фото, відео, аудіо, голосові повідомлення).', reply_markup=markup.markup_cancel())

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_additional_message, get_additional_message, req_id, status)

    elif additional_message.lower() == 'скасувати':
        bot.send_message(message.chat.id, 'Скасовано.', reply_markup=markup.markup_main(user_id))
        return

    else:
        if additional_message != 'None':
            core.add_message(req_id, additional_message, status)

        if check_file != None:
            if additional_message != 'None':
                text = '✅ Ваш файл та повідомлення успішно відправлені!'
            else:
                text = '✅ Ваш файл успішно відправлений!'
        else:
            text = '✅ Ваше повідомлення успішно відправлено!'
        
        bot.send_message(message.chat.id, text, reply_markup=markup.markup_main(user_id))

        if status == 'agent':
            try:
                user_id = core.get_user_id_of_req(req_id)

                if user_id != agent_id:
                    try:
                        if additional_message == 'None':
                            additional_message = ''

                        status_user = 'user'
                        markup_reply = types.InlineKeyboardMarkup()
                        reply_button = types.InlineKeyboardButton("Відповісти",
                                                                  callback_data=f'add_message:{req_id}:{status_user}')
                        markup_reply.add(reply_button)
                        bot.send_message(user_id,
                                         f'⚠️ Отримана нова відповідь на ваш запит ID {req_id}!\n\n🧑‍💻 Elancom:\n{additional_message}',
                                         reply_markup=markup_reply)

                        if file_type == 'photo':
                            bot.send_photo(user_id, photo=file_id, reply_markup=markup.markup_main(user_id))
                        elif file_type == 'document':
                            bot.send_document(user_id, document=file_id, reply_markup=markup.markup_main(user_id))
                        elif file_type == 'video':
                            bot.send_video(user_id, video=file_id, reply_markup=markup.markup_main(user_id))
                        elif file_type == 'audio':
                            bot.send_audio(user_id, audio=file_id, reply_markup=markup.markup_main(user_id))
                        elif file_type == 'voice':
                            bot.send_voice(user_id, voice=file_id, reply_markup=markup.markup_main(user_id))
                        else:
                            bot.send_message(user_id, additional_message, reply_markup=markup.markup_main(user_id))
                    except Exception as user_send_exception:
                        print("Помилка при відправці повідомлення користувачу:", user_send_exception)
            except Exception as get_user_id_exception:
                print("Помилка при отриманні user_id:", get_user_id_exception)

        try:
            if additional_message == 'None':
                additional_message = ''

            # НЕ отправляем уведомление агенту, если агент отправляет ответ
            if status != 'agent':
                # print("Отправляем уведомление агенту")

                # Создаем инлайн-клавиатуру с кнопкой "Открыть запрос"
                callback = 'open_req'
                inline_markup = types.InlineKeyboardMarkup()
                open_request_button = types.InlineKeyboardButton("Відкрити запит",
                                                                 callback_data=f'open_req:{req_id}:{callback}-{req_id}')
                inline_markup.add(open_request_button)

                # Отправляем сообщение с кнопкой "Открыть запрос"
                bot.send_message(agent_id,
                                 f'Отримано нова відповідь на запит ID {req_id}.\nБудь-ласка, перевірте панель агента.',
                                 reply_markup=inline_markup)
        except Exception as agent_send_exception:
            print("Помилка при відправці повідомлення агенту:", agent_send_exception)



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id

    if call.message:
        if ('my_reqs:' in call.data) or ('waiting_reqs:' in call.data) or ('answered_reqs:' in call.data) or ('confirm_reqs:' in call.data):
            """
            Обробники кнопок для:

            ✉️ Мои запросы
            ❗️ Ожидают ответа от поддержки,
            ⏳ Ожидают ответа от пользователя
            ✅ Завершенные запросы  
            """

            parts = call.data.split(':')
            callback = parts[0]
            number = parts[1]
            markup_and_value = markup.markup_reqs(user_id, callback, number)
            markup_req = markup_and_value[0]
            value = markup_and_value[1]

            if value == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ Запити не знайдено.', reply_markup=markup.markup_main(user_id))
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Натисніть на запит, щоб переглянути історію переписки, або додати повідомлення:', reply_markup=markup_req)
            except:
                bot.send_message(chat_id=call.message.chat.id, text='Ваші запити:', reply_markup=markup_req, parse_mode='HTML')

            bot.answer_callback_query(call.id)

        #Открыть запрос
        elif 'open_req:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            callback = parts[2]

            req_status = core.get_req_status(req_id)
            request_data = core.get_request_data(req_id, callback)
            len_req_data = len(request_data)

            i = 1
            for data in request_data:
                if i == len_req_data:
                    markup_req = markup.markup_request_action(req_id, req_status, callback)
                else:
                    markup_req = None

                bot.send_message(chat_id=call.message.chat.id, text=data, parse_mode='html', reply_markup=markup_req)

                i += 1

            bot.answer_callback_query(call.id)

        #Добавить сообщение в запрос
        elif 'add_message:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            status_user = parts[2]

            take_additional_message = bot.send_message(chat_id=call.message.chat.id,
                                                       text='Відправте ваше повідомлення, використавши один з доступних типів даних (текст, файли, фото, відео, аудіо, голосові повідомлення)',
                                                       reply_markup=markup.markup_cancel())

            if status_user == 'agent':
                req_status = core.get_req_status(req_id)
                if req_status == 'waiting':
                    agent_id = call.from_user.id
                    core.update_request_agent(req_id, agent_id)


            bot.register_next_step_handler(take_additional_message, get_additional_message, req_id, status_user)

            bot.answer_callback_query(call.id)

        #Завершить запрос
        elif 'confirm_req:' in call.data:
            parts = call.data.split(':')
            confirm_status = parts[1]
            req_id = parts[2]

            if core.get_req_status(req_id) == 'confirm':
                bot.send_message(chat_id=call.message.chat.id, text="⚠️ Этот запрос уже завершен.", reply_markup=markup.markup_main(user_id))
                bot.answer_callback_query(call.id)

                return
            
            #Запросить подтверждение завершения
            if confirm_status == 'wait':
                bot.send_message(chat_id=call.message.chat.id, text="Для завершения запроса - нажмите кнопку <b>Подтвердить</b>", parse_mode='html', reply_markup=markup.markup_confirm_req(req_id))
            
            #Подтвердить завершение
            elif confirm_status == 'true':
                core.confirm_req(req_id)
                
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="✅ Запрос успешно завершён.", reply_markup=markup.markup_main(user_id))
                except:
                    bot.send_message(chat_id=call.message.chat.id, text="✅ Запрос успешно завершён.", reply_markup=markup.markup_main(user_id))

                bot.answer_callback_query(call.id)

        #Файлы запроса
        elif 'req_files:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            callback = parts[2]
            number = parts[3]

            markup_and_value = markup.markup_files(number, req_id, callback)
            markup_files = markup_and_value[0]
            value = markup_and_value[1]

            if value == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ Файлы не обнаружены.', reply_markup=markup.markup_main(user_id))
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Нажмите на файл, чтобы получить его.', reply_markup=markup_files)
            except:
                bot.send_message(chat_id=call.message.chat.id, text='Нажмите на файл, чтобы получить его.', reply_markup=markup_files)

            bot.answer_callback_query(call.id)

        #Отправить файл
        elif 'send_file:' in call.data:
            parts = call.data.split(':')
            id = parts[1]
            type = parts[2]

            file_id = core.get_file_id(id)


            if type == 'photo':
                bot.send_photo(call.message.chat.id, photo=file_id, reply_markup=markup.markup_main(user_id))
            elif type == 'document':
                bot.send_document(call.message.chat.id, document=file_id, reply_markup=markup.markup_main(user_id))
            elif type == 'video':
                bot.send_video(call.message.chat.id, video=file_id, reply_markup=markup.markup_main(user_id))
            elif type == 'audio':
                bot.send_audio(call.message.chat.id, audio=file_id, reply_markup=markup.markup_main(user_id))
            elif type == 'voice':
                bot.send_voice(call.message.chat.id, voice=file_id, reply_markup=markup.markup_main(user_id))
            
            bot.answer_callback_query(call.id)

        #Вернуться назад в панель агента
        elif call.data == 'back_agent':

            markup_agent = markup.markup_agent()  # Создаем клавиатуру для агента
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text='🔑 Вы авторизовані як Агент підтримки', parse_mode='html',
                                      reply_markup=markup_agent)
            except:
                bot.send_message(call.message.chat.id, '🔑 Вы авторизовані як Агент підтримки', parse_mode='html',
                                 reply_markup=markup_agent)

            bot.answer_callback_query(call.id)
            return

        #Вернуться назад в панель админа
        elif call.data == 'back_admin':
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='🔑 Ви авторизовані як Адмін', parse_mode='html', reply_markup=markup.markup_admin())
            except:
                bot.send_message(call.message.chat.id, '🔑 Ви авторизовані як Адмін', parse_mode='html', reply_markup=markup.markup_admin())

            bot.answer_callback_query(call.id)

        #Добавить агента
        elif call.data == 'add_agent':
            take_agent_id_message = bot.send_message(chat_id=call.message.chat.id, text='Для того, щоб додати агента підтримки - введіть його ID Telegram.', reply_markup=markup.markup_cancel())
            bot.register_next_step_handler(take_agent_id_message, get_agent_id_message)

        #Все агенты
        elif 'all_agents:' in call.data:
            number = call.data.split(':')[1]
            markup_and_value = markup.markup_agents(number)
            markup_agents = markup_and_value[0]
            len_agents = markup_and_value[1]

            if len_agents == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ Агентів не знайдено.', reply_markup=markup.markup_main(user_id))
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Натисніть на агента підтримки, для того щоб його видалити', parse_mode='html', reply_markup=markup_agents)
            except:
                bot.send_message(call.message.chat.id, 'Натсиніть на агента підтримки, щоб його видалити', parse_mode='html', reply_markup=markup_agents)

            bot.answer_callback_query(call.id)

        #Удалить агента
        elif 'delete_agent:' in call.data:
            agent_id = call.data.split(':')[1]
            core.delete_agent(agent_id)

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Натсиніть на агента підтримки, щоб його видалити', parse_mode='html', reply_markup=markup.markup_agents('1')[0])
            except:
                bot.send_message(call.message.chat.id, 'Натсиніть на агента підтримки, щоб його видалити', parse_mode='html', reply_markup=markup.markup_agents('1')[0])

            bot.answer_callback_query(call.id)

        #Все пароли
        elif 'all_passwords:' in call.data:
            number = call.data.split(':')[1]
            markup_and_value = markup.markup_passwords(number)
            markup_passwords = markup_and_value[0]
            len_passwords = markup_and_value[1]

            if len_passwords == 0:
                bot.send_message(chat_id=call.message.chat.id, text='⚠️ Паролі не знайдено.', reply_markup=markup.markup_main(user_id))
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Натсиніть на пароль, щоб його видалити', parse_mode='html', reply_markup=markup_passwords)
            except:
                bot.send_message(call.message.chat.id, 'Натсиніть на пароль, щоб його видалити', parse_mode='html', reply_markup=markup_passwords)

            bot.answer_callback_query(call.id)

        #Удалить пароль
        elif 'delete_password:' in call.data:
            password = call.data.split(':')[1]
            core.delete_password(password)

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Натсиніть на пароль, щоб його видалити', parse_mode='html', reply_markup=markup.markup_passwords('1')[0])
            except:
                bot.send_message(call.message.chat.id, 'Натсиніть на пароль, щоб його видалити', parse_mode='html', reply_markup=markup.markup_passwords('1')[0])

            bot.answer_callback_query(call.id)

        #Сгенерировать пароли
        elif call.data == 'generate_passwords':
            #10 - количество паролей, 16 - длина пароля
            passwords = core.generate_passwords(10, 16) 
            core.add_passwords(passwords)

            text_passwords = ''
            i = 1
            for password in passwords:
                text_passwords += f'{i}. {password}\n'
                i += 1
            
            bot.send_message(call.message.chat.id, f"✅ Згенеровано {i-1} паролей:\n\n{text_passwords}", parse_mode='html', reply_markup=markup.markup_main(user_id))
            bot.send_message(call.message.chat.id, 'Натсиніть на пароль, щоб його видалити', parse_mode='html', reply_markup=markup.markup_passwords('1')[0])

            bot.answer_callback_query(call.id)

        #Остановить бота
        elif 'stop_bot:' in call.data:
            status = call.data.split(':')[1]

            #Запросить подтверждение на отключение
            if status == 'wait':
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Ви точно хочете відключити бота?", parse_mode='html', reply_markup=markup.markup_confirm_stop())
                except:
                    bot.send_message(call.message.chat.id, f"Ви точно хочете відключити бота?", parse_mode='html', reply_markup=markup.markup_confirm_stop())

            #Подтверждение получено
            elif status == 'confirm':
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='✅ Бот відключений.')
                except:
                    bot.send_message(chat_id=call.message.chat.id, text='✅ Бот відключений.')

                bot.answer_callback_query(call.id)
                bot.stop_polling()
                sys.exit()



if __name__ == "__main__":
    bot.polling(none_stop=True)