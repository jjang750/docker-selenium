# -*- coding: utf-8 -*-
# SSG 랜더스 일정/출퇴근 ETA/날씨를 텔레그램으로 전송 (실행 인자: morning | evening, 기본값 evening)
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from icalendar import Calendar
from tqdm.contrib.telegram import TelegramIO

SCHEDULE_URL = "https://www.ssglanders.com/game/schedule/data"
KAKAO_URL = "https://apis-navi.kakaomobility.com/v1/directions"

# KBO 팀 코드 → 한글 구단명
TEAM = {
    'SK': 'SSG', 'WO': '키움', 'LG': 'LG', 'SS': '삼성', 'KT': 'KT',
    'LT': '롯데', 'NC': 'NC', 'HT': 'KIA', 'HH': '한화', 'OB': '두산',
}
WEEKDAY = ['월', '화', '수', '목', '금', '토', '일']


def fetch_games():
    """당월 SSG 경기 일정 리스트 반환."""
    now = datetime.now()
    res = requests.get(SCHEDULE_URL, params={"year": now.year, "month": now.month}, timeout=20)
    res.raise_for_status()
    return res.json()


def format_game(item, today, with_date=True, mark_today=True):
    """경기 한 줄 포맷. with_date=True면 'MM/DD(요일)' 접두. mark_today=True면 오늘 경기에 ★."""
    # API 필드: date / gTime / stadium / home_key / visit_key
    date = item.get("date")
    away = TEAM.get(item.get("visit_key"), item.get("visit_key"))
    home = TEAM.get(item.get("home_key"), item.get("home_key"))
    star = ' ★' if (mark_today and date == today) else ''
    body = f'{item.get("gTime")} {item.get("stadium")}  {away} vs {home}{star}'
    if with_date:
        d = datetime.strptime(date, "%Y-%m-%d")
        return f'{d.month:02d}/{d.day:02d}({WEEKDAY[d.weekday()]}) {body}'
    return body


def commute_eta(to_work=False):
    """카카오 길찾기 ETA 한 줄. to_work=True면 집→회사(출근), False면 회사→집(퇴근). 미설정/실패 시 None."""
    key = os.getenv('KAKAO_REST_KEY')
    company = os.getenv('COMMUTE_ORIGIN')        # 회사 "경도,위도"
    home = os.getenv('COMMUTE_DESTINATION')      # 집 "경도,위도"
    if to_work:
        origin, destination, label = home, company, '🚗 출근길'
    else:
        origin, destination, label = company, home, '🚗 퇴근길'
    if not (key and origin and destination):
        return None
    try:
        res = requests.get(
            KAKAO_URL,
            params={"origin": origin, "destination": destination, "priority": "TIME"},
            headers={"Authorization": f"KakaoAK {key}"},
            timeout=20,
        )
        res.raise_for_status()
        summary = res.json()["routes"][0]["summary"]
        minutes = round(summary["duration"] / 60)
        km = round(summary["distance"] / 1000, 1)
        return f"{label} {minutes}분 ({km:g}km)"
    except Exception as e:
        print(e)
        return None


def weather_line():
    """집 좌표 기준 현재 날씨 한 줄 (wttr.in, 키 불필요). 미설정/실패 시 None."""
    home = os.getenv('COMMUTE_DESTINATION')      # "경도,위도"
    if not home:
        return None
    try:
        lng, lat = home.split(',')
        res = requests.get(
            f"https://wttr.in/{lat},{lng}",
            params={"format": "%c|%t|%f|%h"},
            headers={"User-Agent": "curl/8"},
            timeout=20,
        )
        res.raise_for_status()
        cond, temp, feels, hum = [x.strip() for x in res.text.strip().split("|")]
        temp = temp.replace("+", "")
        feels = feels.replace("+", "")
        return f"🌡️ {temp} · 체감 {feels} · 습도 {hum} {cond}"
    except Exception as e:
        print(e)
        return None


