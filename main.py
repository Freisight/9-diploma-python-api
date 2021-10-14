import requests
from tqdm import tqdm
from pprint import pprint
import json
import os

# заменяем директорию на место размещения скрипта.
dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir)

with open('token.txt', 'r') as file_object:
    token_vk = file_object.read().strip()


class GetPhoto:
    def __init__(self, token, owner, album='profile'):
        self.token = token
        self.owner = owner
        self.album = album

    def get_links(self, count=5, album='profile'):
        all_links = {}
        URL = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': self.owner,
            'album_id': self.album,
            'photo_sizes': 1,
            'access_token': self.token,
            'v': '5.131',
            'extended': 1
            }
        all_photo = requests.get(URL, params=params).json()
        photo_count = all_photo['response']['count']
        # проверяем нужное количество фотографий в альбоме
        if count > photo_count:
            print(f'Запрошено {count} фотографий, но в альбоме всего {photo_count} - загрузим, что есть! ')
            count = photo_count
        elif count <= photo_count:
            print('В альбоме есть нужное количество изображений.')

        for i in range(count):
            url = all_photo['response']['items'][i]['sizes'][-1]['url']
            size = all_photo['response']['items'][i]['sizes'][-1]['type']
            likes = all_photo['response']['items'][i]['likes']['count']
            if all_photo['response']['items'][i]['likes']['count'] in all_links:
                likes = str(likes) + '_' + str(all_photo['response']['items'][i]['date'])
            all_links[likes] = [url, size]
        return all_links

    def upload_to_yandex(self, link_upload):
        token_yandex = input("Введите ваш токен с Полигона Яндекс: ")
        json_file = []
        id = self.owner

        # адрес для создания новой папки
        new_folder = 'https://cloud-api.yandex.net:443/v1/disk/resources'

        # адрес для загрузки
        upload = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload'
        headers = {'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(token_yandex)}

        # создание папки на облачном сервере с ID пользователя
        requests.put(new_folder, headers=headers, params={'path': 'disk:/id{}_album{}'.format(id, self.album)})

        # надо как-то сюда новое имя вкорячить для папки и потом еще ее передавать от пользователя
        for name, link in tqdm(link_upload.items()):
            params = {'path': 'disk:/id{}_album{}/{}'.format(id, self.album, str(name) + '.jpg'), 'url': link[0]}
            requests.post(upload, headers=headers, params=params)
            json_file.append({"file_name": str(name) + ".jpg", "size": link[1]})

        with open('id{}_al{}_json.txt'.format(id, self.album), 'w') as outfile:
            json.dump(json_file, outfile)

    def get_links_and_upload_to_yandex(self, count=5, album="profile"):
        '''
        Соединяет в себе два метода сразу - получения
        ссылок и отправки на Яндекс.диск.
        '''
        links = self.get_links(count, album)
        self.upload_to_yandex(links)

command = {}


def add_id():
    get_id = input('Какой ID пользователя? ')
    command['id'] = get_id
    menu()


def add_album():
    get_album = input('Какой ID Альбома? ')
    command['album'] = get_album
    menu()


def add_count():
    get_count = int(input('Сколько фотографий скачиваем? '))
    command['count'] = get_count
    menu()


def read_command():
    pprint(command)
    menu()


def unknown_command():
    print('Неизвестная команда')
    menu()


def load_to_yandex():
    new_object = GetPhoto(token_vk, command['id'], command.get('album', 'profile'))
    new_object.get_links_and_upload_to_yandex(command.get('count', 5))


def menu():
    actions = {
        'id': add_id,
        'album': add_album,
        'count': add_count,
        'command': read_command,
        'upload': load_to_yandex
        }
    action = input('Введите команду: ').lower()
    get_action = actions.get(action, unknown_command)
    get_action()


if __name__ == '__main__':
    menu()
