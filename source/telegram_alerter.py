""" 메세지를 받아 텔레그램으로 전송한다

public : 
    send_all_msgs(msg_list) : 메세지 리스트를 받아 로그인 후 모두 전송

private :
    __login() : 로그인
    __fill_contents() :  알림 메세지 내용 리턴
    __send_alert(): 메세지 리스트의 모든 메세지 전송
"""
import telegram
import requests
import time
import json
import emoji
from alerter import Alerter
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
class TelegramAlerter(Alerter):
    def __init__(self):
        self.LOGIN_INFO={'token':'', 'chatId':''}
        self.__set_login_info("telegram")
        self.__login()
    
    ## 로그인한다 
    def __login(self):
        self.bot = telegram.Bot(token = self.LOGIN_INFO['token'])
        self.updates = self.bot.getUpdates()
        
    
    ## 텔레그램 로그인 정보 초기화
    def __set_login_info(self, _site):
        with open('/root/maskbot/data/login_info.json') as json_file:
            json_data = json.load(json_file)
            self.LOGIN_INFO['token'] = json_data[_site]["token"]
            self.LOGIN_INFO['chatId'] = json_data[_site]["chatId"]


    ## 텔레그램 알림 메세지 내용 리턴
    ## msg는 dictionary로 받아온다
    def __fill_contents(self, _site, d_msg):
        title = d_msg.get('name')
        context = d_msg.get('context')
        context = emoji.get_emoji_regexp().sub(u'', context) #이모지 삭제
        link = d_msg.get('link')

        #messageWrite 폼 채우기
        message = "[{title}] '{context}'가 약 10분 후 판매됩니다\n 링크:{link}".format(title = title, context = context, link = link)
        print("   ",message)
        return message
        



    ## 알림 보내기
    def __send_alert(self, _msg_list):
    	
        site = 'telegram'
        print("SEND MESSAGES:")
        ## info_list에 있는 모든 정보들을 보내기
        for msg in _msg_list:

            ## 알림 내용 채우기
            _text = self.__fill_contents(site, msg)
            
            ## 발송하기
            self.bot.sendMessage(chat_id=self.LOGIN_INFO['chatId'], text=_text)
        
        print("ALL MESSAGE SENT.")

        

    ## msg_list로 받은 모든 메세지 전송
    def send_all_msgs(self, _msg_list):
        self.__send_alert(_msg_list)
