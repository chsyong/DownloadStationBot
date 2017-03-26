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
    log.setLevel(logging.DEBUG)
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
    log.info("Request DS INFO : " + DEFAULT_URL + "query.cgi?api=" + INFO_API + "&version=1&method=query&query=" + AUTH_API + "," + TASK_API + "," + FILE_API)
    response = req.get(DEFAULT_URL + "query.cgi?api=" + INFO_API + "&version=1&method=query&query=" + AUTH_API + "," + TASK_API ) 
    log.info("Response DS INFO : " + response.text)
    data = response.json()
    AUTH_PATH=data['data'][AUTH_API]['path']
    AUTH_VERSION=data['data'][AUTH_API]['maxVersion']
    TASK_PATH=data['data'][TASK_API]['path']
    TASK_VERSION=data['data'][TASK_API]['maxVersion']


    req2=requests.Session()
    log.info("Request DS INFO : " + DEFAULT_URL + "query.cgi?api=" + INFO_API + "&version=1&method=query&query=" + AUTH_API + "," + FILE_API)
    response = req2.get(DEFAULT_URL + "query.cgi?api=" + INFO_API + "&version=1&method=query&query=" + AUTH_API + "," + FILE_API) 
    data = response.json()
    log.info("Response DS INFO : " + response.text)
    FILE_PATH=data['data'][FILE_API]['path']
    FILE_VERSION=data['data'][FILE_API]['maxVersion']


    # Login
    log.info("LOGIN")
    log.info("Request Login : " + DEFAULT_URL + AUTH_PATH + "?api=" + AUTH_API + "&version=" + str(AUTH_VERSION) + "&method=login&account=" + ACCOUNT + "&passwd=" + PASSWORD + "&session=DownloadStation&format=cookie")
    response = req.get(DEFAULT_URL + AUTH_PATH + "?api=" + AUTH_API + "&version=" + str(AUTH_VERSION) + "&method=login&account=" + ACCOUNT + "&passwd=" + PASSWORD + "&session=DownloadStation&format=cookie")
    log.info("Response Login : " + response.text)

    log.info("Request Login : " + DEFAULT_URL + AUTH_PATH + "?api=" + AUTH_API + "&version=" + str(AUTH_VERSION) + "&method=login&account=" + ACCOUNT + "&passwd=" + PASSWORD + "&session=FileStation&format=cookie")
    response = req2.get(DEFAULT_URL + AUTH_PATH + "?api=" + AUTH_API + "&version=" + str(AUTH_VERSION) + "&method=login&account=" + ACCOUNT + "&passwd=" + PASSWORD + "&session=FileStation&format=cookie")
    log.info("Response Login : " + response.text)

    # Get DS Task List
    log.info("Request Task List : " + DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=list")
    response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=list")
    log.info("Response Task List : " + response.text)
    data = response.json()
    tasks=data['data']['tasks']

    # 다운로드 작업 있는지 확인
    if len(tasks) > 0 :
        log.info("Download Task Exist")

        for task in tasks:
            TASK_ID=task['id']
            log.info("Request Detail : " + DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=getinfo&id=" + TASK_ID + "&additional=detail,transfer,file")
            response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=getinfo&id=" + TASK_ID + "&additional=detail,transfer,file")
            log.info("Response Detail : " + response.text)
            data = response.json()
            URI=data['data']['tasks'][0]['additional']['detail']['uri']
            TITLE=data['data']['tasks'][0]['title']
            STATUS=data['data']['tasks'][0]['status']
            log.info(TITLE + " Task : starting check it")
            log.info(TITLE + " Task : status : " + STATUS)

            # 다운로드 작업에 대해서는 폴더 생성
            if  URI.find("/tfreeca/") != -1 and STATUS.find("downloading") != -1 and TITLE.find(".php") == -1 : 
              log.info(TITLE + " Task (create) : downloading file check")
              FILES_COUNT=data['data']['tasks'][0]['additional']['file']
              log.info(TITLE + " Task (create) : " + str(len(FILES_COUNT)) +  " files")
              CATEGORY=re.search('b_id=(.*?)&id=', URI)
              CATEGORY=CATEGORY.group(1)
              log.info(TITLE + " Task (create) : categoty : " + CATEGORY)
              # 단일 TV 쇼
              if len(FILES_COUNT) == 1 and TITLE.find(".E") != -1 :
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
              # 그외 단일 파일
              elif len(FILES_COUNT) == 1 :
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
              # 복수 파일
              elif len(FILES_COUNT) != 1 :
                  log.info(TITLE  +" Task (create) : mutiple files" )
                  FLAG = 1
                  f = open("FOLDER_LIST", 'r')
                  for line in f :
                      if CATEGORY + "\t" + TITLE in line :
                          log.info(TITLE +" Task (create) : already exists in temp file")
                          FLAG = FLAG + 1
                  f.close()
                  if FLAG == 1 :
                      f = open("FOLDER_LIST", 'a')
                      data = CATEGORY + "\t" + TITLE + "\n"
                      f.write(data)
                      f.close()
                      log.info(TITLE +" Task (create) : new saved in temp file")
            # 다운 완료 된 파일 이동 처리
            elif  URI.find("/tfreeca/") != -1 and STATUS.find("finished") != -1 :
              log.info(TITLE  +" Task (move) : finished file check")
              DESTINATION_PATH=data['data']['tasks'][0]['additional']['detail']['destination']
              DOWNLOAD_PATH=CONFIG.GetDownloadPath()
              # 사용자 지정 폴더 있는지 확인 후 복수 파일 다운로드 시 이동 처리
              if DOWNLOAD_PATH.find(DESTINATION_PATH) != -1 :
                log.info(TITLE + " Task (move) : downloaded to default path ")
                CATEGORY=re.search('b_id=(.*?)&id=', URI)
                CATEGORY=CATEGORY.group(1)
                log.info(TITLE + " Task (move) : category : " + CATEGORY)
                log.info(TITLE + " Task (move) : multiple file start")
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
                log.info(TITLE + " Task (move) : temp file finished")

                # 단일 파일 TV 프로그램 처리
                log.info(TITLE + " Task (move) : single tv show file start")
                if FLAG == 1 and TITLE.find(".E") != -1 :
                  TEMP=TITLE.find(".E")
                  CHECK_STRING=TITLE[TEMP+2:TEMP+4]
                  log.info(TITLE + " Task (move) : TV " + CHECK_STRING + " episode validated")
                  try :
                    int(CHECK_STRING);
                    REAL_TITLE=TITLE[0:TEMP]
                    if CATEGORY == 'tdrama' :
                        TO_PATH=CONFIG.GetTdramaPath()
                        move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                        FLAG=FLAG+1
                    elif CATEGORY == 'tent' :
                        TO_PATH=CONFIG.GetTentPath()
                        move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                        FLAG=FLAG+1
                    elif CATEGORY == 'tv' :
                        TO_PATH=CONFIG.GetTvPath()
                        move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                        FLAG=FLAG+1
                  except Exception:
                      print(traceback.format_exc())
                      log.info(TITLE + " Task (move) : This TV SHOW don't have E(episode tag) and Failed move : " + TITLE)
                # TV 제외 분석 불가는 파일 이름과 동일 한 폴더로 이동
                elif FLAG == 1 :
                    log.info(TITLE + " Task (move) : single movie or etc file start")
                    REAL_TITLE = os.path.splitext(TITLE)[0]

                    if CATEGORY == 'tmovie' :
                        TO_PATH=CONFIG.GetTmoviePath()
                        move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                        log.info(TITLE + " Task (move) : (single) subtitle downloading to " + TO_PATH + REAL_TITLE )
                        os.system("/bin/subliminal download -l ko \"" + TO_PATH + REAL_TITLE + "\"* >> ./DownloadStationBot-" + str(today_date) + ".log")
                        log.info(TITLE + " Task (move) : (single) subtitle downloaded to " + TO_PATH + REAL_TITLE )
                        FLAG=FLAG+1
                    #elif CATEGORY == 'tani' :
                    #    PATH=CONFIG.GetTaniPath()
                    #    shutil.move(DOWNLOAD_PATH + TITLE, PATH + TITLE)
                    #    FLAG=FLAG+1

                if FLAG != 1 : 
                    TASK_ID=task['id']
                    response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=delete&id=" + TASK_ID + "&force_complete=false")

              # 사용자 폴더 지정 다운로드 작업
              else :
                  log.info(TITLE + " Task : user definition path, finished download")
                  TASK_ID=task['id']
                  response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=delete&id=" + TASK_ID + "&force_complete=false")
                  log.info(TITLE + " Task : user definition path, finished download and remove task in download station")
            # tfreeca 는 아니지만 TV show의 경우 검색한번 해봄
            elif TITLE.find(".E") != -1 and STATUS.find("finished") != -1 :
                log.info(TITLE + " Task (no tfreeca) :  not from tfreeca, search ")
                TEMP=TITLE.find(".E")
                CHECK_STRING=TITLE[TEMP+2:TEMP+4]
                log.info(TITLE + " Task (no tfreeca) : TV " + CHECK_STRING + " episode validated")
                try :
                  int(CHECK_STRING);
                  REAL_TITLE=TITLE[0:TEMP]
                  DOWNLOAD_PATH=CONFIG.GetDownloadPath()
                  TO_PATH=CONFIG.GetTdramaPath()
                  move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                  TO_PATH=CONFIG.GetTentPath()
                  move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                  TO_PATH=CONFIG.GetTvPath()
                  move_file(DOWNLOAD_PATH, TO_PATH, TITLE, REAL_TITLE, FILE_VERSION, req2)
                  TASK_ID=task['id']
                  response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=delete&id=" + TASK_ID + "&force_complete=false")
                except :
                    log.info(TITLE + " Task (no tfreeca) : is not tv show or failed")
            # tfreeca 아니고 TV show도 아닌경우 자막 다운로드 시도
            elif TITLE.find(".E") != -1 and STATUS.find("finished") != -1 :
                DOWNLOAD_PATH=CONFIG.GetDownloadPath()
                log.info(TITLE + " Task (just sub) : (user) subtitle downloading to " + DOWNLOAD_PATH + TITLE)
                os.system("/bin/subliminal download -l ko \"" + DOWNLOAD_PATH + TITLE + "\"* >> ./DownloadStationBot-" + str(today_date) + ".log")
                log.info(TITLE + " Task (just sub) : (user) subtitle downloading to " + DOWNLOAD_PATH + TITLE)
            elif  STATUS.find("finished") != -1 :
                log.info(TITLE + " Task : not found rule, but all finished task remove task in download station")
                TASK_ID=task['id']
                response = req.get(DEFAULT_URL + TASK_PATH + "?api=" + TASK_API + "&version=" + str(TASK_VERSION) + "&method=delete&id=" + TASK_ID + "&force_complete=false")
                


    LOG_FILE = os.popen("find . -type f -name 'DownloadStationBot-*.log' -mtime +1").read()
    for logfile in LOG_FILE.splitlines() :
        os.remove(logfile)
        log.info("remove logfile : " + logfile )
       

    response = req.get(DEFAULT_URL + AUTH_PATH + "?api=" + AUTH_API + "&version=" + str(AUTH_VERSION) + "&method=logout&session=DownloadStation")
    log.info("LOGOUT ")
    log.info("******************************************************************************************************************")

if __name__ == "__main__": 
    main()
