# 프로젝트 소개
게시판을 만들어보면서 FastAPI를 배우기 위해 시작하게되었습니다.
독학으로 책과 블로그들을 보면서 제작한 프로젝트입니다.

# 기술스택
FastAPI, Python, Redis(세션 저장용), Docker, PostgreSQL

# 프로젝트 기능
* 유저 - 유저 로그인시 Access Token을 반환 및 Redis를 이용한 Access Token Blacklist 관리 (탈취 위험 방지)
* 게시판 - CRUD 기능(권한 관리 및 접근제어), 페이징, 
* 게시글 - CRUD 기능(접근제어), 페이징
* 댓글 - CRUD (접근제어)

# DB 설계

# API 설계
* To be done

# 실행방법

1. Local 환경에있는 도커를 실행후 docker-compose up -d 실행합니다. 
2. source venv/bin/activate
3. uvicorn main:app --reload
4. http://127.0.0.1:8000/docs 에서 기능 확인가능합니다.
