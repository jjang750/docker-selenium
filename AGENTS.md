# AGENTS.md — landers-schedule

SSG 랜더스 경기 일정·출퇴근 ETA·날씨를 텔레그램으로 1회 전송하는 단발성 Docker 작업.

## 역할
- 매일 호스트 스케줄러(Windows 작업 스케줄러 / cron)가 `docker run` 호출.
- 모드 인자에 따라 다른 내용 전송:
  - `morning` (주중 06:10): 출근 ETA + 날씨 + 오늘 일정 + 오늘 경기
  - `evening` (매일 17:00, 기본값): 퇴근 ETA + 날씨 + 오늘 경기 (매달 1일은 당월 전체 일정)

## 데이터 출처
- **ETA**: 카카오모빌리티 길찾기 (실시간 교통)
- **날씨**: `wttr.in` (집 좌표 기준, 키 불필요)
- **일정**: 개인 캘린더 API `/api/v1/events` (아침 모드 한정)
- **경기**: SSG 랜더스 경기 일정 크롤링

## 기술 스택
- Python (FastAPI 아닌 스크립트)
- Docker (단일 컨테이너, `docker run --rm`)
- 외부 API: 카카오모빌리티, wttr.in, 사내 캘린더 API, 텔레그램

## 구조
```
app/
  main.py               # 메인 스크립트 (mode 인자 처리)
  requirements.txt
  Dockerfile
venv/
README.md
```

## 환경변수
| 변수 | 필수 | 설명 |
|------|------|------|
| `TELEGRAM_TOKEN` | ✅ | 텔레그램 봇 토큰 |
| `TELEGRAM_CHAT_ID` | ✅ | 수신 chat id |
| `TZ` | 권장 | `Asia/Seoul` |

## 실행
```
docker build -t landers-schedule ./app
docker run --rm \
  -e TELEGRAM_TOKEN=... -e TELEGRAM_CHAT_ID=... -e TZ=Asia/Seoul \
  landers-schedule:latest morning
```

## 주의
- `mcp-crawl-landers-schedule` 와 동일 데이터 소스. 둘 다 유지할지 통합할지 검토.
- 사내 캘린더 API 엔드포인트 변경 시 즉시 깨짐. 헬스체크 알림 추가 권장.
- 일회성 실행이므로 컨테이너에 상태 저장 금지.
