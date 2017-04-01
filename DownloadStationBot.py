#-*- coding: utf-8 -*-

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
            log.info(REAL_TITLE + " Task (create) : already exists : " + PATH + REAL_TITLE)
    if FLAG == 1 :
        os.popen("mkdir \"" + PATH + REAL_TITLE + "\"")
        log.info("------------------------------------------------------------------------------------------------------------------")
        log.info(REAL_TITLE + " Task (create) : CREATED DIR : " + PATH + REAL_TITLE)
        log.info("------------------------------------------------------------------------------------------------------------------")

def move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2) :
    log.info(TITLE + " Task (move file) : search path :  " + TO_PATH)
    log.info(TITLE + " Task (move file) : search folder :  " + REAL_TITLE)
    log.info(TITLE + " Task (move file) : source folder :  " + DOWNLOAD_PATH)
    directory_list = [
        d for d in (os.path.join(TO_PATH, d1) for d1 in os.listdir(TO_PATH))
        if os.path.isdir(d)
    ]
    FLAG = 1
    for d in directory_list :
        if d.find(REAL_TITLE) != -1 :
            FLAG = FLAG + 1
            log.info(TITLE + " Task (move file) : target folder :  " + d)
            log.info(TITLE + " Task (move file) : STARTING  FROM : " + DOWNLOAD_PATH + TITLE + " TO : " + d + "/" + TITLE)
            result = os.popen("mv \"" + DOWNLOAD_PATH + TITLE + "\" \"" + d + "/" + TITLE +"\"")

            #SOURCE = DOWNLOAD_PATH + TITLE
            #TEMP = SOURCE.split("/",2)
            #TEMP2 = TEMP[1].lstrip("volume")
            #int(TEMP2)
            #SOURCE = "/" + TEMP[2]
            #SOURCE = "/homes/a.mp4"
            #EnS = urllib.quote(SOURCE.encode('utf-8'), '/:')

            #TARGET = d + "/" + TITLE
            #TEMP = TARGET.split("/",2)
            #TEMP2 = TEMP[1].lstrip("volume")
            #int(TEMP2)
            #TARGET = "/" + TEMP[2]
            #TARGET = "/homes/b.mp4"
            #EnT = urllib.quote(TARGET.encode('utf-8'), '/:')

            #log.info("EnS : " + EnS)
            #log.info("EnT : " + EnT)
            #response = req2.get(DEFAULT_URL + "entry.cgi?api=" + FILE_API + "&version=" + str(FILE_VERSION) + "&method=start&path=" + EnS + "&dest_folder_path=" + EnT ) 
            #response = req2.get(DEFAULT_URL + "entry.cgi?api=" + FILE_API + "&version=" + str(FILE_VERSION) + "&method=start&path=\"" + DOWNLOAD_PATH + TITLE  + "\"&dest_folder_path=\"" +  d + "/" + TITLE +"\"") 
            #response = req2.get(DEFAULT_URL + "entry.cgi?api=" + FILE_API + "&version=" + str(FILE_VERSION) + "&method=start&path="+EnS+"&dest_folder_path="+EnT+"&remove_src=true") 
            #print response.text
            log.info("------------------------------------------------------------------------------------------------------------------")
            log.info(TITLE + " Task (move file) : FINISHED  FROM : " + DOWNLOAD_PATH + TITLE + " TO : " + d + "/" + TITLE)
            log.info("------------------------------------------------------------------------------------------------------------------")
            os.popen("synoindex -A \"" + TO_PATH  + "\"")
    if FLAG == 1 :
        log.info(TITLE + " Task (move file) : not found target folder : " + REAL_TITLE)
    return str(FLAG)

