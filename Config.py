#-*- coding: utf-8 -*-

import sys
import os
import socket
import ConfigParser

class Config(object):
    account = ""
    password = ""
    ip = ""
    port = ""
    main_path = ""
    tdrama_path = ""
    tani_path = ""
    tv_path = ""
    tent_path = ""
    tmovie_path = ""
    download_path = ""

    def __init__(self, *args, **kwargs):
        config_path = str(args[0])
        config = ConfigParser.RawConfigParser()
        config.read(config_path)

        self.account = config.get('DSM', 'ACCOUNT')
        self.password= config.get('DSM', 'PASSWORD')
        self.ip= config.get('DSM', 'IP')
        self.port = config.get('DSM', 'PORT')
        self.download_path = config.get('DIRECTORY', 'download')
        self.main_path = config.get('DIRECTORY', 'main')
        self.tdrama_path = config.get('DIRECTORY', 'tdrama')
        self.tani_path = config.get('DIRECTORY', 'tani')
        self.tv_path = config.get('DIRECTORY', 'tv')
        self.tent_path = config.get('DIRECTORY', 'tent')
        self.tmovie_path = config.get('DIRECTORY', 'tmovie')


    def GetAccount(self):
        return self.account

    def GetPassword(self):
        return self.password

    def GetIP(self):
        return self.ip

    def GetPort(self):
        return self.port

    def GetDownloadPath(self):
        return self.download_path

    def GetMainPath(self):
        return self.main_path

    def GetTdramaPath(self):
        return self.tdrama_path

    def GetTaniPath(self):
        return self.tani_path

    def GetTvPath(self):
        return self.tv_path

    def GetTentPath(self):
        return self.tent_path

    def GetTmoviePath(self):
        return self.tmovie_path
