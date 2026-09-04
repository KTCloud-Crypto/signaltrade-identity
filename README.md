# SignalTrade Identity

사용자 계정과 인증 정보를 책임지는 서비스입니다. 로그인한 사용자가 누구인지 확인하고, 실전투자에 필요한 Upbit API Key와 알림에 필요한 Telegram 연결 정보를 안전하게 관리합니다.

## 주요 역할

- 회원가입, 로그인과 Access Token 발급
- 비밀번호 변경과 Telegram 기반 비밀번호 재설정
- 사용자 프로필과 모의·실전 실행 모드 관리
- Upbit Access Key와 Secret Key 암호화 저장
- Upbit 계정 연결 여부와 Key 유효성 확인
- Telegram 연결 코드 발급, 연결과 해제
- 로그인 실패 제한과 보안 관련 감사 기록

거래소 Secret Key는 암호화한 상태로 DB에 저장합니다. 복호화된 값은 권한이 있는 내부 서비스에만 전달하며 응답이나 로그에 불필요하게 노출하지 않습니다.

## Write 권한이 있는 테이블

- `user`: 계정, 비밀번호, 프로필과 실행 설정
- `api_key`: 암호화된 Upbit API Key와 연결 상태
- `security_audit_log`: 로그인 실패 등 보안 사건 기록
- `message_outbox`: 비동기로 전달할 Identity 이벤트

다른 도메인의 전략, 거래, 포지션 테이블에는 쓰지 않습니다.

## HTTP 통신

Frontend는 공개 API를 통해 로그인과 사용자 설정을 처리합니다. 서비스 간 내부 API는 별도의 Service Token으로 보호합니다.

- Trading: 실전 주문 직전에 사용자의 Upbit Key 요청
- Portfolio: 실제 잔고 조회에 필요한 Upbit Key 요청
- Notification: Telegram 사용자 연결 정보 요청
- Strategy 등 다른 서비스: 필요한 최소 사용자 정보 확인

## Redis와 Queue

Redis에는 영구 보관할 사용자 원본 데이터가 아니라, 일정 시간이 지나면 사라져야 하는 상태를 저장합니다. 예를 들면 요청 횟수 제한, 로그인 보안 상태, Telegram 연결 코드 같은 정보입니다.

비동기 전달이 필요한 이벤트는 업무 변경과 같은 DB transaction 안에서 `message_outbox`에 기록합니다. Messaging이 이를 읽어 알맞은 Queue로 전송합니다. Identity는 Queue를 직접 소비하지 않습니다.
