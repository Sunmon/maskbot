import json
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


def update_info():

    print('try to get mask info from browser')
    ## 브라우저 열기
    driver = open_browser('https://coronamask.kr')

    ##TODO 아침 06:00마다 마스크 리스트 정보 업데이트하기
    ## 마스크 리스트 초기화
    mask_list = init_mask_list(driver)

    ## 마스크 정보 저장하기
    save_update_to_json(mask_list)
    print('updated mask info')

    ## driver 닫기
    driver.quit()

## 웹페이지 열기
def open_browser(_link):
    _link = 'https://coronamask.kr'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--single-process')
    options.add_argument('--dissable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    driver = webdriver.Chrome('../assets/chromedriver_linux64/chromedriver', options=options) ## linux
    driver.set_page_load_timeout(60)
    try:
        driver.get(_link)
    except Exception :
        print("timeout error")
    else:
        return driver

## mask_list를 json에 저장
## 게릴라판매는 직접 json만 수정하면 될수있도록하기위함
def save_update_to_json(mask_list):
    with open('../data/coronamask.json', 'w', encoding='utf-8') as _json_file:
        json.dump(mask_list, _json_file, ensure_ascii=False, indent = "\t")


## mask_list 초기화
def init_mask_list(_driver):
    ## soup 가져오기
    html, soup = get_html(_driver)

    ## 필요한 정보가 담긴 wrapper 가져오기
    raw_data = soup.select('.pb-14 > div:nth-child(1) > div:nth-child(1) > div.w-full > div:nth-child(2)')
    mask_list = {}

    for data in raw_data:
        d = get_data_dictionary(data)
        if d : mask_list = {**mask_list, **get_data_dictionary(data)}

    return mask_list


## raw data 단일 element를 받아 dictionary형태로 반환
def get_data_dictionary(_raw_data):
    raw_str = _raw_data.find('div').get_text()

    ## 구매 불가능한 상태면 return None
    available = _raw_data.select('div > p')[1].get_text().strip()
    if available == "판매종료" : return None

    ## 정규식 이용하여 속성 알아내기
    m = re.match(r'\[(.+)\](.+)', raw_str)
    name = m.group(1)
    context = m.group(2)
    link = _raw_data.find('a').get('href')
    sell_time = re.search(r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}', available)
    if sell_time : sell_time = sell_time.group()
    dic = {name:{ 'name':name, 'context':context, 'link':link, 'sell_time':sell_time, 'alerted':False}}
    return dic


## 페이지의 내용을 조작할수 있게 html과 bs4 결과를 리턴
def get_html(_driver):
    html = _driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    return html, soup



## 실행하기
if __name__ == '__main__':
    update_info()
