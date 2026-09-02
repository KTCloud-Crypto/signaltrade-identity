# signaltrade-identity

SignalTrade의 사용자 인증, 프로필, 거래소 API 키, Telegram 연결 및 보안 감사를
소유하는 독립 서비스입니다.

## 개발

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/pytest
```

## 실행

```sh
.venv/bin/uvicorn signaltrade_identity.main:app --host 0.0.0.0 --port 8000
```

기준 코드는 `KTCloud-Crypto`의 `feat/132`, 커밋
`013107ae8ddd08bed02d88db89af7eeb0cf65bba`입니다. 기준 모노레포는 수정하지
않습니다.

