import sys
import requests
import os
import re

page_id = sys.argv[1]
headers = {"Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}", "Notion-Version": "2022-06-28"}

# 주소 추출
resp = requests.get(f"https://api.notion.com/v1/pages/{page_id}", headers=headers).json()
props = resp['properties']
address = (props.get("지번주소", {}).get("rich_text", [{}])[0].get("plain_text", "") or
           props.get("도로명주소", {}).get("rich_text", [{}])[0].get("plain_text", ""))

print(f"📍 주소: {address}")

if not address:
    print("❌ 주소 없음")
    sys.exit(1)

# 서울시 API
api_key = os.getenv('SEOUL_API_KEY')
url = f"https://api.seoul.go.kr:8080/openapi/buildingInfo?serviceKey={api_key}&address={address}"
resp = requests.get(url).json()

if resp.get('resultCode') == '00' and resp.get('buildingInfo'):
    building = resp['buildingInfo'][0]
    
    payload = {
        "properties": {
            "건물명": {"title": [{"text": {"content": building.get('bldNm', 'N/A')}}]},
            "용도": {"rich_text": [{"text": {"content": building.get('mainPurpsNm', 'N/A')}}]},
            "연면적": {"number": float(building.get('totArea', 0))},
            "지상층수": {"number": int(building.get('totDongCnt', 0))},
            "사용승인일": {"date": {"start": building.get('prposYear', '')}},
            "업데이트": {"date": {"start": "2026-03-06"}}
        }
    }
    
    requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json=payload)
    print("🎉 건축물대장 입력 완료!")
else:
    print("❌ API 조회 실패")
