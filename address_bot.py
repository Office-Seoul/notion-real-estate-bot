#!/usr/bin/env python3
import sys
import requests
import json
import os

try:
    page_id = sys.argv[1]
    keyword = sys.argv[2] if len(sys.argv) > 2 else "강남구 역삼동"
    
    print(f"📍 검색어: {keyword}")
    print(f"📄 페이지ID: {page_id}")
    
    # Vworld API 호출
    vworld_key = os.getenv('VWORLD_KEY')
    url = f"https://api.vworld.kr/req/address?service=address&request=search&version=2.0&format=json&type=ROAD&key={vworld_key}&query={keyword}"
    
    print(f"🌐 API 호출: {url}")
    resp = requests.get(url, timeout=10)
    data = resp.json()
    
    print(f"📡 응답 상태: {data.get('response', {}).get('status', 'UNKNOWN')}")
    
    if data.get('response', {}).get('status') == 'OK':
        elements = data['response']['result']['elements']
        if elements:
            road_addr = elements[0]['address']['road']
            lotno_addr = elements[0].get('address', {}).get('lotnoAddr', '')
            
            headers = {
                "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json"
            }
            
            payload = {
                "properties": {
                    "도로명주소": {"rich_text": [{"text": {"content": road_addr}}]},
                    "지번주소": {"rich_text": [{"text": {"content": lotno_addr}}]}
                }
            }
            
            notion_resp = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json=payload)
            
            if notion_resp.status_code == 200:
                print(f"✅ 도로명주소: {road_addr}")
                print(f"✅ 지번주소: {lotno_addr}")
                print("🎉 노션 업데이트 성공!")
            else:
                print(f"❌ 노션 업데이트 실패: {notion_resp.status_code}")
                print(f"응답: {notion_resp.text}")
        else:
            print("❌ 검색 결과 없음")
    else:
        print(f"❌ Vworld API 오류: {data}")
        
except Exception as e:
    print(f"💥 오류 발생: {str(e)}")
    sys.exit(1)
