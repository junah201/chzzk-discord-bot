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

1. 사용하실 서버에 디스코드 봇을 [이 링크](https://discord.com/api/oauth2/authorize?client_id=1191657232480350238&permissions=137439464512&scope=bot+applications.commands)를 눌러 추가해주세요.
2. 알림을 받고 싶으신 치치직 채널의 링크에서 ID를 복사해주세요. \`https://chzzk.naver.com/live/bb382c2c0cc9fa7c86ab3b037fb5799c` 다음과 같은 링크에서 `bb382c2c0cc9fa7c86ab3b037fb5799c` 이 부분이 ID 입니다.
4. `/알림추가` 명령어에 치지직 채널의 ID와 알림을 받고 싶은 디스코드 채널을 선택해서 입력해주시면, 방송이 켜질 경우 해당 채널에 알림이 전송됩니다.

※ 알림은 방송이 켜진 후 최대 5분 이내로 전송됩니다.

## 기술 스택

위 프로젝트는 서버리스인 AWS Lambda와 NoSQL인 DynamoDB를 사용하고 있습니다. 또한 API GateWay를 제외한 모든 인프라는 Terraform을 통해 관리하고 있습니다.
```
📦
 ┣ 📂 .github : lambda와 layer의 CI/CD 코드입니다.
 ┣ 📂 lambdas
 ┃ ┣ 📂 event_handler : 알림추가와 알림삭제 등 슬래시명령어 및 버튼에 관한 코드
 ┃ ┗ 📂 link_check : 방송을 켰는지 확인하는 lambda 코드입니다. 5분에 한번 씩 실행되도록 cron job이 설정되어 있습니다.
 ┣ 📂 layers : lambda에서 사용될 layer에 대한 코드입니다.
 ┗ 📂 terrafrom : AWS 인프라 설정에 관련된 terraform 코드입니다.
```
