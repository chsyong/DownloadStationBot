# DownloadStationBot
다운로드 받는 파일을 자동으로 정리하는 스크립트를 만들어 봤습니다.

사용하실 분이 있을지 모르겠지만 공유 해봅니다~

 

파이썬이라는 걸 처음 알아가며

여기저기 복사 붙여 넣기 / 예외처리 안함 / 로그 대충 생성으로 인해 많이 지저분 합니다.

그리고 다운로드 받는 소스가 TV쇼 인지 영화인지 구분할 방법을 못찾아서…

 

티프리카 RSS 등록 후 사용한다는 기준 ( 즉 다운로드 받는 URL에  tfreeca 가 존재해야 함)에서만 동작합니다.

(제가 사용하므로….)

ex) http://xxxxxxx/tfreeca/rss.php?bo_table=tdrama&k=720p-next&page=1

 

이래 저래 제약 사항도 많고 잘 동작할지도 모르겠지만 의견 주시면 반영하거나 직접 수정해 주셔도 됩니다. ㅋ

그리고 분류할 좋은 방법 있으시면 알려주세요~

 

 

파일 다운로드

http://daewoo.duckdns.org:8081/07_Share/NAS/XPEnology/DownloadStationBot.tar

파일 설명 

DownloadStationBot.sh         : 시놀 작업 관리자에 등록할 스크립트

DownloadStationBot.py         : 메인 파이썬 스크립트

DownloadStationBot.cfg        : 환경 설정 파일

Config.py                           : 설정 파일 불러오는 스크립트

DownloadStationBot-xxx.log  : 로그파일

FOLDER_LIST                       : 다운로드 받는 파일이 단일 파일이 아닌 경우를 위한 임시 저장 파일

FOLDER_LIST.tmp                 : 다운로드 받는 파일이 단일 파일이 아닌 경우를 위한 임시 저장 파일2

 

 

사용 방법

1. 파일을 적당한 경로에 압축 해제

ex) /volume1/homes/xxx/DownloadStationBot 에 DownloadStationBot.tar 을 넣었다고 가정

cd /volume1/homes/xxx/DownloadStationBot; tar xvf DownloadStationBot.tar

2. DownloadStationBot.sh 에서 python 경로 확인 ( 대부분 수정할 필요 없을 듯 )

3. DownloadStationBot.cfg  설정 파일 수정

4. 시놀로지 작업 관리자에 1분(?) 주기 실행으로 작업 등록

ex) cd /volume1/homes/xxx/DownloadStationBot;./DownloadStationBot.sh

위와 같이 해당 경로로 들어가는 cd 로 안하고 full path 주면 환경 설정 파일 못 찾습니다. ㅋ

실행 주기는 다운로드 스테이션에서 새로운 파일이 다운로드 중일때 정보를 뽑아 올 수 있을 정도의 주기로 하면 됩니다만 저 같은 경우는 드라마 한개 다운하는 데 몇분 안걸리더군요. 1분 주기로 해도 이전 스크립트가 실행중이면 새로 안도는데 다운로드 작업이 많아서 이전 스크립트 실행 시간이 길면 놓치는 파일도 생길수 있을 듯 합니다.

 

 

기능 / 동작 방식

1. 티프리카 RSS를 통해서 다운 받는 경우만 동작

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

 

 

참고 1

subliminal 설치는 2번까지만 하면됩니다. (3번은 수동으로 받을때 테스트해보시면 됩니다.)

1. subliminal  설치 파일을 다운로드 받음

git clone -b master https://github.com/Diaoul/subliminal /tmp/subliminal

2. subliminal 설치

cd /tmp/subliminal
/bin/python setup.py install  ( 파이썬은 자신의 파이선 위치, 왠만해선 환경 변수 잡혀있어서 경로는 필요 없음 )

3. 자막 다운로드

/bin/subliminal download -l ko “”/volume2/Media/”*  ( 이렇게 하면 /volume2/Media 경로 아래에 모든 파일에 대해 자막 검색 다운로드 )

근데 한글 자막 다운로드가 잘 안되는듯, 좀 더 써봐야 겠네요

 

참고 2

다운로드 스테이션 작업 정리시 오류 나서 찾아보니

force_complete=false로 해야한다함;

api 예시에는 true 되어 있던데….

( https://forum.synology.com/enu/viewtopic.php?t=116519 )

ssh에서는 os.mkdirs 같은 명령이 먹는데 시놀 작업 관리자 등록하면 동작안함 -0-;

 

참고 3

헤놀 6.1에서 혼자서만 테스트 해봤고 저도 실 사용기간 거의 없습니다;;;
