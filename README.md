# landers-schedule

SSG 랜더스 경기 일정·출퇴근 ETA·날씨를 텔레그램으로 1회 전송하는 단발성 프로그램.
실행 인자로 모드를 구분하며, 매일 전송은 **호스트 스케줄러(Windows 작업 스케줄러 / cron)** 가 `docker run` 명령을 호출하는 방식으로 동작한다.

## 실행 모드

실행 인자로 `morning` / `evening` 을 지정한다. 인자가 없으면 `evening`.

| 모드 | 시점(예시) | 전송 내용 |
|------|-----------|-----------|
| `morning` | 주중 06:10 | 출근(집→회사) ETA + 날씨 + 오늘 일정(캘린더) + 오늘 경기 |
| `evening` | 매일 17:00 | 퇴근(회사→집) ETA + 날씨 + 오늘 경기 (매달 1일은 당월 전체 일정) |

- ETA는 카카오모빌리티 길찾기(실행 시점 실시간 교통 기준).
- 날씨는 `wttr.in`(키 불필요)으로 집 좌표 기준 현재 날씨를 조회한다.
- 오늘 일정은 개인 캘린더 API(`/api/v1/events`)에서 조회하며, 아침 모드에만 표시된다.

## 환경변수

| 변수 | 필수 | 설명 |
|------|------|------|
| `TELEGRAM_TOKEN` | ✅ | 텔레그램 봇 토큰 |
| `TELEGRAM_CHAT_ID` | ✅ | 수신 chat id |
| `TZ` | 권장 | `Asia/Seoul` |
| `KAKAO_REST_KEY` | 선택 | 카카오 REST API 키. 키+좌표 2개가 모두 있어야 ETA가 붙음 |
| `COMMUTE_ORIGIN` | 선택 | 회사 좌표 `경도,위도` |
| `COMMUTE_DESTINATION` | 선택 | 집 좌표 `경도,위도`. 날씨 조회 기준 좌표로도 쓰임 |
| `CALENDAR_API_URL` | 선택 | 개인 캘린더 API 베이스 URL (예: `https://host:8301`). 아침 모드 일정용(📅) |
| `CALENDAR_API_KEY` | 선택 | 캘린더 API의 `X-API-Key` 값 |
| `GOOGLE_ICAL_URL` | 선택 | 구글 캘린더 "iCal 형식의 비공개 주소"(`.../basic.ics`). 아침 모드 일정용(🗓️) |

> 각 항목은 관련 환경변수가 없으면 해당 줄만 생략된다(전송 자체는 정상). 개인 캘린더는 URL+키가 둘 다, 구글 캘린더는 iCal URL이 있어야 일정 줄이 붙는다.
> 구글 iCal은 반복 일정(RRULE) 확장은 지원하지 않으며, 00:00(KST) 시작 일정은 종일 일정으로 간주해 시간 표기를 생략한다.

## 이미지 빌드

빌드 컨텍스트는 `app/` 폴더다.

```bash
docker build -t landers-cron:latest ./app
```

## 환경 설정

프로젝트 루트에 `.env` 파일을 두고 위 환경변수 표의 값을 채운다(`.env` 는 .gitignore 처리되어 커밋되지 않음).
`--env-file` 값에는 따옴표·인라인 주석을 쓰지 않는다. 주석은 `#` 로 시작하는 별도 줄만 허용된다.

## 실행

`--rm` 으로 1회 실행 후 컨테이너는 자동 종료된다. 마지막 인자(`morning`/`evening`)로 모드를 지정한다.

```bash
docker run --rm --env-file .env landers-cron:latest morning
docker run --rm --env-file .env landers-cron:latest evening
```

## 자동 실행 (호스트 스케줄러)

같은 이미지를 시점만 다르게 2번 등록한다. (`.env` 는 절대경로 권장)

### Linux cron

```cron
10 6 * * 1-5  docker run --rm --env-file /path/to/.env landers-cron:latest morning
0 17 * * *    docker run --rm --env-file /path/to/.env landers-cron:latest evening
```

### Windows / NAS 작업 스케줄러

- 아침: 매주 월–금 06:10 → `docker run --rm --env-file /path/to/.env landers-cron:latest morning`
- 저녁: 매일 17:00 → `docker run --rm --env-file /path/to/.env landers-cron:latest evening`

## 로컬 실행 (도커 없이)

Docker 이미지(`python:3.12-slim`)와 동일하게 Python 3.12 기준이다.

```bash
py -3.12 -m venv venv             # Linux/macOS: python3.12 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r app/requirements.txt
TELEGRAM_TOKEN=xxx TELEGRAM_CHAT_ID=xxx python app/main.py
```

## 참고

- 컨테이너는 Chrome/Selenium 을 사용하지 않는다. SSG 공식 JSON API(`/game/schedule/data`)를 `requests` 로 직접 호출한다.
- 외부 연동 3곳으로의 아웃바운드가 필요하다 — `api.telegram.org`(전송), `apis-navi.kakaomobility.com`(ETA), `wttr.in`(날씨). 막혀 있으면 해당 줄만 실패하거나 전송이 안 된다.
