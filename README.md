# ap-madang-server
랜던 동네 모임 서버

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

## 프로덕션 배포

1. 새로 추가한 라이브러리가 있는 경우
```
pip3 freeze > requirements.txt
```

2. 모델링을 변경한 경우( 로컬, 테스트, 프로덕션 모두 )
```
python3 manage.py migrate
```

3. `develop` -> `main` 으로 PR & merge

4. github actions log 확인
