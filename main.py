import json
import requests
import io
from my_token import yd_token, ipinfo_token

class IpifyClient:
    base_url = 'https://api.ipify.org'
    def get_my_ip(self):
        resp = requests.get(f'{self.base_url}?format=json')
        resp.raise_for_status()
        return resp.json()['ip']


class IpinfoClient:
    base_url = 'https://ipinfo.io'
    def __init__(self, token):
        self.token = token
    def get_geo_info(self, ip):
        url = f'{self.base_url}/{ip}/json'
        resp = requests.get(url, params={'token': self.token})
        resp.raise_for_status()
        return resp.json()

class YD:
    base_url = 'https://cloud-api.yandex.net'

    def __init__(self, token):
        self.headers = {'Authorization': f'OAuth {token}'}

    def create_folder(self, path):
        response = requests.put(f'{self.base_url}/v1/disk/resources',
                                headers=self.headers,
                                params={'path': path})
        return response.status_code in {201, 409}

    def upload_data(self, data: bytes, remote_path: str):
        resp = requests.get(f'{self.base_url}/v1/disk/resources/upload',
                            headers=self.headers,
                            params={'path': remote_path, 'overwrite': 'true'})
        resp.raise_for_status()
        url_upload = resp.json()["href"]

        with io.BytesIO(data) as f:
            resp2 = requests.put(url_upload, data=f.read())
        resp2.raise_for_status()
        return True



def main():
    ipify = IpifyClient()
    ip = ipify.get_my_ip()

    ipinfo = IpinfoClient(ipinfo_token)
    geo_data = ipinfo.get_geo_info(ip)

    json_str = json.dumps(geo_data, ensure_ascii=False, indent=2)
    json_bytes = json_str.encode('utf-8')


    yd = YD(yd_token)
    folder_name = '/IP_Info'
    if yd.create_folder(folder_name):
        print(f'Папка "{folder_name}" создана')
    else:
        print('Ошибка создания папки')
        return
    remote_path = f'{folder_name}/ip_Info.json'
    try:
        yd.upload_data(json_bytes, remote_path)
    except Exception as e:
        print(f'Ошибка загрузки: {e}')


if __name__ == '__main__':
    main()
