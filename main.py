import requests
from tqdm import tqdm
from pprint import pprint
import json

with open('token.txt', 'r') as file_object:
    token_vk = file_object.read().strip()


class Get_last_photo:
    def __init__(self, token, owner, album='profile'):
        self.token = token
        self.owner = owner
        self.album = album

    def get_links(self, count=5, album='profile'):
        all_links = {}
        URL = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.owner,
                    'album_id': self.album,
                    'photo_sizes': 1,
                    'access_token': self.token,
                    'v':'5.131',
                    'extended': 1}

        all_photo = requests.get(URL, params=params).json()

        photo_count = all_photo['response']['count']
        
        # проверяем нужное количество фотографий в альбоме
        if count > photo_count:
            print(f'Вы запросили {count} фотографий, но в альбоме всего {photo_count} фотографий - загрузим, что есть! ')
            count = photo_count
        elif count <= photo_count:
            print('В альбоме есть нужное количество изображений.')


        for i in range(count):
            if all_photo['response']['items'][i]['likes']['count'] not in all_links:
                all_links[all_photo['response']['items'][i]['likes']['count']] = [all_photo['response']['items'][i]['sizes'][-1]['url'], all_photo['response']['items'][i]['sizes'][-1]['type']]
            elif all_photo['response']['items'][i]['likes']['count'] in all_links:
                all_links[str(all_photo['response']['items'][i]['likes']['count']) + '_' + str(all_photo['response']['items'][i]['date'])] = [all_photo['response']['items'][i]['sizes'][-1]['url'], all_photo['response']['items'][i]['sizes'][-1]['type']]

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
        requests.put(new_folder, headers=headers, params={'path' : 'disk:/id{}_album{}'.format(id, self.album)})

        # надо как-то сюда новое имя вкорячить для папки и потом еще ее передавать от пользователя
        for name, link in tqdm(link_upload.items()):
            requests.post(upload, headers=headers, params={'path' : 'disk:/id{}_album{}/{}'.format(id, self.album, str(name) + '.jpg'), 'url' : link[0]})
            json_file.append({"file_name": name, "size": link[1]})

        with open('id{}_al{}_json.txt'.format(id, self.album), 'w') as outfile:
            json.dump(json_file, outfile)



    def get_links_and_upload_to_yandex(self, count=5, album="profile"):
        '''
        Метод класса соединяющий в себе сразу два метода - получения ссылок (get_links) и загрузки на яндекс (upload_to_yandex)
        Если не указан count, то возьмет по умолчанию 5 файлов для загрузки, если файлов меньше - сделает сколько есть.
        Вторым параметром указывается ID альбома для загрузки. По умолчанию стоит 'profile', есть ещё 'wall' и...
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




def load_to_yandex():
    new_object = Get_last_photo(token_vk, command['id'], command.get('album', 'profile'))
    new_object.get_links_and_upload_to_yandex(command.get('count', 5))

def menu():
    user_input = input('Введите команду: ')
    if user_input == 'id':
        add_id()
    elif user_input == 'album':
        add_album()
    elif user_input == 'count':
        add_count()
    elif user_input == 'command':
        read_command()
    elif user_input == 'upload':
        load_to_yandex()



menu()

# ID юзера и альбома для теста
# 1647573
# 154979481


# всякая фигня
# создаём объект, указываем только токен и ID пользователя
# new_object = Get_last_photo(token_vk, '1647573', '154979481')
# тестируем получение ссылок
# links = new_object.get_links(5)
# pprint(links)
# вызываем метод для получения ссылок и заливки фотографий из указанного альбома
# new_object.get_links_and_upload_to_yandex(2)