#!/usr/bin/env python3
import sys
import requests
import os
import json

try:
    page_id = sys.argv[1]
    print(f"📄 페이지ID: {page_id}")
    
    # 노션 페이지 정보 조회
    headers = {"Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}", "Notion-Version": "2022-06-28"}
    resp = requests.get(f"https://api.notion.com/v1/pages/{page_id}", headers=headers)
    data = resp.json()
    
    props = data.get('properties', {})
    road_addr = props.get("도로명주소", {}).get("rich_text", [{}])[0].get("plain_text", "")
    lotno_addr = props.get("지번주소", {}).get("rich_text", [{}])[0].get("plain_text", "")
    
    address = road_addr or lotno_addr
    print(f"📍 주소: {address}")
    
    if not address:
        print("❌ 주소 정보가 없습니다. 먼저 주소검색을 실행하세요.")
        sys.exit(1)
    
    # 서울시 건축물대장 API
    api_key = os.getenv('SEOUL_API_KEY')
    url = f"https://api.seoul.go.kr:8080/openapi/buildingInfo?serviceKey={api_key}&address={address}"
    
    print(f"🌐 API 호출: {url}")
    resp = requests.get(url, timeout=10)
    data = resp.json()
    
    print(f"📡 응답 코드: {data.get('resultCode')}")
    
    if data.get('resultCode') == '00' and data.get('buildingInfo'):
        building = data['buildingInfo'][0]
        
        payload = {
            "properties": {
                "건물명": {"title": [{"text": {"content": building.get('bldNm', 'N/A')}}]},
                "용도": {"rich_text": [{"text": {"content": building.get('mainPurpsNm', 'N/A')}}]},
                "연면적": {"number": float(building.get('totArea', 0))},
                "지상층수": {"number": int(building.get('totDongCnt', 0))},
                "사용승인일": {"date": {"start": building.get('prposYear')}},
                "업데이트": {"date": {"start": "2026-03-06"}}
            }
        }
        
        notion_resp = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", headers=headers, json=payload)
        
        if notion_resp.status_code == 200:
            print("🎉 건축물대장 정보 입력 완료!")
            print(f"🏢 건물명: {building.get('bldNm', 'N/A')}")
        else:
            print(f"❌ 노션 업데이트 실패: {notion_resp.status_code}")
            print(f"응답: {notion_resp.text}")
    else:
        print(f"❌ 건축물대장 API 실패: {data.get('resultMsg', '알 수 없는 오류')}")
        
except Exception as e:
    print(f"💥 오류 발생: {str(e)}")
    sys.exit(1)
