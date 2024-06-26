# 치직

<p>
    <a href="https://github.com/junah201/chzzk-discord-bot/graphs/contributors">
        <img alt="GitHub Contributors" src="https://img.shields.io/github/contributors/junah201/chzzk-discord-bot" />
    </a>
    <a href="https://github.com/junah201/chzzk-discord-bot/issues">
        <img alt="Issues" src="https://img.shields.io/github/issues/junah201/chzzk-discord-bot?color=0088ff" />
    </a>
    <a href="https://github.com/junah201/chzzk-discord-bot/pulls">
        <img alt="GitHub pull requests" src="https://img.shields.io/github/issues-pr/junah201/chzzk-discord-bot?color=0088ff" />
    </a>
</p>

치지직 방송 알림을 디스코드로 받아보세요!

## 사용법

1. 사용하실 서버에 디스코드 봇을 [이 링크](https://api.chzzk.junah.dev/invite)를 눌러 추가해주세요.
2. 알림을 받고 싶으신 치치직 채널의 링크에서 ID를 복사해주세요. `https://chzzk.naver.com/live/bb382c2c0cc9fa7c86ab3b037fb5799c` 다음과 같은 링크에서 `bb382c2c0cc9fa7c86ab3b037fb5799c` 이 부분이 ID 입니다.
3. [치직 봇 대시보드](https://chzzk.junah.dev)에 접속하여, 대시보드 버튼을 눌러주세요.
4. 알림을 추가하고 싶은 서버를 클릭해주세요.
5. 이후 치지직 ID, 디스코드 채널, 커스텀 메시지 등을 입력하여 알림을 추가해주세요.
6. 커스텀 메시지 수정, 테스트 알림 전송, 알림 삭제 등의 모든 기능을 대시보드에서 조작 가능합니다.

※ 알림은 방송이 켜진 후 최대 5분 이내로 전송됩니다.

## 기술 스택

위 프로젝트는 서버리스인 AWS Lambda와 NoSQL인 DynamoDB를 사용하고 있습니다. 또한 DynamoDB를 제외한 모든 인프라는 Serverless framework 통해 관리하고 있습니다.

```
📦
 ┣ 📂 frontend : 치직 봇 대시보드 사이트의 코드입니다.
 ┣ 📂 lambdas
 ┃ ┣ 📂 event_handler : 알림추가와 알림삭제 등 슬래시명령어 및 버튼에 관한 코드
 ┃ ┗ 📂 link_check : 5분 마다 방송을 켰는지 확인하는 lambda 코드입니다.
 ┃ ┗ 📂 naver_session_renew : 12시간 마다 네이버 세션을 갱신하는 코드입니다.
 ┣ 📂 shared : lambda에서 공유하는 코드입니다.
 ┗ 📜 serverless.yml : AWS 인프라 설정에 관련된 serverless framework 코드입니다. DynamoDB를 제외한 모든 V2 인프라가 정의되어 있습니다.
```
