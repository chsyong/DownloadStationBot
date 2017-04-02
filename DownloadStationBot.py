#-*- coding: utf-8 -*-

import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
import json
import re
import Config
import os
import subprocess
import datetime
import shutil
import logging
import logging.handlers
import urllib
import psutil
import BeautifulSoup
import traceback
from datetime import datetime

global IP           
global PORT         
global ACCOUNT
global PASSWORD
global SESSION
global DEFAULT_URL  
global INFO_API
global AUTH_API
global TASK_API
global FILE_API
global CONFIG
global log

CONFIG = Config.Config(sys.argv[1])
IP          = CONFIG.GetIP()
PORT        = CONFIG.GetPort()
ACCOUNT     = CONFIG.GetAccount()
PASSWORD    = CONFIG.GetPassword()

DEFAULT_URL = "http://" + IP + ":" + PORT + "/webapi/"
INFO_API="SYNO.API.Info"
AUTH_API="SYNO.API.Auth"
TASK_API="SYNO.DownloadStation.Task"
FILE_API="SYNO.FileStation.CopyMove"

today_date = datetime.today().strftime('%Y%m%d')
log = logging.getLogger('LOGGER.')

def create_directory(PATH, REAL_TITLE) :
    FLAG = 1
    directory_list = [
        d for d in (os.path.join(PATH, d1) for d1 in os.listdir(PATH))
        if os.path.isdir(d)
    ]
    for d in directory_list :
        if d.find(REAL_TITLE) != -1 :
            FLAG=FLAG+1
            log.info("(create) : already exists folder : " + PATH + REAL_TITLE)
    if FLAG == 1 :
        os.popen("mkdir \"" + PATH + REAL_TITLE + "\"")
        log.info("------------------------------------------------------------------------------------------------------------------")
        log.info("(create) : CREATED DIR : " + PATH + REAL_TITLE)
        log.info("------------------------------------------------------------------------------------------------------------------")

def move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2) :
    log.info("(move) : search path :  " + TO_PATH)
    log.info("(move) : search folder :  " + REAL_TITLE)
    log.info("(move) : source folder :  " + DOWNLOAD_PATH)
    directory_list = [
        d for d in (os.path.join(TO_PATH, d1) for d1 in os.listdir(TO_PATH))
        if os.path.isdir(d)
    ]
    FLAG = 1
    for d in directory_list :
        if d.find(REAL_TITLE) != -1 :
            FLAG = FLAG + 1
            log.info("(move) : target folder :  " + d)
            log.info("(move) : STARTING  MOVE, FROM : " + DOWNLOAD_PATH + TITLE + " TO : " + d + "/" + TITLE)
            result = os.popen("mv \"" + DOWNLOAD_PATH + TITLE + "\" \"" + d + "/" + TITLE +"\"")

            log.info("------------------------------------------------------------------------------------------------------------------")
            log.info("(move) : FINISHED MOVE, FROM : " + DOWNLOAD_PATH + TITLE + " TO : " + d + "/" + TITLE)
            log.info("------------------------------------------------------------------------------------------------------------------")
            os.popen("synoindex -A \"" + TO_PATH  + "\"")
    if FLAG == 1 :
        log.info("(move) : not found target folder : " + REAL_TITLE)
    return str(FLAG)

def move_folder(DOWNLOAD_PATH, PATH, TITLE) :
    log.info("(move folder) : source folder :  " + DOWNLOAD_PATH)
    log.info("(move folder) : target path :  " + PATH)
    log.info("(move folder) : STARTING MOVE, FROM : " + DOWNLOAD_PATH + " TO : " + PATH )
    os.popen("mv \"" + DOWNLOAD_PATH + TITLE + "\" \"" + PATH + TITLE + "\"")
    log.info("------------------------------------------------------------------------------------------------------------------")
    log.info("(move folder) : FINISHED MOVE, FROM : " + DOWNLOAD_PATH + TITLE +" TO : " + PATH + TITLE)
    log.info("------------------------------------------------------------------------------------------------------------------")
    os.popen("synoindex -A \"" + PATH + "\"")

