import requests
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.abspath(os.path.join(current_dir, '../../Key_GIS/key.txt'))

with open(key_path, 'r') as f:
    APPLICATION_TOKEN = f.read().strip()

USERNAME = 'Dorney'

# Авторизация и получение apiKey
login_url = 'https://m2m.cr.usgs.gov/api/api/json/stable/login-token'
login_payload = {
    "username": USERNAME,
    "token": APPLICATION_TOKEN
}

login_resp = requests.post(login_url, json=login_payload)
login_data = login_resp.json()
apiKey = login_data.get('data')
if not apiKey:
    print("Не получили apiKey")
    exit(1)
print("Авторизация успешна")

headers = {
    'X-Auth-Token': apiKey
}

# Запрос scene-search для поиска сцен
scene_search_url = 'https://m2m.cr.usgs.gov/api/api/json/stable/scene-search'
payload = {
    "datasetName": "landsat_ot_c2_l1",
    "maxResults": 1,
    "sceneFilter": {
        "acquisitionFilter": {
            "start": "2025-07-13",
            "end": "2025-07-13"
        }
    }
}

response = requests.post(scene_search_url, json=payload, headers=headers)
if not response.ok:
    print(f"Ошибка запроса scene-search: {response.status_code}")
    exit(1)

data = response.json()
if data.get('errorCode'):
    print(f"Ошибка API: {data['errorCode']} - {data['errorMessage']}")
    exit(1)

search_data = data.get('data', {})
results = search_data.get('results', [])
if not results:
    print("Сцены не найдены")
    exit(0)

scene = results[0]
entity_id = scene.get('entityId')
scene_display_id = scene.get('displayId')
print(f"Найдена сцена: {entity_id}")

# Запрос download-search для получения доступных файлов
download_search_url = 'https://m2m.cr.usgs.gov/api/api/json/stable/download-search'
download_search_payload = {
    # Можно добавить фильтр activeOnly, если нужно
}
download_resp = requests.post(download_search_url, json=download_search_payload, headers=headers)
if not download_resp.ok:
    print(f"Ошибка запроса download-search: {download_resp.status_code}")
    exit(1)

downloads = download_resp.json().get('data', [])
if not downloads:
    print("Нет доступных загрузок.")
    exit(1)

# Фильтруем файлы по entityId сцены (часть entityId совпадает с displayId)
scene_downloads = [d for d in downloads if d.get('entityId', '').startswith('L1_' + scene_display_id)]

if not scene_downloads:
    print("Нет файлов для скачивания, связанных с этой сценой.")
    exit(1)

print(f"Файлов для скачивания: {len(scene_downloads)}")

# Создаем папку для загрузки
download_folder = os.path.join(current_dir, 'downloads')
os.makedirs(download_folder, exist_ok=True)


def accept_eula(download_id):
    url = 'https://m2m.cr.usgs.gov/api/api/json/stable/download-order-load'
    payload = {
        "downloadId": download_id,
        "acceptEula": True
    }
    resp = requests.post(url, json=payload, headers=headers)
    if resp.ok:
        print(f"EULA для downloadId={download_id} принята")
        return True
    else:
        print(f"Ошибка при принятии EULA для downloadId={download_id}: {resp.status_code} {resp.text}")
        return False


def request_download(download_id):
    url = 'https://m2m.cr.usgs.gov/api/api/json/stable/download-request'
    payload = {"downloadId": download_id}
    resp = requests.post(url, json=payload, headers=headers)
    if resp.ok:
        print(f"Запрос download-request для downloadId={download_id} успешен")
        return True
    else:
        print(f"Ошибка download-request для downloadId={download_id}: {resp.status_code} {resp.text}")
        return False


# Активируем загрузки и принимаем EULA, если требуется
for file_info in scene_downloads:
    download_id = file_info.get('downloadId')
    display_id = file_info.get('displayId')
    eula_code = file_info.get('eulaCode')
    print(f"Обрабатываем файл: {display_id} (downloadId: {download_id})")

    if eula_code:
        if not accept_eula(download_id):
            print(f"Пропускаем файл {display_id} из-за непринятой лицензии")
            continue

    if not request_download(download_id):
        print(f"Пропускаем файл {display_id} из-за ошибки запроса download-request")
        continue

# Ждем некоторое время, чтобы сервер подготовил файлы
print("Ожидание подготовки файлов (примерно 10 секунд)...")
time.sleep(10)

# Получаем список доступных файлов с url
download_retrieve_url = 'https://m2m.cr.usgs.gov/api/api/json/stable/download-retrieve'
retrieve_payload = {"downloadApplication": "EE"}
retrieve_resp = requests.post(download_retrieve_url, json=retrieve_payload, headers=headers)

if not retrieve_resp.ok:
    print(f"Ошибка запроса download-retrieve: {retrieve_resp.status_code}")
    exit(1)

retrieve_data = retrieve_resp.json()
if retrieve_data.get('errorCode'):
    print(f"Ошибка API download-retrieve: {retrieve_data['errorCode']} - {retrieve_data['errorMessage']}")
    exit(1)

available_files = retrieve_data.get('data', {}).get('available', [])

# Создаем словарь для быстрого поиска по downloadId
available_map = {f['downloadId']: f for f in available_files}

for file_info in scene_downloads:
    download_id = file_info.get('downloadId')
    display_id = file_info.get('displayId')

    file_entry = available_map.get(download_id)
    if file_entry and file_entry.get('url'):
        file_url = file_entry['url']
        print(f"Скачивание {display_id} по ссылке: {file_url}")
        local_path = os.path.join(download_folder, display_id)

        r = requests.get(file_url, stream=True)
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"Скачано: {local_path}")
        else:
            print(f"Ошибка скачивания файла {display_id}: HTTP {r.status_code}")
    else:
        print(f"Ссылка для скачивания не найдена для {display_id}")

print("Загрузка завершена.")
