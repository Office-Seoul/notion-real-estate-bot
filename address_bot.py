#!/usr/bin/env python3
import sys
import requests
import os
import re

try:
    # 페이지 ID 추출 (URL에서 32자리만)
    full_input = sys.argv[1]
    page_id_match = re.search(r'[a-zA-Z0-9]{32}', full_input)
    page_id = page_id_match.group() if page_id_match else full_input.strip()
    
    print(f"📄 페이지ID: {page_id}")
    print("🧪 테스트 모드: '연관지번' 속성에 '테스트' 입력")
    
    # 노션 API 헤더
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    # 간단 테스트: "연관지번" 속성에 "테스트" 입력
    payload = {
        "properties": {
            "연관지번": {
                "rich_text": [{
                    "text": {
                        "content": "테스트"
                    }
                }]
            }
        }
    }
    
    print(f"📤 노션 업데이트 요청: {page_id}")
    response = requests.patch(f"https://api.notion.com/v1/pages/{page_id}", 
                             headers=headers, 
                             json=payload)
    
    print(f"📡 응답 상태코드: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ '연관지번'에 '테스트' 입력 성공!")
    else:
        print(f"❌ 실패: {response.status_code}")
        print(f"응답 내용: {response.text[:200]}")
        
except Exception as e:
    print(f"💥 오류: {str(e)}")
    sys.exit(1)