def find_category_title_path(TITLE, TASK, URI) :
    log.info("(" +TASK + ") : searching category and real title" )
    CATEGORY = ""
    REAL_TITLE = ""
    TO_PATH=""

    if TITLE.find("Raws") != -1 and TITLE.find(" - ") != -1 :
        TEMP = TITLE.find(" - ")
        REAL_TITLE = TITLE[0:TEMP]
    elif TITLE.find(".E") != -1 :
        TEMP=TITLE.find(".E")
        CHECK_STRING=TITLE[TEMP+2:TEMP+4]
        try :
            int(CHECK_STRING);
            REAL_TITLE=TITLE[0:TEMP]
        except :
            REAL_TITLE = os.path.splitext(TITLE)[0]
    else :
        REAL_TITLE = os.path.splitext(TITLE)[0]
    log.info("(" + TASK + ") : real title is " + REAL_TITLE)
     
    # 다운 소스가 tfreeca 인 경우 
    if URI.find("/tfreeca/") != -1 :
        CATEGORY=re.search('b_id=(.*?)&id=', URI)
        CATEGORY=CATEGORY.group(1)
    # tfreeca 아닌 경우  tfreeca 검색 시도
    else :
      boardList = ['torrent_tv', 'torrent_movie', 'torrent_variety', 'torrent_docu', 'torrent_mid', 'torrent_ani']
      for board in boardList:
          response = requests.get("https://torrentkim10.net/bbs/s.php?k=" + REAL_TITLE + "&b=" + board + "&q=")
          sp = BeautifulSoup.BeautifulSoup(response.text)
          bList = sp.find('div', attrs={'id':'blist'})
          if bList == None:
              log.info("(" + TASK + ") :  category not found in torkim " + board + " 1")
          else :
              torTRs = bList.findAll('td', attrs={'class':'subject'})
              if len(torTRs) > 0 :
                  log.info("(" + TASK + ") : category found in torkim " + board)
                  CATEGORY = board
                  break
              else :
                  log.info("(" + TASK + ") :  category not found in torkim " + board + " 2")

      if CATEGORY == 'torrent_tv' :
          CATEGORY = 'tdrama'
      elif CATEGORY == 'torrent_movie' :
          CATEGORY = 'tmovie'
      elif CATEGORY == 'torrent_variety' :
          CATEGORY = 'tent'
      elif CATEGORY == 'torrent_ani' :
          CATEGORY = 'tani'

      if(len(CATEGORY) == 0) :
          boardList = ['tv', 'tmovie', 'tent', 'tani']
          for board in boardList:
              response = requests.get("http://www.tfreeca22.com/board.php?b_id=" + board + "&mode=list&sc=" + REAL_TITLE + "&x=0&y=0")
              data = response.text.encode('ISO-8859-1')
              sp = BeautifulSoup.BeautifulSoup(data)
              bList = sp.find('table', attrs={'class':'b_list'})
              if bList == None:
                  log.info("(" + TASK + ") :  category not found in tfreeca " + board + " 1")
              else :
                  torTRs = bList.findAll('td', attrs={'class':'subject'})
              if len(torTRs) > 0 :
                  log.info("(" + TASK + ") : category found in tfreeca " + board)
                  CATEGORY = board 
                  break
              else :
                  log.info("(" + TASK + ") :  category not found in tfreeca " + board + " 2")

    log.info("(" + TASK + ") : category : " + CATEGORY)

    if CATEGORY == 'tdrama' :
        TO_PATH=CONFIG.GetTdramaPath() + "/"
    elif CATEGORY == 'tent' :
        TO_PATH=CONFIG.GetTentPath() + "/"
    elif CATEGORY == 'tv' :
        TO_PATH=CONFIG.GetTvPath() + "/"
    elif CATEGORY =='tmovie' :
        TO_PATH = CONFIG.GetTmoviePath() + "/"
    elif CATEGORY == 'tani' :
        TO_PATH = CONFIG.GetTaniPath() + "/"

    return CATEGORY, REAL_TITLE, TO_PATH

