# DownloadStationBot
시놀로지 다운로드 스테이션으로 통해 
다운로드 받는 파일을 자동으로 정리하는 스크립트를 만들어 봤습니다.
사용하실 분이 있을지 모르겠지만 공유 해봅니다~
<br/><br/>
파이썬이라는 걸 처음 알아가며
여기저기 복사 붙여 넣기 / 예외처리 안함 / 로그 대충 생성으로 인해 많이 지저분 합니다.
그리고 다운로드 받는 소스가 TV쇼 인지 영화인지 구분할 방법을 못찾아서…
<br/><br/>
 
<h3>파일 설명 </h3>

setup.sh                      : 초기 설치파일

DownloadStationBot.sh         : 시놀 작업 관리자에 등록할 스크립트

DownloadStationBot.py         : 메인 파이썬 스크립트

DownloadStationBot.cfg        : 환경 설정 파일

Config.py                     : 설정 파일 불러오는 스크립트

DownloadStationBot-xxx.log    : 로그파일

FOLDER_LIST                   : 다운로드 받는 파일이 단일 파일이 아닌 경우를 위한 임시 저장 파일

FOLDER_LIST.tmp               : 다운로드 받는 파일이 단일 파일이 아닌 경우를 위한 임시 저장 파일2

bash                          : shell script 실행 bash

 
<br/><br/>
<h2>사전 조건</h2>

1. 시놀로지 package 센터에서 아래 패키지 설치
git server
python 2
python module
 

<br/><br/>
<h2>사용 방법</h2>

1. 시놀로지에 ssh 접속 후 DownloadStationBot 다운 받을 경로로 이동후 아래 명령으로 다운로드

git clone git://github.com/chsyong/DownloadStationBot  

2. DownloadStationBot 폴더 아래 파일 중 setup.sh 실행하여 필요한 유틸들 다운로드 및 설치 진행

cd DownloadStationBot
./setup.sh

3. DownloadStationBot.cfg  설정 파일 자신의 시놀로지 정보와 다운로드 후 옮겨지 디렉토리 지정
(영화,드라마,예능 등 큰 카테고리의 폴더를 지정해주고 미리 폴더가 생성되어 있어야 함)

4. 시놀로지 작업 관리자에 1분(?) 주기 실행으로 작업 등록

ex) cd /volume1/homes/xxx/DownloadStationBot;./DownloadStationBot.sh

위와 같이 해당 경로로 들어가는 cd 로 안하고 full path 주면 환경 설정 파일 못 찾습니다. ㅋ

실행 주기는 다운로드 스테이션에서 새로운 파일이 다운로드 중일때 정보를 뽑아 올 수 있을 정도의 주기로 하면 됩니다만 저 같은 경우는 드라마 한개 다운하는 데 몇분 안걸리더군요. 1분 주기로 해도 이전 스크립트가 실행중이면 새로 안도는데 다운로드 작업이 많아서 이전 스크립트 실행 시간이 길면 놓치는 파일도 생길수 있을 듯 합니다.

 

 

<h2>기능 / 동작 방식</h2>


2. 애니는 RSS 다운로드가 안되서 테스트 못하고 예능, 드라마, 영화 만 동작할 듯 합니다.

3. 드라마/예능의 경우

다운로드가 시작되면 제목 분석 시도해서 단일 파일에 신규면 환결 설정 경로 아래에 폴더를 생성

다운로드가 완료되면 단일 파일의 경우 이미 만들어 놓은 폴더로 이동, 폴더 형식이면 통째로 이동

4. 영화의 경우

다운로드가 시작되면 단일 파일이면 확장자만 뺀 이름으로 폴더 설정 파일 기준으로 영화 경로 아래 폴더 생성

다운로드가 완료되면 단일 파일의 경우 이미 만들어 놓은 폴더로 이동, 폴더 형식이면 통째로 이동

영화인 경우 subliminal 모듈을 사용해서 자막 파일 받기 시도 함

5. 이동 후 다운로드 스테이션의 작업 정리

6. 사용자가 다운로드 스테이션 기본 폴더가 아닌 특정 폴더로 지정했을 경우 패스

 

 
