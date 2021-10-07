# ap-madang-server
우리 동네 앞마당 서버

당근마켓 MVP 인턴십 Jinny


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
* secrets.json 파일을 생성해서 DB 정보 작성

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

## 배포

1. 새로 추가한 라이브러리가 있는 경우
```
pip3 freeze > requirements.txt
```

2. `develop` -> `main` 으로 PR & merge

3. EC2에 소스코드 업로드 
```
git pull
```

4. 서버 재시작
```
sudo systemctl restart gunicorn nginx
```

## 로그 확인

```
cat /var/log/nginx/access.log
```

```
cat /var/log/nginx/error.log
```

## gunicon / nignx 설정 변경시

```
sudo ln -sf /etc/nginx/sites-available/ap-madang.conf /etc/nginx/sites-enabled/ap-madang.conf
```

```
sudo systemctl daemon-reload
```

```
sudo systemctl restart gunicorn nginx
```