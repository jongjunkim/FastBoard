# 프로젝트 소개
게시판을 만들어보면서 FastAPI를 배우기 위해 시작하게되었습니다.
독학으로 책과 블로그들을 보면서 제작한 프로젝트입니다.

# 기술스택
FastAPI, Python, Redis(Access Token 저장용), Docker(PostreSQL Redis 관리), PostgreSQL

# 프로젝트 기능
* 유저 - 유저 로그인시 Access Token을 반환 및 Redis를 이용한 Access Token Blacklist 관리 (탈취 위험 방지)
* 게시판 - CRUD 기능(권한 관리 및 접근제어), 페이징, 
* 게시글 - CRUD 기능(접근제어), 페이징
* 댓글 - CRUD (접근제어)

# DB 설계
![image](https://github.com/jongjunkim/FastBoard/blob/master/image/ER%20diagram.PNG)
# API 설계
## 게시판
![image](https://github.com/jongjunkim/FastBoard/blob/master/image/%EA%B2%8C%EC%8B%9C%ED%8C%90.PNG)

## 게시물
![image](https://github.com/jongjunkim/FastBoard/blob/master/image/%EA%B2%8C%EC%8B%9C%EB%AC%BC.PNG)

## 댓글
![image](https://github.com/jongjunkim/FastBoard/blob/master/image/%EB%8C%93%EA%B8%80.PNG)

## 유저
![image](https://github.com/jongjunkim/FastBoard/blob/master/image/%EC%9C%A0%EC%A0%80.PNG )

# API 명세

## 유저

* signup: fullname, email, password1, password2 를 입력받습니다.
* login: login을 했을때 jwt에 기반한 access token을 반환합니다. access token은 쿠키에 저장이 됩니다. 
* logout: access token을 Redis를 이용해서 Blacklist로 저장하여 탈취위험을 막습니다.

## 게시판
* create: 게시판 이름과 public을 받습니다. public은 모든 유저에게 공개되는 True와 생성자에게만 보여지는 False가 있습니다.
* update: 게시판의 이름과 public을 수정할수있습니다. 생성자만 수정이 가능합니다.
* Delete: board_id를 입력 받아 게시판을 삭제합니다. 생성자만 삭제가 가능합니다.
* Get: board_id를 입력받아서 게시판에 속해있는 모든 게시물들을 보여줍니다.
* list: 게시판 목록을 조회합니다. 현재 로그인한 유저가 본인이 생성한 게시판과 모든 유저들에게 공개된 게시판의 리스트를 페이지별로 볼 수 있습니다. 게시글 개수 순서대로 보여집니다.

## 게시물
* create: board_id, 제목, 내용을 입력받아 게시물을 작성합니다. 본인이 생성한 게시판이나 모든 유저들에게 공개된 게시판에만 작성이 가능합니다
* update: 게시물의 제목과 내용을 입력받아 게시물을 수정합니다. 본인의 게시물만 수정이 가능합니다
* Delete: 게시물을 삭제합니다. 본인의 게시물만 삭제가 가능합니다.
* Get: post_id를 입력값으로 받아 post의 정보와 post에 속해있는 댓글들을 보여줍니다.
* List:  board_id를 입력받아 게시판에 속해있는 게시물 목록을 조회합니다. 본인이 접근할수있는 게시판만 조회가 가능합니다.

## 댓글
* create: post_id를 입력받아 댓글을 작성합니다.
* update: 댓글을 수정합니다. 본인의 댓글만 수정이 가능합니다.
* delete: 댓글을 삭제합니다. 본인의 댓글만 삭제가 가능합니다.
* get: 댓글을 조회합니다. 

# 실행방법

1. Local 환경에있는 도커를 실행후 docker-compose up -d 실행합니다. 
2. source venv/bin/activate
3. uvicorn main:app --reload
4. http://127.0.0.1:8000/docs 에서 기능 확인가능합니다.

# 프로젝트를 마치며

## 후기
FastAPI를 공부하면서 혼자 계획해서 만든 프로젝트이기 때문에, 혼자 힘으로 RestAPI를 구현했다는 뿌듯함과 더불어 아쉬움이 많이 남습니다.

많이 막혔던 부분을 꼽아보자면 맨처음 동기 구현을 하고 나서 비동기 구현으로 바꾸면서 함수앞에 async붙이고 모든 함수를 부를때 await을 붙이면 작동될줄 알았지만 비동기로 했을경우에는 로직 부분에서 수정해야할 부분이 많아 시행착오를 많이 겪었습니다

덕분에 디버깅을 하고 수정하면서 많이 배우게 됬습니다. 앞으로 제가 무엇을 더 공부해야할지 스스로 인지 하게 되었고, 벡엔드 지식에 대해 흥미를 많이 가지게 될 수 있었습니다. 
