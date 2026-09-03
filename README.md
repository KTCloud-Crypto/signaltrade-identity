# SignalTrade Identity

사용자 인증, 프로필, Upbit 키 암호화 보관, Telegram 연결을 맡는 서비스입니다.

```text
src/signaltrade_identity/  API·인증·보안 코드
tests/                     서비스 테스트
```

Frontend는 인증·사용자 API를 호출합니다. Trading과 Notification은 내부 HTTP와 서비스 토큰으로 필요한 사용자 정보나 거래소 키를 조회합니다. 키는 응답 처리 뒤 저장하거나 로그에 남기지 않습니다.
