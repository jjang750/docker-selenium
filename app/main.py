# -*- coding: utf-8 -*-
import os
from datetime import datetime

import requests
from tqdm.contrib.telegram import TelegramIO


def landers():
    yyyy = int('20' + datetime.now().strftime('%y'))
    mm = int(datetime.now().strftime('%m'))
    dd = datetime.now().strftime('%d')

    message = f'Landers {yyyy}-{mm}-{dd}\n'

    url = "https://www.ssglanders.com/game/schedule/data"
    params = {
        "year": yyyy,
        "month": mm
    }

    res = requests.get(url, params=params)
    res.raise_for_status()
    data = res.json()
    print(data)

    # JSON 구조 확인 후 원하는 필드 출력
    for item in data:  # 실제 키 이름 확인 필요
        game_date = item.get("date")
        home_team = item.get("home_key")
        away_team = item.get("visit_key")
        stadium = item.get("stadium")
        gTime = item.get("gTime")
        if f"{yyyy}-{mm}-{dd}" == game_date:
            message += f"{game_date}:{gTime} {stadium} {away_team} VS {home_team} ★ \n"
        else:
            message += f"{game_date}:{gTime} {stadium} {away_team} VS {home_team}\n"

        print(f"{game_date}:{gTime} {away_team} VS {home_team} : {stadium}")

    try:
        token = os.getenv('TELEGRAM_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')

        telegram = TelegramIO(token=token, chat_id=chat_id)
        telegram.write(message)
    except Exception as e:
        print(e)
    print('-- end --')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    landers()