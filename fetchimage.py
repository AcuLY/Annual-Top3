import httpx
import json
from datetime import datetime
import time


subjects_without_image = []

start_time = datetime(2024, 1, 1)
end_time = datetime(2024, 12, 31)

with open('../BangumiStaffStats/backend/jsonlines/subject.jsonlines', mode='r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        sid = data['id']
        stype = data['type']
        
        if not stype == 2:
            continue
        
        name_cn = data['name_cn'] if data['name_cn'] else data['name']
        
        favorite = sum(data['favorite'].values())
        if favorite < 50:
            continue
        
        nsfw = data['nsfw']
        if nsfw:
            continue
        
        if not 'date' in data.keys() or not data['date']:
            continue
        date = datetime.strptime(data['date'], '%Y-%m-%d')
        if not start_time < date < end_time:
            continue
        
        subjects_without_image.append({
            'id': sid,
            'name': name_cn,
            'date': date
        })

subjects_without_image = sorted(subjects_without_image, key=lambda s: s['date'])

full_list = []

def fetch_data_with_retry(url, headers, retries=3):
    for attempt in range(retries):
        try:
            sresponse = httpx.get(url, headers=headers, timeout=10)
            sresponse.raise_for_status()  
            return sresponse
        except httpx.RequestError as e:
            print(f"请求错误: {e}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP 错误: {e}")
        except httpx.TimeoutException as e:
            print(f"超时错误: {e}")
        
        if attempt < retries - 1:
            print(f"等待 {2 ** attempt} 秒后重试...")
            time.sleep(2 ** attempt)  
    return None 

for s in subjects_without_image:
    url = f'https://api.bgm.tv/v0/subjects/{s["id"]}'
    headers = {
        'User-Agent': 'AcuL/BangumiStaffStatistics/1.0 (Web) (https://github.com/AcuLY/BangumiStaffStats)'
    }

    sresponse = fetch_data_with_retry(url, headers)

    if sresponse is None:
        print(f"获取 {s['id']} 数据失败，跳过该条数据")
        continue
    
    d = sresponse.json()
    
    img = d['images']['common'] if 'images' in d.keys() else 'https://lain.bgm.tv/img/no_icon_subject.png'
    
    full_list.append({
        'id': s['id'],
        'name': s['name'],
        'image': img,
    })
    
    print(full_list[-1])

# 保存数据到 JSON 文件
with open('full_list.json', mode='w', encoding='utf-8') as f:
    json.dump(full_list, f, ensure_ascii=False, indent=4)
