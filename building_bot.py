#!/usr/bin/env python3
import sys
import requests
import os
import json
import re

try:
    # 입력값에서 페이지 ID 추출 (URL이든 직접 입력이든)
    full_input = sys.argv[1]
    page_id = re.search(r'[a-zA-Z0-9]{32}', full_input)
    if page_id:
        page_id = page_id.group()
    else:
        page_id = full_input.strip()
    
    print(f"📄 페이지ID: {page_id}")
    
    if len(page_id)