def main() :
    # LOG Setting
    log.setLevel(logging.INFO)
    formatter = logging.Formatter('[ %(levelname)-10s | %(filename)s: %(lineno)s\t\t] %(asctime)s > %(message)s')
    fileHandler = logging.FileHandler('./DownloadStationBot-'+str(today_date)+'.log')
    streamHandler = logging.StreamHandler()
    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)
    log.addHandler(fileHandler)
    log.addHandler(streamHandler)

    # GET Download Station Info
    log.info("******************************************************************************************************************")
    log.info("START")
    req=requests.Session()
    log.debug("Request DS INFO : " + DEFAULT_URL + "query.cgi?api=" + INFO_API + "&version=1&method=query&query=" + AUTH_API + "," + TASK_API + "," + FILE_API)
    response = req.get(DEFAULT_URL + "query.cgi?api=" + INFO_API + "&version=1&method=query&query=" + AUTH_API + "," + TASK_API ) 
    log.debug("Response DS INFO : " + response.text)
    data = response.json()
    AUTH_PATH=data['data'][AUTH_API]['path']
    AUTH_VERSION=data['data'][AUTH_API]['maxVersion']
    TASK_PATH=data['data'][TASK_API]['path']
    TASK_VERSION=data['data'][TASK_API]['maxVersion']


    req2=requests.Session()
    log.debug("Request DS INFO : " + DEFAULT_URL + "query.cgi?api=" + INFO_API + "&version=1&method=query&query=" + AUTH_API + "," + FILE_API)
    response = req2.get(DEFAULT_URL + "query.cgi?api=" + INFO_API + "&version=1&method=query&query=" + AUTH_API + "," + FILE_API) 
    data = response.json()
    log.debug("Response DS INFO : " + response.text)
    FILE_PATH=data['data'][FILE_API]['path']
    FILE_VERSION=data['data'][FILE_API]['maxVersion']


    # Login
    log.info("LOGIN")
    log.debug("Request Login : " + DEFAULT_URL + AUTH_PATH + "?api=" + AUTH_API + "&version=" + str(AUTH_VERSION) + "&method=login&account=" + ACCOUNT + "&passwd=" + PASSWORD + "&session=DownloadStation&format=cookie")
    response = req.get(DEFAULT_URL + AUTH_PATH + "?api=" + AUTH_API + "&version=" + str(AUTH_VERSION) + "&method=login&account=" + ACCOUNT + "&passwd=" + PASSWORD + "&session=DownloadStation&format=cookie")
    log.debug("Response Login : " + response.text)

    log.debug("Request Login : " + DEFAULT_URL + AUTH_PATH + "?api=" + AUTH_API + "&version=" + str(AUTH_VERSION) + "&method=login&account=" + ACCOUNT + "&passwd=" + PASSWORD + "&session=FileStation&format=cookie")
    response = req2.get(DEFAULT_URL + AUTH_PATH + "?api=" + AUTH_API + "&version=" + str(AUTH_VERSION) + "&method=login&account=" + ACCOUNT + "&passwd=" + PASSWORD + "&session=FileStation&format=cookie")
    log.debug("Response Login : " + response.text)

    # Get DS Task List
    log.debug("Request Task List : " + DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=list")
    response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=list")
    log.debug("Response Task List : " + response.text)
    data = response.json()
    tasks=data['data']['tasks']


    # 작업 있는지 확인
    if len(tasks) > 0 :
        log.info("Download Task Exist")

        for task in tasks:
            TASK_ID=task['id']
            log.debug("Request Detail : " + DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=getinfo&id=" + TASK_ID + "&additional=detail,transfer,file")
            response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=getinfo&id=" + TASK_ID + "&additional=detail,transfer,file")
            log.debug("Response Detail : " + response.text)
            data = response.json()
            URI=data['data']['tasks'][0]['additional']['detail']['uri']
            TITLE=data['data']['tasks'][0]['title']
            STATUS=data['data']['tasks'][0]['status']
            log.info("--------" + TITLE  + "---------")
            log.info("starting check it")
            log.info("status : " + STATUS)

            # 다중 파일의 경우 다운로드 할때 체크하여 임시 파일에 저장
            if STATUS.find("downloading") != -1 and TITLE.find(".php") == -1 : 
              log.info("(downloading) : downloading file check")
              FILES_COUNT=data['data']['tasks'][0]['additional']['file']
              log.info("(downloading) : " + str(len(FILES_COUNT)) +  " files")

              f = open("FOLDER_LIST", 'r')
              for line in f :
                  if TITLE in line :
                      log.info("(downloading) : already exists in temp file for fast")
              f.close()

              # 모든 복수 파일
              if len(FILES_COUNT) != 1 :
                CATEGORY, REAL_TITLE, TO_PATH = find_category_title_path(TITLE, "downloading", URI)
                log.info("(downloading) : multiple file check start")
                if len(CATEGORY) > 0 :
                  FLAG = 1
                  f = open("FOLDER_LIST", 'r')
                  for line in f :
                      if CATEGORY + "\t" + TITLE in line :
                          log.info("(downloading) : already registered in temp file")
                          FLAG = FLAG + 1
                  f.close()
                  if FLAG == 1 :
                      f = open("FOLDER_LIST", 'a')
                      data = CATEGORY + "\t" + TITLE + "\n"
                      f.write(data)
                      f.close()
                      log.info("(downloading) : new saved in temp file for folder move")
                else :
                  log.info("(downloading) : failed to register folder because not found category" )



            # 다운 완료 된 파일 이동 처리
            elif STATUS.find("finished") != -1 :
              log.info("(finished) : finished file check")
              DESTINATION_PATH=data['data']['tasks'][0]['additional']['detail']['destination']
              DOWNLOAD_PATH=CONFIG.GetDownloadPath() + "/"
              # 사용자 지정 폴더 없고 
              if DOWNLOAD_PATH.find(DESTINATION_PATH) != -1 :
                log.info("(finished) : downloaded to default path ")

                CATEGORY, REAL_TITLE, TO_PATH = find_category_title_path(TITLE, "move", URI)

                # 복수 파일 다운로드 시 이동 처리 시작
                log.info("(move) : (multiple) file check start")
                infile = file('FOLDER_LIST')
                tempfile = open('FOLDER_LIST.tmp', 'w')
                FLAG=1
                for line in infile :
                    if CATEGORY + "\t" + TITLE not in line :
                        tempfile.write(line)
                    else :
                        move_folder(DOWNLOAD_PATH, TO_PATH, TITLE)
                        FLAG=FLAG+1
                        if CATEGORY == 'tmovie' or CATEGORY == 'tani' :
                            log.info("(move) : (multiple) subtitle downloading to " + DOWNLOAD_PATH + TITLE)
                            os.system("/bin/subliminal download -l ko \"" + DOWNLOAD_PATH + TITLE + "\"* >> ./DownloadStationBot-" + str(today_date) + ".log")
                            log.info("(move) : (multiple) subtitle downloaded to " + DOWNLOAD_PATH + TITLE)
                infile.close()
                tempfile.close()
                os.popen("cp -p  FOLDER_LIST.tmp  FOLDER_LIST ")
                log.info("(move) : multiple file check finished")
                # 복수 파일 처리 종료

                # FLAG가 1인 경우(즉 복수 파일에서 처리되지 못한것은) 단일 파일로  처리
                if len(CATEGORY) > 0  and FLAG == 1 :

                    log.info("(move) : single file check start")

                    create_directory(TO_PATH, REAL_TITLE)

                    RESULT = move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)

                    if int(RESULT) == 2:
                      FLAG=FLAG+1

                    if int(RESULT) == 2 and (CATEGORY == 'tani' or CATEGORY == 'tmovie') :
                        log.info("(move) : (single) subtitle downloading to " + TO_PATH + REAL_TITLE )
                        os.system("/bin/subliminal download -l ko \"" + TO_PATH + REAL_TITLE + "\"* >> ./DownloadStationBot-" + str(today_date) + ".log")
                        log.info("(move) : (single) subtitle downloaded to " + TO_PATH + REAL_TITLE )
                    log.info("(move) : single file check finished")

                # 여전히 못찾은 경우 
                if FLAG == 1 :
                  if TITLE.find(".E") != -1 :
                    log.info("(move) : single tv show : search in exists folder")
                    # TV show의 경우 기존 폴더 있는지 검색한번 해봄
                    TEMP=TITLE.find(".E")
                    CHECK_STRING=TITLE[TEMP+2:TEMP+4]
                    log.info("(move) : TV " + CHECK_STRING + " episode validated")
                    try :
                      int(CHECK_STRING);
                      REAL_TITLE=TITLE[0:TEMP]
                      DOWNLOAD_PATH=CONFIG.GetDownloadPath() + "/"
                      TO_PATH=CONFIG.GetTdramaPath() + "/"
                      RESULT = move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                      if int(RESULT) == 1 :
                          TO_PATH=CONFIG.GetTentPath() + "/"
                          RESULT = move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                          if int(RESULT) == 1 :
                              TO_PATH=CONFIG.GetTvPath() + "/"
                              RESULT = move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                              if int(RESULT) != 1 :
                                  FLAG = FLAG + 1
                                  log.info("(move) :  single, not from tfreeca, found already exist folder")
                          else :
                              FLAG = FLAG +1
                              log.info("(move) :  single, not from tfreeca, found already exist folder")
                      else :
                          FLAG = FLAG + 1
                          log.info("(move) :  single, not from tfreeca, found already exist folder")
                    except :
                        log.info("(move) : is not tv show or failed")
                    log.info("(move) : single tv show : search in exists folder finished")
                  # TV show 아닌경우 자막 다운로드 시도
                  else :
                    DOWNLOAD_PATH=CONFIG.GetDownloadPath() + "/"
                    log.info("(just sub) : subtitle downloading to " + DOWNLOAD_PATH + TITLE)
                    os.system("/bin/subliminal download -l ko \"" + DOWNLOAD_PATH + TITLE + "\"* >> ./DownloadStationBot-" + str(today_date) + ".log")
                    log.info("(just sub) : subtitle downloading to " + DOWNLOAD_PATH + TITLE)

                #  log.info("(move) : single not downloaded in tfreeca but search in tfreea " )
                #  req3=requests.Session()
                #  boardList = ['tdrama', 'tent', 'tv', 'tmovie']
                #  keyword = TITLE

                if FLAG != 1 : 
                  TASK_ID=task['id']
                  response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=delete&id=" + TASK_ID + "&force_complete=false")


              # 사용자 폴더 지정 다운로드 작업
              else :
                  log.info(": user definition path, finished download")
                  if TITLE.find(".E") == -1 :
                    DOWNLOAD_PATH=CONFIG.GetDownloadPath() + "/"
                    log.info("(just sub) : (user) subtitle downloading to " + DOWNLOAD_PATH + TITLE)
                    os.system("/bin/subliminal download -l ko \"" + DOWNLOAD_PATH + TITLE + "\"* >> ./DownloadStationBot-" + str(today_date) + ".log")
                    log.info("(just sub) : (user) subtitle downloading to " + DOWNLOAD_PATH + TITLE)
                  TASK_ID=task['id']
                  response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=delete&id=" + TASK_ID + "&force_complete=false")
                  log.info(": user definition path, finished download and remove task in download station")

            elif  STATUS.find("paused") != -1 :
                log.info(": status paused")
                boardList = ['torrent_tv', 'torrent_movie', 'torrent_variety', 'torrent_docu', 'torrent_mid', 'torrent_ani']
                REAL_TITLE = ""
                if TITLE.find("Raws") != -1 and TITLE.find(" - ") != -1 :
                    TEMP = TITLE.find(" - ")
                    REAL_TITLE = TITLE[0:TEMP]
                for board in boardList:
                    response = requests.get("https://torrentkim10.net/bbs/s.php?k=" + REAL_TITLE + "&b=" + board + "&q=")
                    sp = BeautifulSoup.BeautifulSoup(response.text)
                    bList = sp.find('div', attrs={'id':'blist'})
                    if bList == None:
                        log.info("(move) :  category not found in " + board + " 1")
                    else :
                        torTRs = bList.findAll('td', attrs={'class':'subject'})
                        if len(torTRs) > 0 :
                            log.info("(move) : category found in " + board)
                            CATEGORY = board 
                            break
                        else :
                            log.info("(move) :  category not found in " + board + " 2")

    LOG_FILE = os.popen("find . -type f -name 'DownloadStationBot-*.log' -mtime +0").read()
    for logfile in LOG_FILE.splitlines() :
        os.remove(logfile)
        log.info("remove logfile : " + logfile )
       

    response = req.get(DEFAULT_URL + AUTH_PATH + "?api=" + AUTH_API + "&version=" + str(AUTH_VERSION) + "&method=logout&session=DownloadStation")
    log.info("LOGOUT ")
    log.info("******************************************************************************************************************")

if __name__ == "__main__": 
    main()
