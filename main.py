import requests
from tqdm import tqdm
from pprint import pprint

with open('token.txt', 'r') as file_object:
    token_vk = file_object.read().strip()


class Get_last_photo:
    def __init__(self, token, owner):
        self.token = token
        self.owner = owner

    def get_links(self, count=5, album="profile"):
        all_links = {}
        URL = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.owner,
                    'album_id': album,
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

        # из запроса выдёргиваем все нужные фотографии и запихиваем их в словарь с ссылками и названием файла в виде лайков или даты
        for i in range(count):
            if all_photo['response']['items'][i]['likes']['count'] not in all_links:
                all_links[all_photo['response']['items'][i]['likes']['count']] = all_photo['response']['items'][i]['sizes'][-1]['url']
            elif all_photo['response']['items'][i]['likes']['count'] in all_links:
                all_links[str(all_photo['response']['items'][i]['likes']['count']) + '_' + str(all_photo['response']['items'][i]['date'])] = all_photo['response']['items'][i]['sizes'][-1]['url']

        return all_links


    def upload_to_yandex(self, link_upload):
        # получение токена сделать из файла
        token_yandex = 'AQAAAAAKXC4TAADLW4SJJMLjPkXhv7Z6j0BjI6M'

        id = self.owner

        # адрес для создания новой папки
        new_folder = 'https://cloud-api.yandex.net:443/v1/disk/resources'

        # адрес для загрузки
        upload = 'https://cloud-api.yandex.net:443/v1/disk/resources/upload'
        headers = {'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(token_yandex)}

        #  вот тут надо подставлять имя или id человеква и называть ею папку для загрузки файлов
        requests.put(new_folder, headers=headers, params={'path' : 'disk:/id{}'.format(id)})

        # надо как-то сюда новое имя вкорячить для папки и потом еще ее передавать от пользователя
        for name, link in tqdm(link_upload.items()):
            r = requests.post(upload, headers=headers, params={'path' : 'disk:/id{}/{}'.format(id, str(name) + '.jpg'), 'url' : link})

    def get_links_and_upload_to_yandex(self, count=5, album="profile"):
        '''
        Метод класса соединяющий в себе сразу два метода - получения ссылок (get_links) и загрузки на яндекс (upload_to_yandex)
        Если не указан count, то возьмет по умолчанию 5 файлов для загрузки, если файлов меньше - сделает сколько есть.
        '''
        links = self.get_links(count, album)
        self.upload_to_yandex(links)
        




# создаём объект, указываем только токен и ID пользователя
bulgakov = Get_last_photo(token_vk, 552934290)

# указываем нужное количество ссылок и ID нужного альбома для получения ссылок, пол умолчанию идёт 'profile' - альбом фотографий пользователя.
# links = bulgakov.get_links(7)
# pprint(links)

# загружаем на яндекс по полученным ссылкам
# bulgakov.upload_to_yandex(links)

bulgakov.get_links_and_upload_to_yandex(6)