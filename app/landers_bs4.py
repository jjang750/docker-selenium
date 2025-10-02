# -*- coding: utf-8 -*-
import requests
import os
from datetime import datetime


yyyy = int('20'+datetime.now().strftime('%y'))
mm = int(datetime.now().strftime('%m'))
dd = datetime.now().strftime('%d')

url = "https://www.ssglanders.com/game/schedule/data"
params = {
    "year": 2025,
    "month": 9
}

message = f'Landers {yyyy}-{mm}-{dd}\n'

res = requests.get(url, params=params)
res.raise_for_status()
data = res.json()
print(data)

# JSON 구조 확인 후 원하는 필드 출력
for item in data:   # 실제 키 이름 확인 필요
    game_date = item.get("date")
    home_team = item.get("home_key")
    away_team = item.get("visit_key")
    stadium = item.get("stadium")
    gTime = item.get("gTime")
    message += f"{game_date}:{gTime} {away_team} VS {home_team}\n"
    print(f"{game_date}:{gTime} {away_team} VS {home_team} : {stadium}")
