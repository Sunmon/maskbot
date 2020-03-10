"""
description : bot 클래스 : 크롤링하고 알람까지 하는 클래스. 관리자.
manager클래스다. 메인에선 그냥 이 클래스의 함수만 실행시키면 된다.
"""
import json
import time
import re
import datetime 
from pytz import timezone, utc
from alerter import Alerter

class Bot():
    def __init__(self):
        ##self.crawl_site = 'https://coronamask.kr'
        self.json_file = '/root/maskbot/data/coronamask.json'
        self.mask_list = {}     # 크롤링할 마스크 사이트 정보 {name: {content, link, sell_time}}
        self.alerter = Alerter()
        pass
        
    ## 크롤링 메소드
    def crawling(self, _time = 60, _count = -1):

        ## 마스크 정보 읽어오기
        self.get_info_from_json()
        
        ## 판매시간 계산하여 10분전이면 알림 보내기
        msg_list = [mask for mask in self.mask_list.values() if self.is_time_to_alert(mask)]

        ## 알림 메세지 보내기
        if msg_list:
            try:
                self.alerter.send_all_msgs(msg_list)
            except Exception as e:
                print(e)
            else:
                ## 알람 보낸 애들은 alerted = True로 전환
                for dic in msg_list:
                    n = dic['name']
                    self.mask_list[n]['alerted']=True
                self.save_update_to_json()


    ## 알림 보낼 수 있는 시간인가 확인하여 true/false 리턴
    def is_time_to_alert(self, mask):
        ## 이미 알림을 보냈으면 알림 또 보낼 필요 없음
        if mask['alerted'] : return False

        ## 만약 마스크 판매 시간이 안 정해졌으면 알림 못 보냄
        if not mask['sell_time'] : return False

        ## 한국의 현재 시간 가져오기
        KST = timezone('Asia/Seoul')
        now = datetime.datetime.utcnow()
        now = utc.localize(now).astimezone(KST)

        ## mask 판매시간을 datetime객체로 변환
        mask_time = datetime.datetime.strptime(mask['sell_time'], '%Y/%m/%d %H:%M')
        mask_time = KST.localize(mask_time)
        ##mask_time = mask_time.astimezone(KST)
        
        ## 마스크 판매시간 10분전이면 알림을 보내기
        diff = (mask_time - now).seconds // 60
        day_diff = (mask_time - now).days
        return ((day_diff==0) and (diff < 12))


    ## mask_list를 json에 저장
    ## 게릴라판매는 직접 json만 수정하면 될수있도록하기위함
    def save_update_to_json(self):
        with open(self.json_file, 'w', encoding='utf-8') as _json_file:
            json.dump(self.mask_list, _json_file, ensure_ascii=False, indent = "\t")
    

    ## 코로나마스크 json 불러오기
    ## 게릴라 판매들은 수동으로 json에 입력해주기 위함
    def get_info_from_json(self):
        with open(self.json_file, encoding='utf-8') as masks:
            self.mask_list = json.load(masks)
