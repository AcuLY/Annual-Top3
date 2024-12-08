import httpx
import json
from datetime import datetime
import time

params = {
    'user_id': '0',
    'subject_type': 2,
    'position': '',
    'collection_types': [2, 3, 4, 5],
    'tags': ['2024']
}

# 设置最大重试次数
MAX_RETRIES = 3
# 设置超时时间（秒）
TIMEOUT = 10

response = httpx.post('https://search.bgmss.fun/statistics', json=params)

data = response.json()['all_subjects']

full_list = []

def fetch_data_with_retry(url, headers, retries=MAX_RETRIES):
    """带重试机制的 GET 请求"""
    for attempt in range(retries):
        try:
            # 使用 timeout 设置请求超时时间
            sresponse = httpx.get(url, headers=headers, timeout=TIMEOUT)
            sresponse.raise_for_status()  # 如果响应错误（例如 4xx 或 5xx），会抛出异常
            return sresponse
        except httpx.RequestError as e:
            print(f"请求错误: {e}")
        except httpx.HTTPStatusError as e:
            print(f"HTTP 错误: {e}")
        except httpx.TimeoutException as e:
            print(f"超时错误: {e}")
        
        # 如果发生错误或超时，等待一定时间后重试
        if attempt < retries - 1:
            print(f"等待 {2 ** attempt} 秒后重试...")
            time.sleep(2 ** attempt)  # 采用指数退避策略
    return None  # 如果重试完还是失败，返回 None

for s in data:
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
    date = datetime.strptime(d['date'], '%Y-%m-%d') if 'date' in d.keys() and d['date'] else datetime(2025, 1, 1)
    
    full_list.append({
        'id': s['id'],
        'name': s['name_cn'],
        'image': img,
        'date': date
    })
    
    print(full_list[-1])

# 按照日期排序
full_list_sorted = sorted(full_list, key=lambda s: s['date'])

# 保存数据到 JSON 文件
with open('full_list.json', mode='w', encoding='utf-8') as f:
    json.dump(full_list_sorted, f, ensure_ascii=False, indent=4)
