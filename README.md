# ap-madang-server
랜던 동네 모임 서버
![image](https://user-images.githubusercontent.com/57395765/137661835-504cf61f-530d-4772-97d1-f47ac7792078.png)


## 환경 세팅

1. 레포지토리를 클론합니다
```
git clone https://github.com/karrotmvp/ap-madang-server.git
```

2. 가상환경을 생성/활성화 합니다
```
python3 -m venv venv
```
```
source venv/bin/activate
```

3. 라이브러리 다운
```
pip3 install -r requirements.txt
```

4. DB 연결
* .env 파일을 생성해서 DB 정보 작성

```
python3 manage.py makemigrations
```

```
python3 manage.py migrate
```

5. 서버 가동
```
python3 manage.py runserver
```

6. 접속

[개발 문서 접속](http://127.0.0.1:8000/swagger/)
[어드민 접속](http://127.0.0.1:8000/admin)


## PR 시 주의사항

* develop branch에 PR 날리기
* 새로 추가한 라이브러리가 있는 경우
```
pip3 freeze > requirements.txt
```
* 마이그레이션 파일 확인

## 테스트 배포
1. 모델링을 변경한 경우, 로컬에서 dev db 연결 후에
```
python3 manage.py migrate
```

2. 추가한 환경 변수가 있는 경우 -> 배포 후에 AWS 에서 등록

3. `feature` -> `develop` 으로 PR & merge

4. github actions log 확인

5. 배포 후 QA 진행


## 프로덕션 배포

1. 모델링을 변경한 경우, 로컬에서 production db 연결 후
```
python3 manage.py migrate
```

2. 추가한 환경 변수가 있는 경우 -> 수동배포!

3. `develop` -> `main` 으로 PR & merge

4. github actions log 확인

## 크론잡 배포
1. 크론잡을 추가한 경우에 CRON_JOBS에 추가

2. 모델링을 변경한 경우, 로컬에서 production db 연결 후
```
python3 manage.py migrate
```

3. EC2에 SSH 접속 후 소스코드 업로드
```
git pull origin main
```

4. cron job 제거
```
python3 manage.py crontab remove
```

5. cron job 등록
```
python3 manage.py crontab add
```

6. cron job 조회
```
python3 manage.py crontab show
```

7. 서버 재시작
```
sudo systemctl restart gunicorn nginx
```

8. 리눅스 cronjob 스케줄 확인
```
sudo crontab -l
```

9. 로그 확인
```
sudo tail -20 /var/log/cron
```