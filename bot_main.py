import telebot, uuid, os, requests, time
memory = {}
def bot_main():
    path = os.getcwd()
    print("Текущая рабочая директория %s" % path)
    token = '1002705356:AAH6tQVXl_wW97YoL77BkoYQwXMBVjTI3M8'
    bot = telebot.TeleBot(token)


    keyboard1 = telebot.types.ReplyKeyboardMarkup()
    keyboard1.row('Ввести новый тикет', 'Выход')
    keyboard2 = telebot.types.ReplyKeyboardMarkup()
    keyboard2.row('Ввести новый тикет', 'Завершить', 'Выход',)
    name = ''
    surname = []
    id = ''
    new_path = ''
    age = 0
    #login = 'zambas124@gmail.com'
    login = 'a.pisarenko@akrikhin.ru'
    #key = 'TNPqlBA55hkrZVVmRWjBvY~tgQAGyrlwYvuKsLg22VIdrsDoJOPk9ofrewo-4RZIIX3oL07Bk80KETRxYHlwTQHl904cRce2'
    key = 'HqQ-qKwHZg6Brfnbv2pL5UBDnRTOaSiz35JZx~Ynsa4C9v4WcZPsiAGgngzx-JJ9hhpGwWPDkGwm7cdaoSF2-1re6z5TkZWD'



    @bot.message_handler(content_types=['text'])
    def start(message):
        if message.text == 'Ввести новый тикет':
            bot.send_message(message.chat.id, "Введите описание проблемы", reply_markup=keyboard1)
            global memory
            id = uuid.uuid4().__str__()
            new_path = path + '/' + id
            memory.update({id: {'path': new_path}})
            os.mkdir(new_path)
            bot.register_next_step_handler(message, get_name, id) #следующий шаг – функция get_name
            print('Новый клиент', id)
        else:
            bot.send_message(message.chat.id, "Нажмите кнопку: Ввести новый тикет", reply_markup=keyboard1)

    def get_name(message, id): #получаем фамилию
        global memory
        mem = memory.get(id)
        if message.text:
            name = message.text
            mem.update({'name': name, 'files': [], 'files_uploaded': []})
            bot.send_message(message.chat.id, 'Приложите файл, если есть или нажмите выход')
            bot.register_next_step_handler(message, get_surname, id)

    def get_surname(message, id):
        global memory
        mem = memory.get(id)
        if message.document or message.photo:
            files = mem.get('files')
            if message.document:
                files_new = files + [message.document,]
            else:
                files_new = files + [message.photo[-1], ]
            mem.update({'files': files_new})
            bot.send_message(message.chat.id, 'Еще файл?', reply_markup=keyboard2)
            bot.register_next_step_handler(message, get_surname, id)
        else:
            quit(message, id)

    def quit(message, id):
        global memory
        mem = memory.get(id)
        surname = mem.get('files')
        new_path = mem.get('path')
        for i in surname:
            file = bot.get_file(i.file_id)
            downloaded_file = bot.download_file(file.file_path)
            with open(new_path + '/{0}'.format(i.file_id), 'wb') as new_file:
                new_file.write(downloaded_file)
                new_file.close()
        bot.send_message(message.chat.id, 'Ожидайте.....')
        task_id = create_task(id) # создание и отправка таска
        bot.send_message(message.chat.id, 'Покедово, был создан тикет {0}'.format('https://pyrus.com/t#id{0}'.format(task_id)))
        bot.send_message(message.chat.id, '\tC описанием: ')
        bot.send_message(message.chat.id, '\t' + mem.get('name'))
        bot.send_message(message.chat.id, '\tи {0} вложения'.format(len(surname)))

    def autorization():
        url = "https://api.pyrus.com/v4/auth?login={0}&security_key={1}".format(login, key)
        responce = requests.get(url)
        access_token = responce.json().get('access_token')
        return access_token

    def upload_files(access_token, id):
        import requests
        global memory
        mem = memory.get(id)
        files_mem = mem.get('files')
        files_uploaded = mem.get('files_uploaded')
        for file in files_mem:
            headers = {
                'authorization': 'Bearer {0}'.format(access_token)
            }
            if getattr(file, 'file_name', None):
                name = file.file_name or file.id
            else:
                name = file.file_id
            files = {'file': (name, open(path + '/' + id + '/' + file.file_id, 'rb'))}
            response = requests.post('https://api.pyrus.com/v4/files/upload', headers=headers, files=files)
            resp = response.json()
            files_uploaded.append(resp.get('guid'))
            print(response.status_code)
        return mem

    def create_task(id):
        global memory
        access_token = autorization()
        mem = upload_files(access_token, id)
        files = mem.get('files_uploaded')
        headers = {
            'authorization': 'Bearer {0}'.format(access_token)
        }
        body = {
            "text": mem.get('name'),
            "responsible": {
                "id": 1733
            },
            "attachments": files,
            "participants": [
                {
                    "id": 1733
                },
                {
                    "email": login
                }
            ]
        }
        responce = requests.post('https://api.pyrus.com/v4/tasks', json=body, headers=headers)
        data = responce.json()
        print(responce.status_code)
        print(responce.text)
        return data.get('task').get('id')

    bot.polling(none_stop=True)

