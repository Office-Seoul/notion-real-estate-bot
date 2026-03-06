import sys
import requests
import json
import os

page_id, keyword = sys.argv[1], sys.argv[2]
headers = {"Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}

# Vworld 검색
url = f"https://api.vworld.kr/req/address?service=address&request=search&version=2.0&format=json&type=ROAD&key={os.getenv('VWORLD_KEY')}&query={keyword}"
resp = requests.get(url).json()

if resp['response']['status'] == 'OK':
    elements = resp['response']['result']['elements']
    road_addr = elements[0]['address']['road'] if elements else ""
    
    payload = {"properties": {"도로명주소": {"rich_text": [{"text": {"content": road_addr}}]}}}
    requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json=payload)
    print(f"✅ {road_addr}")
else:
    print("❌ 검색실패")