def move_folder(DOWNLOAD_PATH, PATH, TITLE) :
    log.info(TITLE + " Task (move folder) : source folder :  " + DOWNLOAD_PATH)
    log.info(TITLE + " Task (move folder) : target path :  " + PATH)
    log.info(TITLE + " Task (move folder) : STARTING FROM : " + DOWNLOAD_PATH + " TO : " + PATH )
    os.popen("mv \"" + DOWNLOAD_PATH + TITLE + "\" \"" + PATH + TITLE + "\"")
    log.info("------------------------------------------------------------------------------------------------------------------")
    log.info(TITLE + " Task (move folder) : FINISHED FROM : " + DOWNLOAD_PATH + " TO : " + PATH )
    log.info("------------------------------------------------------------------------------------------------------------------")
    os.popen("synoindex -A \"" + PATH + "\"")

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


    # 다운로드 작업 있는지 확인
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
            log.info(TITLE + " Task : starting check it")
            log.info(TITLE + " Task : status : " + STATUS)

            # 다운로드 작업에 대해서는 폴더 생성
            if STATUS.find("downloading") != -1 and TITLE.find(".php") == -1 : 
              log.info(TITLE + " Task (create) : downloading file check")
              FILES_COUNT=data['data']['tasks'][0]['additional']['file']
              log.info(TITLE + " Task (create) : " + str(len(FILES_COUNT)) +  " files")

              log.info(TITLE + " Task (create) : searching category" )
              f = open("FOLDER_LIST", 'r')
              for line in f :
                  if TITLE in line :
                      log.info(TITLE +" Task (create) : already exists in temp file for fast")
              f.close()

              CATEGORY = ""
              # 다운 소스가 tfreeca 인 경우 
              if URI.find("/tfreeca/") != -1 :
                  CATEGORY=re.search('b_id=(.*?)&id=', URI)
                  CATEGORY=CATEGORY.group(1)
              # tfreeca 아닌 경우  tfreeca 검색 시도
              else :
                log.info(TITLE + " Task (create) : searching category in tfreea " )
                req3=requests.Session()
                boardList = ['tdrama', 'tent', 'tv', 'tmovie']
                REAL_TITLE = ""
                if TITLE.find(".E") != 1 :
                    TEMP=TITLE.find(".E")
                    CHECK_STRING=TITLE[TEMP+2:TEMP+4]
                    try :
                        int(CHECK_STRING);
                        REAL_TITLE=TITLE[0:TEMP]
                    except :
                        REAL_TITLE = os.path.splitext(TITLE)[0]
                else :
                    REAL_TITLE = os.path.splitext(TITLE)[0]
                log.info(REAL_TITLE)

                for board in boardList:
                    response = req3.get("http://www.tfreeca22.com/board.php?b_id=" + board + "&mode=list&sc=" + REAL_TITLE + "&x=0&y=0")
                    data = response.text.encode('ISO-8859-1')
                    sp = BeautifulSoup.BeautifulSoup(data)
                    bList = sp.find('table', attrs={'class':'b_list'})
                    if bList == None:
                        log.info(TITLE + " Task (create) :  category not found in " + board + " 1")
                    else :
                        torTRs = bList.findAll('td', attrs={'class':'subject'})
                        if len(torTRs) > 0 :
                            log.info(TITLE + " Task (create) : category found in " + board)
                            CATEGORY = board 
                            break
                        else :
                            log.info(TITLE + " Task (create) :  category not found in " + board + " 2")

                log.info(REAL_TITLE)
                if len(CATEGORY) == 0 :
                  REAL_TITLE = REAL_TITLE.rstrip(re.search('(.\d{4}.*)', REAL_TITLE).group(0))
                  for board in boardList:
                    response = req3.get("http://www.tfreeca22.com/board.php?b_id=" + board + "&mode=list&sc=" + REAL_TITLE + "&x=0&y=0")
                    data = response.text.encode('ISO-8859-1')
                    sp = BeautifulSoup.BeautifulSoup(data)
                    bList = sp.find('table', attrs={'class':'b_list'})
                    if bList == None:
                        log.info(TITLE + " Task (create) :  category not found in " + board + " 3")
                    else :
                        torTRs = bList.findAll('td', attrs={'class':'subject'})
                        if len(torTRs) > 0 :
                            log.info(TITLE + " Task (create) : category found in " + board)
                            CATEGORY = board 
                            break
                        else :
                            log.info(TITLE + " Task (create) :  category not found in " + board + " 4")

                if len(CATEGORY) == 0 :
                  REAL_TITLE = REAL_TITLE.replace(".", "")
                  for board in boardList:
                    response = req3.get("http://www.tfreeca22.com/board.php?b_id=" + board + "&mode=list&sc=" + REAL_TITLE + "&x=0&y=0")
                    data = response.text.encode('ISO-8859-1')
                    sp = BeautifulSoup.BeautifulSoup(data)
                    bList = sp.find('table', attrs={'class':'b_list'})
                    if bList == None:
                        log.info(TITLE + " Task (create) :  category not found in " + board + " 5")
                    else :
                        torTRs = bList.findAll('td', attrs={'class':'subject'})
                        if len(torTRs) > 0 :
                            log.info(TITLE + " Task (create) : category found in " + board)
                            CATEGORY = board 
                            break
                        else :
                            REAL_TITLE = REAL_TITLE.replace(".", " ")
                            log.info(TITLE + " Task (create) :  category not found in " + board + " 6")
                
              log.info(TITLE + " Task (create) : category : " + CATEGORY)
              log.info(TITLE + " Task (create) : multiple file check start")

              # tfreeca 단일 TV 쇼
              if len(CATEGORY) > 0 and CATEGORY != 'tmovie' and len(FILES_COUNT) == 1 :
                log.info(TITLE +" Task (create) : single file tv show")
                TEMP=TITLE.find(".E")
                CHECK_STRING=TITLE[TEMP+2:TEMP+4]
                try :
                    int(CHECK_STRING);
                    log.info(TITLE + " Task (create) : TV " + CHECK_STRING + " episode validated")
                    REAL_TITLE=TITLE[0:TEMP]

                    if CATEGORY == 'tdrama' :
                        PATH=CONFIG.GetTdramaPath()
                        log.info(TITLE + " Task (create) : target path" + PATH )
                        create_directory(PATH, REAL_TITLE)
                    elif CATEGORY == 'tent' :
                        PATH = CONFIG.GetTentPath()
                        log.info(TITLE + " Task (create) : target path" + PATH )
                        create_directory(PATH, REAL_TITLE)
                    elif CATEGORY == 'tv' :
                        PATH = CONFIG.GetTvPath()
                        log.info(TITLE + " Task (create) : target path" + PATH )
                        create_directory(PATH, REAL_TITLE)
                except : 
                    log.info("This TV SHOW don't have E(episode tag) : " + TITLE)
              # 그외 tfreeca 단일 파일
              elif len(CATEGORY) > 0 and CATEGORY == 'tmovie' and len(FILES_COUNT) == 1 :
                    REAL_TITLE = os.path.splitext(TITLE)[0]
                    log.info(TITLE  +" Task (create) : single file movie or etc" )
                    CATEGORY=re.search('b_id=(.*?)&id=', URI)
                    CATEGORY=CATEGORY.group(1)

                    if CATEGORY == 'tmovie' :
                        PATH = CONFIG.GetTmoviePath()
                        create_directory(PATH, REAL_TITLE)
                    #elif CATEGORY == 'tani' :
                    #    PATH=CONFIG.GetTaniPath()
                    #    REAL_TITLE=REAL_TITLE.rstrip(" - ")
                    #    create_directory(PATH, REAL_TITLE)
              # 모든 복수 파일
              elif len(FILES_COUNT) != 1 :
                if len(CATEGORY) > 0 :
                  log.info(TITLE  +" Task (create) : mutiple files if tfreeca download" )
                  FLAG = 1
                  f = open("FOLDER_LIST", 'r')
                  for line in f :
                      if CATEGORY + "\t" + TITLE in line :
                          log.info(TITLE +" Task (create) : already exists in temp file if tfreeca download")
                          FLAG = FLAG + 1
                  f.close()
                  if FLAG == 1 :
                      f = open("FOLDER_LIST", 'a')
                      data = CATEGORY + "\t" + TITLE + "\n"
                      f.write(data)
                      f.close()
                      log.info(TITLE +" Task (create) : new saved in temp file if tfreeca download")
                else :
                  log.info(TITLE + " Task (create) : failed to create folder" )
              else : 
                  log.info(TITLE + " Task (create) : failed to create folder" )
            # 다운 완료 된 파일 이동 처리
            elif STATUS.find("finished") != -1 :
              log.info(TITLE  +" Task (move) : finished file check")
              DESTINATION_PATH=data['data']['tasks'][0]['additional']['detail']['destination']
              DOWNLOAD_PATH=CONFIG.GetDownloadPath()
              # 사용자 지정 폴더 없고 
              if DOWNLOAD_PATH.find(DESTINATION_PATH) != -1 :
                log.info(TITLE + " Task (move) : downloaded to default path ")
                # 복수 파일 다운로드 시 이동 처리 시작
                CATEGORY = ""
                # 다운 소스가 tfreeca 인 경우 
                if URI.find("/tfreeca/") != -1 :
                    CATEGORY=re.search('b_id=(.*?)&id=', URI)
                    CATEGORY=CATEGORY.group(1)
                # tfreeca 아닌 경우  tfreeca 검색 시도
                else :
                  log.info(TITLE + " Task (move) : searching category in tfreea " )
                  req3=requests.Session()
                  boardList = ['tdrama', 'tent', 'tv', 'tmovie']
                  REAL_TITLE = ""
                  if TITLE.find(".E") != 1 :
                      TEMP=TITLE.find(".E")
                      CHECK_STRING=TITLE[TEMP+2:TEMP+4]
                      try :
                          int(CHECK_STRING);
                          REAL_TITLE=TITLE[0:TEMP]
                      except :
                          REAL_TITLE = os.path.splitext(TITLE)[0]
                  else :
                      REAL_TITLE = os.path.splitext(TITLE)[0]
  
                  for board in boardList:
                      response = req3.get("http://www.tfreeca22.com/board.php?b_id=" + board + "&mode=list&sc=" + REAL_TITLE + "&x=0&y=0")
                      data = response.text.encode('ISO-8859-1')
                      sp = BeautifulSoup.BeautifulSoup(data)
                      bList = sp.find('table', attrs={'class':'b_list'})
                      if bList == None:
                          log.info(TITLE + " Task (move) :  category not found in " + board + " 1")
                      else :
                          torTRs = bList.findAll('td', attrs={'class':'subject'})
                          if len(torTRs) > 0 :
                              log.info(TITLE + " Task (move) : category found in " + board)
                              CATEGORY = board 
                              break
                          else :
                              log.info(TITLE + " Task (move) :  category not found in " + board + " 2")

                  if len(CATEGORY) == 0 :
                    REAL_TITLE = REAL_TITLE.rstrip(re.search('(.\d{4}.*)', REAL_TITLE).group(0))
                    for board in boardList:
                      response = req3.get("http://www.tfreeca22.com/board.php?b_id=" + board + "&mode=list&sc=" + REAL_TITLE + "&x=0&y=0")
                      data = response.text.encode('ISO-8859-1')
                      sp = BeautifulSoup.BeautifulSoup(data)
                      bList = sp.find('table', attrs={'class':'b_list'})
                      if bList == None:
                          log.info(TITLE + " Task (move) :  category not found in " + board + " 3")
                      else :
                          torTRs = bList.findAll('td', attrs={'class':'subject'})
                          if len(torTRs) > 0 :
                              log.info(TITLE + " Task (move) : category found in " + board)
                              CATEGORY = board 
                              break
                          else :
                              log.info(TITLE + " Task (move) :  category not found in " + board + " 4")

                  if len(CATEGORY) == 0 :
                    REAL_TITLE = REAL_TITLE.replace(".", "")
                    for board in boardList:
                      response = req3.get("http://www.tfreeca22.com/board.php?b_id=" + board + "&mode=list&sc=" + REAL_TITLE + "&x=0&y=0")
                      data = response.text.encode('ISO-8859-1')
                      sp = BeautifulSoup.BeautifulSoup(data)
                      bList = sp.find('table', attrs={'class':'b_list'})
                      if bList == None:
                          log.info(TITLE + " Task (move) :  category not found in " + board + " 5")
                      else :
                          torTRs = bList.findAll('td', attrs={'class':'subject'})
                          if len(torTRs) > 0 :
                              log.info(TITLE + " Task (move) : category found in " + board)
                              CATEGORY = board 
                              break
                          else :
                              REAL_TITLE = REAL_TITLE.replace(".", " ")
                              log.info(TITLE + " Task (move) :  category not found in " + board + " 6")
                  
                log.info(TITLE + " Task (move) : category : " + CATEGORY)
                log.info(TITLE + " Task (move) : multiple file check start")
                infile = file('FOLDER_LIST')
                tempfile = open('FOLDER_LIST.tmp', 'w')
                FLAG=1
                for line in infile :
                    if CATEGORY + "\t" + TITLE not in line :
                        tempfile.write(line)
                    elif CATEGORY == 'tdrama' :
                        PATH=CONFIG.GetTdramaPath()
                        move_folder(DOWNLOAD_PATH, PATH, TITLE)
                        FLAG=FLAG+1
                    elif CATEGORY == 'tmovie' :
                        PATH=CONFIG.GetTmoviePath()
                        log.info(TITLE + " Task (move) : (multiple) subtitle downloading to " + DOWNLOAD_PATH + TITLE)
                        os.system("/bin/subliminal download -l ko \"" + DOWNLOAD_PATH + TITLE + "\"* >> ./DownloadStationBot-" + str(today_date) + ".log")
                        log.info(TITLE + " Task (move) : (multiple) subtitle downloaded to " + DOWNLOAD_PATH + TITLE)
                        move_folder(DOWNLOAD_PATH, PATH, TITLE)
                        FLAG=FLAG+1
                    elif CATEGORY == 'tent' :
                        PATH=CONFIG.GetTentPath()
                        move_folder(DOWNLOAD_PATH, PATH, TITLE)
                        FLAG=FLAG+1
                    elif CATEGORY == 'tv' :
                        PATH=CONFIG.GetTvPath()
                        move_folder(DOWNLOAD_PATH, PATH, TITLE)
                        FLAG=FLAG+1
                    #elif CATEGORY == 'tani' :
                    #    PATH=CONFIG.GetTaniPath()
                    #    shutil.move(DOWNLOAD_PATH + TITLE, PATH + TITLE)
                    #    FLAG=FLAG+1
                infile.close()
                tempfile.close()
                os.popen("cp -p  FOLDER_LIST.tmp  FOLDER_LIST ")
                log.info(TITLE + " Task (move) : multiple file check finished")
                # 복수 파일 처리 종료

                # FLAG가 1인 경우(즉 복수 파일에서 처리되지 못한것은) 단일 파일로  처리,  TV 프로그램 처리
                log.info(TITLE + " Task (move) : single tv show file check start")
                if len(CATEGORY) > 0  and CATEGORY != 'tmovie' and FLAG == 1 :
                  TEMP=TITLE.find(".E")
                  CHECK_STRING=TITLE[TEMP+2:TEMP+4]
                  log.info(TITLE + " Task (move) : TV Show episode check for " + CHECK_STRING )
                  REAL_TITLE=TITLE
                  try :
                      int(CHECK_STRING);
                      REAL_TITLE=TITLE[0:TEMP]
                  except Exception:
                      print(traceback.format_exc())
                      log.info(TITLE + " Task (move) : This TV SHOW don't have E(episode tag)  : " + TITLE)
                  log.info(TITLE + " Task (move) : This is title  : " + REAL_TITLE)
                  if CATEGORY == 'tdrama' :
                      TO_PATH=CONFIG.GetTdramaPath()
                      RESULT = move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                      if int(RESULT) == 2:
                          FLAG=FLAG+1
                  elif CATEGORY == 'tent' :
                      TO_PATH=CONFIG.GetTentPath()
                      RESULT = move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                      if int(RESULT) == 2:
                          FLAG=FLAG+1
                  elif CATEGORY == 'tv' :
                      TO_PATH=CONFIG.GetTvPath()
                      RESULT = move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                      if int(RESULT) == 2:
                          FLAG=FLAG+1
                  log.info(TITLE + " Task (move) : single tv show file check finished")
                # TV가 아닌 경우 단일 파일은(단일 파일 영화?) 파일 이름과 동일한 폴더 생성 후 이동
                elif CATEGORY == 'tmovie' and FLAG == 1 :
                    log.info(TITLE + " Task (move) : single movie or etc file check start")
                    REAL_TITLE = os.path.splitext(TITLE)[0]

                    if CATEGORY == 'tmovie' :
                        TO_PATH=CONFIG.GetTmoviePath()
                        RESULT = move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                        if int(RESULT) == 2:
                            log.info(TITLE + " Task (move) : (single) subtitle downloading to " + TO_PATH + REAL_TITLE )
                            os.system("/bin/subliminal download -l ko \"" + TO_PATH + REAL_TITLE + "\"* >> ./DownloadStationBot-" + str(today_date) + ".log")
                            log.info(TITLE + " Task (move) : (single) subtitle downloaded to " + TO_PATH + REAL_TITLE )
                            FLAG=FLAG+1
                    #elif CATEGORY == 'tani' :
                    #    PATH=CONFIG.GetTaniPath()
                    #    shutil.move(DOWNLOAD_PATH + TITLE, PATH + TITLE)
                    #    FLAG=FLAG+1
                    log.info(TITLE + " Task (move) : single movie or etc file check finished")
                # 여전히 못찾은 경우 
                if FLAG == 1 :
                  if TITLE.find(".E") != -1 :
                    log.info(TITLE + " Task (move) : single tv show : search in exists folder")
                    # TV show의 경우 기존 폴더 있는지 검색한번 해봄
                    TEMP=TITLE.find(".E")
                    CHECK_STRING=TITLE[TEMP+2:TEMP+4]
                    log.info(TITLE + " Task (move) : TV " + CHECK_STRING + " episode validated")
                    try :
                      int(CHECK_STRING);
                      REAL_TITLE=TITLE[0:TEMP]
                      DOWNLOAD_PATH=CONFIG.GetDownloadPath()
                      TO_PATH=CONFIG.GetTdramaPath()
                      RESULT = move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                      if int(RESULT) == 1 :
                          TO_PATH=CONFIG.GetTentPath()
                          RESULT = move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                          if int(RESULT) == 1 :
                              TO_PATH=CONFIG.GetTvPath()
                              RESULT = move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                              if int(RESULT) != 1 :
                                  FLAG = FLAG + 1
                                  log.info(TITLE + " Task (move) :  single, not from tfreeca, found already exist folder")
                          else :
                              FLAG = FLAG +1
                              log.info(TITLE + " Task (move) :  single, not from tfreeca, found already exist folder")
                      else :
                          FLAG = FLAG + 1
                          log.info(TITLE + " Task (move) :  single, not from tfreeca, found already exist folder")
                    except :
                        log.info(TITLE + " Task (move) : is not tv show or failed")
                    log.info(TITLE + " Task (move) : single tv show : search in exists folder finished")
                    #if FLAG == 1 :
                # tfreeca 아니고 TV show도 아닌경우 자막 다운로드 시도
                #elif TITLE.find(".E") == -1 :
                #    DOWNLOAD_PATH=CONFIG.GetDownloadPath()
                #    log.info(TITLE + " Task (just sub) : (user) subtitle downloading to " + DOWNLOAD_PATH + TITLE)
                #    os.system("/bin/subliminal download -l ko \"" + DOWNLOAD_PATH + TITLE + "\"* >> ./DownloadStationBot-" + str(today_date) + ".log")
                #    log.info(TITLE + " Task (just sub) : (user) subtitle downloading to " + DOWNLOAD_PATH + TITLE)

                #  log.info(TITLE + " Task (move) : single not downloaded in tfreeca but search in tfreea " )
                #  req3=requests.Session()
                #  boardList = ['tdrama', 'tent', 'tv', 'tmovie']
                #  keyword = TITLE

                #  for board in boardList:
                #      response = req3.get("http://www.tfreeca22.com/board.php?b_id=" + board + "&mode=list&sc=" + keyword + "&x=0&y=0")
                #      data = response.text.encode('ISO-8859-1')
                #      #log.info(data)
                #      sp = BeautifulSoup.BeautifulSoup(data)
                #      bList = sp.find('table', attrs={'class':'b_list'})
                #      log.info(sp)
                #      if bList == None:
                #          log.info(TITLE + " Task (move) : single no found in " + board)
                #      else :
                #          log.info(TITLE + " Task (move) : single found in " + board)
                #          CATEGORY = board 
                #         torTRs = bList.findAll('td', attrs={'class':'subject'})
                #          log.info(torTRs)
                if FLAG != 1 : 
                  TASK_ID=task['id']
                  response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=delete&id=" + TASK_ID + "&force_complete=false")


              # 사용자 폴더 지정 다운로드 작업
              else :
                  log.info(TITLE + " Task : user definition path, finished download")
                  if TITLE.find(".E") == -1 :
                    DOWNLOAD_PATH=CONFIG.GetDownloadPath()
                    log.info(TITLE + " Task (just sub) : (user) subtitle downloading to " + DOWNLOAD_PATH + TITLE)
                    os.system("/bin/subliminal download -l ko \"" + DOWNLOAD_PATH + TITLE + "\"* >> ./DownloadStationBot-" + str(today_date) + ".log")
                    log.info(TITLE + " Task (just sub) : (user) subtitle downloading to " + DOWNLOAD_PATH + TITLE)
                  TASK_ID=task['id']
                  response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=delete&id=" + TASK_ID + "&force_complete=false")
                  log.info(TITLE + " Task : user definition path, finished download and remove task in download station")


                  #if FLAG != 1 :
                  #    response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=delete&id=" + TASK_ID + "&force_complete=false")
              #else :
                  #response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=delete&id=" + TASK_ID + "&force_complete=false")

            #elif  STATUS.find("finished") != -1 :
            #    log.info(TITLE + " Task : not found rule, but all finished task remove task in download station")
            #    TASK_ID=task['id']
            #    response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=delete&id=" + TASK_ID + "&force_complete=false")
                


    LOG_FILE = os.popen("find . -type f -name 'DownloadStationBot-*.log' -mtime +0").read()
    for logfile in LOG_FILE.splitlines() :
        os.remove(logfile)
        log.info("remove logfile : " + logfile )
       

    response = req.get(DEFAULT_URL + AUTH_PATH + "?api=" + AUTH_API + "&version=" + str(AUTH_VERSION) + "&method=logout&session=DownloadStation")
    log.info("LOGOUT ")
    log.info("******************************************************************************************************************")

if __name__ == "__main__": 
    main()
