#!/usr/bin/env python3
import sys
import requests
import json
import os

try:
    full_input = sys.argv[1]
    keyword = sys.argv[2] if len(sys.argv) > 2 else "강남구 역삼동"
    
    # URL에서 페이지 ID만 추출
    page_id = full_input.split('/')[-1].split('?')[0].split('-')[-1]
    if len(page_id) != 32:
        page_id = full_input.split('/')[-1].replace('-', '')[:32]
    
    print(f"📍 검색어: {keyword}")
    print(f"📄 추출된 페이지ID: {page_id}")
    
    # Vworld API 호출 (오류 안전 처리)
    vworld_key = os.getenv('VWORLD_KEY')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    url = f"https://api.vworld.kr/req/address?service=address&request=search&version=2.0&format=json&type=ROAD&key={vworld_key}&query={keyword}"
    
    print(f"🌐 API 호출: {url}")
    resp = requests.get(url, headers=headers, timeout=10)
    
    print(f"📡 상태코드: {resp.status_code}")
    print(f"📡 응답 길이: {len(resp.text)}")
    
    if resp.status_code != 200:
        print(f"❌ HTTP 오류: {resp.status_code}")
        sys.exit(1)
    
    if not resp.text.strip():
        print("❌ 빈 응답")
        sys.exit(1)
    
    try:
        data = resp.json()
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 실패: {resp.text[:200]}")
        sys.exit(1)
    
    print(f"📡 응답 상태: {data.get('response', {}).get('status', 'UNKNOWN')}")
    
    if data.get('response', {}).get('status') == 'OK':
        elements = data['response']['result'].get('elements', [])
        if elements:
            addr = elements[0]['address']
            road_addr = addr.get('road', '')
            lotno_addr = addr.get('lotnoAddr', '')
            
            headers_notion = {
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
            
            notion_resp = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers_notion, json=payload)
            
            if notion_resp.status_code == 200:
                print(f"✅ 도로명주소: {road_addr}")
                print(f"✅ 지번주소: {lotno_addr}")
                print("🎉 노션 업데이트 성공!")
            else:
                print(f"❌ 노션 오류 {notion_resp.status_code}: {notion_resp.text}")
        else:
            print("❌ 검색 결과 없음")
    else:
        print(f"❌ Vworld API 오류: {data}")
        
except Exception as e:
    print(f"💥 오류: {str(e)}")
    sys.exit(1)
