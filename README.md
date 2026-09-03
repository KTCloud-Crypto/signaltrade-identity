# SignalTrade Identity

사용자 계정과 인증을 담당하는 서비스입니다. 로그인한 사용자의 프로필, 실행 모드, Upbit API Key, Telegram 연결 상태를 한곳에서 관리합니다.

## 주요 책임

- 회원가입, 로그인, Access Token 발급
- 비밀번호 변경과 Telegram 기반 재설정
- 사용자 프로필과 모의·실전 실행 설정
- Upbit Access/Secret Key 암호화 보관
- Telegram 계정 연결 코드 발급·해제
- 로그인 실패 제한과 보안 감사 기록

## 디렉터리

```text
src/signaltrade_identity/
  api_auth.py        인증과 사용자 API
  dependencies.py    Token 검증과 현재 사용자 조회
  security.py        비밀번호·JWT·암호화 처리
  upbit_adapter.py   Upbit 계정 확인 보조 코드
  telegram_link.py   Telegram 연결 코드 처리
tests/               API·보안·Telegram 연결 테스트
```

## 다른 서비스와 통신

Frontend는 `/auth`, `/users` API로 로그인과 설정을 처리합니다. Trading은 실전 주문 직전에 내부 API로 해당 사용자의 복호화된 거래소 키를 조회합니다. Notification은 Telegram 연결 상태를 확인할 수 있습니다.

내부 요청은 `X-SignalTrade-Service-Token`으로 보호합니다. 반환된 거래소 키는 주문 처리 메모리에서만 사용하며 DB나 로그에 다시 저장하지 않습니다.

## 로컬 확인

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/pytest
.venv/bin/uvicorn signaltrade_identity.main:app --host 0.0.0.0 --port 8000
```

kind 전체 환경에서는 Core가 만든 PostgreSQL·Redis와 Kubernetes Secret을 사용합니다.
