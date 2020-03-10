""" 메세지를 받아 카카오톡으로 전송한다

public : 
    send_all_msgs(msg_list) : 메세지 리스트를 받아 로그인 후 모두 전송

private :
    __login() : 카카오톡 채널 로그인
    __fill_contents() : 카톡 채널에 알림 메세지 폼 채우기
    __send_alert(): 메세지 리스트의 모든 메세지 전송
"""
import requests
import time
import json
import emoji
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
class Alerter():
    def __init__(self):
        self.LOGIN_INFO={'id':'', 'password':'', 'link':''}
        self.__set_login_info("kakao")
    
    ## 로그인한다 
    def __login(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        ## crontab 사용하려면 절대경로로
        self.driver = webdriver.Chrome('/root/maskbot/assets/chromedriver_linux64/chromedriver', options=options)
        #self.driver = webdriver.Chrome('../assets/chromedriver_linux64/chromedriver')
        self.driver.get(self.LOGIN_INFO['link'])
        self.driver.set_page_load_timeout(30)
        self.driver.find_element_by_id('id_email_2').send_keys(self.LOGIN_INFO['id'])
        time.sleep(2)
        self.driver.find_element_by_id('id_password_3').send_keys(self.LOGIN_INFO['password'])
        time.sleep(2)
        self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div/form/fieldset/div[8]/button').click()
        time.sleep(1)
        print("kakao logined")       
        ##TODO 로그인 실패 처리하기
    
    ## 카카오 로그인 정보 초기화
    def __set_login_info(self, _site):
        with open('/root/maskbot/data/login_info.json') as json_file:
            json_data = json.load(json_file)
            self.LOGIN_INFO['id'] = json_data[_site]["id"]
            self.LOGIN_INFO['password']=json_data[_site]["password"]
            self.LOGIN_INFO['link'] = json_data[_site]["link"]


    ## 카카오톡 알림 폼 채우기
    ## msg는 dictionary로 받아온다
    def __fill_contents(self, _site, d_msg):
        title = d_msg.get('name')
        context = d_msg.get('context')
        context = emoji.get_emoji_regexp().sub(u'', context) #이모지 삭제
        link = d_msg.get('link').replace('https://','')
        link = link.replace('http://','')

        #폼이 열릴때까지 기다리기
        wait = WebDriverWait(self.driver, 3)
        wait.until(presence_of_element_located((By.CSS_SELECTOR, '#messageWrite')))

        #messageWrite 폼 채우기
        message = "[{title}] '{context}'가 약 10분 후 판매됩니다".format(title = title, context = context)
        print("   ",message)
        self.driver.find_element_by_id('messageWrite').send_keys(message)
                
        ##번들메세지 링크 보내기
        self.driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[1]/div[1]/div[4]/div/div/div[4]/label').click()
        self.driver.find_element_by_id('btnName').send_keys('구매 링크 열기')

        ## 링크 url 입력하기
        self.driver.find_element_by_id('linkUpload').click()
        time.sleep(3)
        self.driver.find_element_by_id('linkUpload').send_keys(link)



    ## 알림 보내기
    def __send_alert(self, _msg_list):
        site = 'https://center-pf.kakao.com/_xgWysxb/messages/new/feed'
        print("SEND MESSAGES:")
        ## info_list에 있는 모든 정보들을 보내기
        for msg in _msg_list:

            ## 카톡 채널 접근하기
            self.driver.get(site)

            ## 알림 내용 채우기
            try:
                self.__fill_contents(site, msg)
                time.sleep(1)
            except Exception as e:
                print(e)
                self.driver.quit()

            ## 다음 버튼 누르기
            self.driver.find_element_by_xpath('//*[@id="mArticle"]/div/form/div[2]/span/div/button[2]').click()
            time.sleep(1)

            ## 발송 버튼 누르기
            self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div/form/div[2]/button[4]').click()
            time.sleep(1)

            ## 발송확인
            self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/div/div/div[2]/button[2]').click()
            time.sleep(1)
        
        print("ALL MESSAGE SENT.")
        ##창 닫기
        self.driver.quit()


        

    ## msg_list로 받은 모든 메세지 전송
    def send_all_msgs(self, _msg_list):
        self.__login()
        self.__send_alert(_msg_list)
