import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
from time import sleep
from bs4 import BeautifulSoup
import re
import json
from tqdm import tqdm

# --크롬창을 숨기고 실행-- driver에 options를 추가해주면된다
# options = webdriver.ChromeOptions()
# options.add_argument('headless')
gu_list = ['마포구','서대문구','은평구','종로구','중구','용산구','성동구','광진구',
           '동대문구','성북구','강북구','도봉구','노원구','중랑구','강동구','송파구',
           '강남구','서초구','관악구','동작구','영등포구','금천구','구로구','양천구','강서구']


for gu in tqdm(gu_list):
    url = 'https://map.naver.com/v5'
    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]  #크롬드라이버 버전 확인

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito") # 시크릿 모드
#    chrome_options.add_argument("--headless") # 리눅스 GUI 없는 디스플레이 모드
    chrome_options.add_argument("--no-sandbox") # 리소스에 대한 엑서스 방지
    chrome_options.add_argument("--disable-setuid-sandbox") # 크롬 충돌 방지
    chrome_options.add_argument("--disable-dev-shm-usage") # 메모리 부족 에러 방지
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    try: # 크롬 드라이버
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver', chrome_options=chrome_options)   
    except:
        chromedriver_autoinstaller.install(True)
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver', chrome_options=chrome_options)

    # WebDruverException Error 방지 기존의 드라이버 버젼으로 지정
    # driver = webdriver.Chrome(executable_path='/Users/cmblir/Python/Musinsa-Analysis/100/chromedriver')
    driver.implicitly_wait(10) # 10초정도 멈추기
     # driver = webdriver.Chrome('./chromedriver',chrome_options=options) # 크롬창 숨기기
    driver.get(url)
    key_word = f'{gu} 맛집'  # 검색어


    # css 찾을때 까지 10초대기
    def time_wait(num, code):
        try:
            wait = WebDriverWait(driver, num).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, code)))
        except:
            print(code, '태그를 찾지 못하였습니다.')
            driver.quit()
        return wait


    # css를 찾을때 까지 10초 대기
    time_wait(40, 'div.input_box > input.input_search')

    # 검색창 찾기
    search = driver.find_element(By.CSS_SELECTOR,'div.input_box > input.input_search')
    search.send_keys(key_word)  # 검색어 입력
    search.send_keys(Keys.ENTER)  # 엔터버튼 누르기

    res = driver.page_source  # 페이지 소스 가져오기
    soup = BeautifulSoup(res, 'html.parser')  # html 파싱하여  가져온다

    sleep(1)


    # frame 변경 메소드
    def switch_frame(frame):
        driver.switch_to.default_content()  # frame 초기화
        driver.switch_to.frame(frame)  # frame 변경
        res
        soup


    # 페이지 다운
    def page_down(num):
        body = driver.find_element(By.CSS_SELECTOR,'body')
        body.click()
        for i in range(num):
            body.send_keys(Keys.PAGE_DOWN)


    # frame 변경
    switch_frame('searchIframe')
    page_down(40)
    sleep(5)

    # 매장 리스트
    store_list = driver.find_elements(By.CSS_SELECTOR,'._1EKsQ')
    # 페이지 리스트
    next_btn = driver.find_elements(By.CSS_SELECTOR,'._2ky45 > a')

    # dictionary 생성
    store_dict = {'매장정보': []}
    # 시작시간
    start = time.time()
    print('[크롤링 시작...]')

    # 크롤링 (페이지 리스트 만큼)
    for btn in range(len(next_btn))[1:]:  # next_btn[0] = 이전 페이지 버튼 무시 -> [1]부터 시작
        store_list
        for data in range(len(store_list)):  # 매장 리스트 만큼
            page = driver.find_elements(By.CSS_SELECTOR,'.OXiLu')
            page[data].click()
            sleep(2)
            try:
                # 상세 페이지로 이동
                switch_frame('entryIframe')
                time_wait(5, '._3XamX')
                # 스크롤을 맨밑으로 1초간격으로 내린다.
                for down in range(3):
                    sleep(1)
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # -----매장명 가져오기-----
                store_name = driver.find_element(By.CSS_SELECTOR,'._3XamX').text

                # -----평점-----
                try:
                    store_rating_list = driver.find_element(By.CSS_SELECTOR,'._1A8_M').text
                    store_rating = re.sub('별점', '', store_rating_list).replace('\n', '')  # 별점이라는 단어 제거
                except:
                    pass
                print(store_rating)

                # -----주소(위치)-----
                try:
                    store_addr_list = driver.find_elements(By.CSS_SELECTOR,'._1aj6-')
                    for i in store_addr_list:
                        store_addr = i.find_element(By.CSS_SELECTOR,'._1h3B_').text
                except:
                    pass
                print(store_addr)
                # -----전화번호 가져오기-----
                try:
                    store_tel = driver.find_element(By.CSS_SELECTOR,'._3ZA0S').text
                except:
                    pass

                print(store_tel)
                # -----영업시간-----
                try:
                    store_time_list = driver.find_elements(By.CSS_SELECTOR,'._2vK84')  # 아니 태그가 그세 바뀌네ㅡ,.ㅡ
                    for i in store_time_list:
                        store_time = i.find_element(By.CSS_SELECTOR,'._3uEtO > time').text
                except:
                    pass
                print(store_time)

                # -----메뉴-----
                try:
                    menu_list = driver.find_elements(By.CSS_SELECTOR,'._1XxR5')
                    menu_name = []  # 메뉴이름
                    menu_price = []  # 메뉴가격

                    for i in menu_list:
                        name = i.find_element(By.CSS_SELECTOR,'._1q3GD').text
                        menu_name.append(name)

                        price = i.find_element(By.CSS_SELECTOR,'._3IAAc').text  # 텍스트를 넣을 변수 생성
                        price = re.sub('원\d{2},\d{3}', '', price)  # 할인 전 가격 제거  # 재정의
                        menu_price.append(price)  # 추가

                except:
                    pass

                # -----메뉴2 (다른 태그의 메뉴)-----
                try:
                    menu_list_two = driver.find_elements(By.CSS_SELECTOR,'._20R25')
                    menu_name_two = []
                    menu_price_two = []

                    for i in menu_list_two:
                        name_two = i.find_element(By.CSS_SELECTOR,'._2E0Gk').text
                        name_two = re.sub('\n사진|\n대표', '', name_two)

                        price_two = i.find_element(By.CSS_SELECTOR,'._3GJcI').text

                        menu_name_two.append(name_two)
                        menu_price_two.append(price_two)

                except:
                    pass

                # 메뉴 리스트 합체
                menus = menu_name + menu_name_two
                prices = menu_price + menu_price_two

                print(menus)
                print(prices)
                # -----키워드 리뷰 가져오기-----
                try:
                    keyword_list = driver.find_element(By.CSS_SELECTOR,'._28hFN')  # 키워드가 담긴 리스트 클릭
                    keyword_list.click()

                except:  # 키워드리뷰 없으면 다음 음식점으로
                    print('키워드리뷰 없음 >>> 다음으로',)
                    switch_frame('searchIframe')
                    continue

                try:
                    keyword_review_list = driver.find_elements(By.CSS_SELECTOR,'._3FaRE')  # 리뷰 리스트
                    kwd_title = []
                    kwd_count = []
                    sleep(2)

                    for i in keyword_review_list:
                        keyword_title = i.find_element(By.CSS_SELECTOR,'._1lntw').text  # 키워드리뷰
                        keyword_count = i.find_element(By.CSS_SELECTOR,'.Nqp-s').text   # 리뷰를 선택한 수

                        # db에 넣을 때 편의를 위해 요청하였음
                        title_re = re.sub('"', '', keyword_title) \
                            .replace('양이 많아요', '1').replace('음식이 맛있어요', '2').replace('재료가 신선해요', '3') \
                            .replace('가성비가 좋아요', '4').replace('특별한 메뉴가 있어요', '5').replace('화장실이 깨끗해요', '6') \
                            .replace('주차하기 편해요', '7').replace('친절해요', '8').replace('특별한 날 가기 좋아요', '9').replace(
                            '매장이 청결해요',
                            '10') \
                            .replace('인테리어가 멋져요', '11').replace('단체모임 하기 좋아요', '12').replace('뷰가 좋아요', '13').replace(
                            '매장이 넓어요',
                            '14') \
                            .replace('혼밥하기 좋아요', '15')

                        title_num = list(map(str, range(1, 16)))  # 1~15만 리스트에추가 (이외에 다른 키워드들은 추가하지않음)
                        count_keyword = re.sub('이 키워드를 선택한 인원\n', '', keyword_count)
                        if title_re in title_num:
                            kwd_title.append(title_re)
                            kwd_count.append(count_keyword)
                        else:
                            pass
                except:
                    pass
                kwd_count = list(map(int, kwd_count))  # int 형변환

                print(kwd_title)
                print(kwd_count)

                # -----썸네일 사진 주소-----
                try:
                    thumb_list = driver.find_element(By.CSS_SELECTOR,'.cb7hz') \
                        .value_of_css_property('background-image')  # css 속성명을 찾는다
                    store_thumb = re.sub('url|"|\)|\(', '', thumb_list)  # url , (" ") 제거
                except:
                    pass
                print(store_thumb)

                # ---- dict에 데이터 집어넣기----
                dict_temp = {
                    'name': store_name,
                    'tel': store_tel,
                    'star': store_rating,
                    'addr': store_addr,
                    'time': store_time,
                    'menu': menus,
                    'price': prices,
                    'kwd': kwd_title,
                    'kwd_count': kwd_count,
                    'thumb': store_thumb
                }

                store_dict['매장정보'].append(dict_temp)

                print(f'{store_name} ...완료')
                switch_frame('searchIframe')
                sleep(1)

            except:
                print('ERROR!' * 3)

        # 다음 페이지 버튼
        if page[-1]:  # 마지막 매장일 경우 다음버튼 클릭
            next_btn[-1].click()
            sleep(2)
        else:
            print('페이지 인식 못함')
            break

    print('[데이터 수집 완료]\n소요 시간 :', time.time() - start)
    driver.quit()  # 작업이 끝나면 창을닫는다.

    # json 파일로 저장
    with open(f'data/{gu}_store_data.json', 'w', encoding='utf-8') as f:
        json.dump(store_dict, f, indent=4, ensure_ascii=False)