def calendar_lines():
    """개인 캘린더 오늘 일정 라인 리스트. 미설정/실패 시 None(섹션 생략), 일정 없으면 []."""
    base = os.getenv('CALENDAR_API_URL')      # 예: https://panthip.ddns.net:8301
    key = os.getenv('CALENDAR_API_KEY')
    if not (base and key):
        return None
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        res = requests.get(
            f"{base}/api/v1/events",
            params={"from": today, "to": today},
            headers={"X-API-Key": key},
            timeout=20,
        )
        res.raise_for_status()
        events = res.json()
    except Exception as e:
        print(e)
        return None
    lines = []
    for ev in events:
        title = ev.get("title") or ev.get("contents") or "(제목 없음)"
        btime = ev.get("btime")
        lines.append(f"📅 {btime} {title}" if btime else f"📅 {title}")
    return lines


def google_calendar_lines():
    """구글 캘린더(iCal) 오늘 일정 라인 리스트. 미설정/실패 시 None, 일정 없으면 []."""
    url = os.getenv('GOOGLE_ICAL_URL')
    if not url:
        return None
    try:
        res = requests.get(url, timeout=20)
        res.raise_for_status()
        cal = Calendar.from_ical(res.content)
    except Exception as e:
        print(e)
        return None
    kst = ZoneInfo("Asia/Seoul")
    today = datetime.now().date()
    rows = []
    for comp in cal.walk('VEVENT'):
        dt = comp.get('DTSTART').dt
        title = str(comp.get('SUMMARY') or "(제목 없음)")
        if isinstance(dt, datetime):
            local = dt.astimezone(kst) if dt.tzinfo else dt
            if local.date() != today:
                continue
            hhmm = local.strftime('%H:%M')
            # 00:00은 사실상 종일 일정 → 시간 생략
            rows.append((hhmm, f"🗓️ {title}" if hhmm == '00:00' else f"🗓️ {hhmm} {title}"))
        else:  # VALUE=DATE (종일)
            if dt != today:
                continue
            rows.append(('00:00', f"🗓️ {title}"))
    rows.sort()
    return [line for _, line in rows]


def send(message):
    """텔레그램 전송. 콘솔에도 출력."""
    print(message)
    try:
        token = os.getenv('TELEGRAM_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        TelegramIO(token=token, chat_id=chat_id).write(message)
    except Exception as e:
        print(e)
    print('-- end --')


def daily_message(to_work, header_emoji, kind, full_schedule=False, with_calendar=False):
    """출근/퇴근 공통 메시지 생성. to_work=True 출근(집→회사), False 퇴근(회사→집).
    full_schedule=True면 오늘 경기 대신 당월 전체 일정을 표시(매달 1일 용).
    with_calendar=True면 개인 캘린더 오늘 일정을 추가."""
    today = datetime.now().strftime('%Y-%m-%d')
    d = datetime.now()
    lines = [f'{header_emoji} {d.month}월 {d.day}일({WEEKDAY[d.weekday()]}) {kind} 정보', '']

    eta = commute_eta(to_work=to_work)
    if eta:
        lines.append(eta)

    weather = weather_line()
    if weather:
        lines.append(weather)

    if with_calendar:
        personal = calendar_lines()
        google = google_calendar_lines()
        if personal is not None or google is not None:
            events = (personal or []) + (google or [])
            lines += events if events else ['📅 오늘 일정 없음']

    games = fetch_games()
    if full_schedule:
        lines += [f'⚾ {format_game(g, today, with_date=True)}' for g in games]
    else:
        todays = [g for g in games if g.get("date") == today]
        if todays:
            lines += [f'⚾ {format_game(g, today, with_date=False, mark_today=False)}' for g in todays]
        else:
            lines.append('⚾ 오늘 경기 없음')

    send("\n".join(lines))


def morning():
    """주중 06:10: 출근(집→회사) ETA + 날씨 + 오늘 일정(캘린더) + 오늘 경기."""
    daily_message(to_work=True, header_emoji='☀️', kind='출근', with_calendar=True)


def evening():
    """매일 17시: 퇴근(회사→집) ETA + 날씨 + 오늘 경기. 매달 1일엔 당월 전체 일정."""
    is_first_day = datetime.now().day == 1
    daily_message(to_work=False, header_emoji='🌙', kind='퇴근', full_schedule=is_first_day)


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'evening'
    if mode == 'morning':
        morning()
    else:
        evening()
