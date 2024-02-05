import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import re
from sync_bot import post_msg
from datetime import datetime, timezone
session = requests.Session()


# где хранятся данные. тк я не умею в субд, то это просто json
bd = r'C:\Users\Dmitrii\PycharmProjects\channel_parsing_filter\data_list.json'
last = 'last_good_id'

# поиск по regex
patterns = [r'https://[^"]+\.jpg', r'https://[^"]+\.mp4', ]

cooldown: int = 60*60*24*30   # за какой период искать дубликаты


def get_first_media_url(soup_elem, message_id):
    for media in soup_elem:
        elem = media.get('style')
        if elem:
            for p in patterns:
                match = re.findall(p, elem)
                if match:
                    if str(message_id) in media.get('href'):
                        return match[0]
                    else:
                        return None


#  вытащить из поста данные
def get_message_data(group: str, message_id: int) -> dict | bool:
    link = f'https://t.me/{group}/{message_id}?embed=1&mode=tme'
    response = session.get(link)
    print('r', message_id)
    soup = BeautifulSoup(response.text, features="html.parser")

    # если пост не существует
    if soup.find('div', class_="tgme_widget_message_error"):
        return False

    # поиск текста
    js_message = str(soup.find('div', class_="tgme_widget_message_text js-message_text")).replace('<br/>', '\n')
    string = BeautifulSoup(js_message, features="html.parser")
    message_text = string.get_text().replace(' \n', '\n')

    # поиск ссылки на медиа из поста
    grouped_media = soup.findAll('a')
    first_media_url = get_first_media_url(grouped_media, message_id)

    # дата поста
    unix_timestamp = ''
    msg_date = soup.find('time', class_="datetime")
    if msg_date:
        msg_date = msg_date.get('datetime')
        unix_timestamp = int(datetime.fromisoformat(msg_date).replace(tzinfo=timezone.utc).timestamp())

    output = {
        'text': message_text,
        'link': link,
        # 'grouped': len(grouped_media),
        'unix': unix_timestamp,
        'media_url': first_media_url,
    }
    return output


def do_task(channel: str, msg_id: int, far: bool):
    not_found = 0
    last_good_id = str(msg_id)

    # читать, пока не будет много ненайденных подряд
    while not_found < 30 or far:
        msg = get_message_data(channel, msg_id)

        # если пост существует
        if msg:
            far = False
            not_found = 0
            msg_link = msg.get('link').split('?')[0]
            last_good_id = msg_link.split('/')[-1]
            unix_time = msg.get('unix')
            media_url = msg.get('media_url')
            if media_url:
                file_id = media_url.split('/')[-1].split('.')[0]
                # проверить уникальность
                if not is_spam(content=file_id, unix_time=unix_time):
                    # опубликовать
                    post_msg(text=msg_link)

            # сохранить последний пост
            with open(last, 'w') as f:
                f.write(last_good_id)

        else:  # если пост не найден
            not_found += 1

        # след пост
        msg_id = msg_id + 1
    print('End reached')
    print('last', f'https://t.me/{channel}/{last_good_id}')


def is_spam(content, unix_time) -> bool:
    spam = False
    mem_erase = False

    # чтение бд
    with open(bd, encoding='utf-8') as f:
        data = json.load(f)

    # перебор старых записей
    for old_msg in data:
        old_time, old_text = old_msg

        # если найдена устаревшая запись
        dif = unix_time - cooldown
        # print('unix_time:', unix_time, 'dif:', dif, 'old_time:', old_time, )
        if dif > old_time:
            mem_erase = old_msg  # пометить на удаление

        # если найдено повторение
        elif content == old_text:
            print("❌")
            spam = True
            break

    # чистка памяти
    if mem_erase:
        erase_until = data.index(mem_erase) + 1
        data = data[erase_until:]
        print(erase_until, 'erased until', mem_erase)

    if not spam:
        # запись в бд
        new_line = tuple((unix_time, content,))
        data.append(new_line)
        with open(bd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            print('✅')
    return spam

