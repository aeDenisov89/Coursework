import json
import requests
from my_token import yd_token, ipinfo_token


class YD:
    base_url = 'https://cloud-api.yandex.net'

    def __init__(self, token):
        self.headers = {'Authorization': f'OAuth {token}'}

    def create_folder(self, path):
        response = requests.put(f'{self.base_url}/v1/disk/resources',
                                headers=self.headers,
                                params={'path': path})
        return response.status_code in {201, 409}

    def upload_file(self, path_to_file, path_to_yd):
        resp = requests.get(f'{self.base_url}/v1/disk/resources/upload',
                            headers=self.headers,
                            params={'path': path_to_yd, 'overwrite': 'true'})
        resp.raise_for_status()
        url_upload = resp.json()["href"]

        with open(path_to_file, "rb") as f:
            resp2 = requests.put(url_upload, data=f)

        resp2.raise_for_status()
        return True


def get_my_ip():
    resp = requests.get('https://api.ipify.org?format=json')
    resp.raise_for_status()
    return resp.json()['ip']


def get_geo_info(ip, token):
    url = f'https://ipinfo.io/{ip}/json'
    params = {'token': token}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()


def save_to_json(data, filename='ip_info.json'):
    with open(filename, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    ip = '188.242.138.63'
    geo_data = get_geo_info(ip, ipinfo_token)

    filename = 'ip_info.json'
    save_to_json(geo_data, filename)
    yd = YD(yd_token)
    folder_name = '/IP_Info'
    if yd.create_folder(folder_name):
        print(f'Папка "{folder_name}" создана')
    else:
        print('Ошибка создания папки')
        return
    remote_path = f'{folder_name}/{filename}'
    try:
        yd.upload_file(filename, remote_path)
    except Exception as e:
        print(f'Ошибка загрузки: {e}')


if __name__ == '__main__':
    main()
