import os
import time
import re
import chromedriver_autoinstaller
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

class KakaoMapCollection:
    def __init__(self, gu_lst):
        self.default_url = 'https://map.kakao.com/'
        self.driver = None
        self.gu_lst = gu_lst
        self._DataFrameColumns = ["맛집명", "주소", "영업시간", "전화번호", "총합평점", "업종", "유저이름", "평점", "리뷰"]
        self._DefaultDataFrame = pd.DataFrame(columns = self._DataFrameColumns)

    def DriverSettings(self, linux_mode = False):
        chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]  #크롬드라이버 버전 확인
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--incognito") # 시크릿 모드
        if linux_mode == True: chrome_options.add_argument("--headless") # 리눅스 GUI 없는 디스플레이 모드
        chrome_options.add_argument("--no-sandbox") # 리소스에 대한 엑서스 방지
        chrome_options.add_argument("--disable-setuid-sandbox") # 크롬 충돌 방지
        chrome_options.add_argument("--disable-dev-shm-usage") # 메모리 부족 에러 방지
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try: # 크롬 드라이버
            self.driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver', chrome_options=chrome_options)   
        except:
            chromedriver_autoinstaller.install(True)
            self.driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver', chrome_options=chrome_options)
        # WebDruverException Error 방지 기존의 드라이버 버젼으로 지정
        # driver = webdriver.Chrome(executable_path='/Users/cmblir/Python/Musinsa-Analysis/100/chromedriver')

    def ClickMoreReview(self):
        while True:
            EvaluationReview = self.driver.find_element(By.CLASS_NAME, "evaluation_review")
            temp = EvaluationReview.find_element(By.CLASS_NAME, "link_more")
            temp_text = temp.text
            if temp_text == "후기 접기":
                break
            action = webdriver.ActionChains(self.driver)
            action.move_to_element(temp).perform()
            temp.send_keys("\n")

    def GetReviewData(self):
        self.driver.implicitly_wait(6)
        self.ClickMoreReview()
        t1 = self.driver.page_source
        t2 = BeautifulSoup(t1, "html.parser")
        t3 = t2.find(name="div", attrs={"class":"evaluation_review"})
        star= t3.find_all('span',{'class':'ico_star inner_star'})
        self.user_name = [i.text for i in t3.find_all("a", {"class" : "link_user"})]
        self.user_review = [i.text.replace("더보기", "") for i in t3.find_all('p',{'class':'txt_comment'})]
        self.more_user_reviews = [i.text.replace("더보기", "") for i in t3.find_all('p',{'class':'txt_comment txt_fold'})]
        self.user_rating = []
        for point in star:
            point = str(point['style']).replace("width:","")
            if point == "20%;": self.user_rating.append(1)
            elif point == "40%;": self.user_rating.append(2)
            elif point == "60%;": self.user_rating.append(3)
            elif point == "80%;": self.user_rating.append(4)
            elif point == "100%;": self.user_rating.append(5)

    def AppendDataFrame(self):
        for user_name, user_rating, user_review in zip(self.user_name, self.user_rating, self.user_review):
            AppendDict = {"맛집명" : self.place_name,
                          "주소" : self.place_address,
                          "영업시간" : self.place_time,
                          "전화번호" : self.place_tel,
                          "총합평점" : self.place_rating,
                          "업종" : self.place_sub_category,
                          "유저이름" : user_name,
                          "평점" : user_rating,
                          "리뷰" : user_review}
            AppendDataFrame = pd.DataFrame(AppendDict, index=[0])
            self._DefaultDataFrame = self._DefaultDataFrame.append(AppendDataFrame, ignore_index = True)

    def GetData(self, place_lists):
        for p in place_lists: # WebElement
            store_html = p.get_attribute('innerHTML')
            store_info = BeautifulSoup(store_html, "html.parser")
            self.place_name = store_info.select('.head_item > .tit_name > .link_name')
            if len(self.place_name) == 0:
                continue # 광고
            self.place_name = store_info.select('.head_item > .tit_name > .link_name')[0].text
            self.place_address = store_info.select('.info_item > .addr > p')[0].text
            self.place_time = store_info.select('.info_item > .openhour > p > a')[0].text
            self.place_tel = store_info.select('.info_item > .contact > span')[0].text
            try: self.place_rating = store_info.select('.rating > .score > .num')[0].text
            except : self.place_rating = "0"
            self.place_sub_category = store_info.select('.head_item > .subcategory')[0].text
            detail_link = p.find_element(By.CSS_SELECTOR, 'div.info_item > div.contact > a.moreview').get_attribute("href")
            self.driver.get(detail_link)
            try:
                self.GetReviewData()
                self.AppendDataFrame()
            except:
                pass
            self.driver.back()

    def StartCrawling(self):
        for gu_name in tqdm(self.gu_lst):
            self.driver.implicitly_wait(10) # 10초정도 멈추기
            self.driver.get(self.default_url)  # 주소 가져오기
            search_area = self.driver.find_element(By.XPATH, '//*[@id="search.keyword.query"]') # 검색 창
            search_area.send_keys(gu_name + ' 맛집')  # 검색어 입력
            self.driver.find_element(By.XPATH, '//*[@id="search.keyword.submit"]').send_keys(Keys.ENTER)  # Enter로 검색
            self.driver.implicitly_wait(3) # 기다려 주자
            more_page = self.driver.find_element(By.ID, "info.search.place.more")
            # more_page.click()
            more_page.send_keys(Keys.ENTER) # 더보기 누르고
            # 첫 번째 검색 페이지 끝
            # driver.implicitly_wait(5) # 기다려 주자
            time.sleep(1)

            # next 사용 가능?
            next_btn = self.driver.find_element(By.ID, "info.search.page.next")
            has_next = "disabled" not in next_btn.get_attribute("class").split(" ")
            Page = 1
            
            while has_next: # 다음 페이지가 있으면 loop
                time.sleep(1)
                # place_lists = driver.find_element(By.CSS_SELECTOR, ('#info\.search\.place\.list > li:nth-child(1)')
                # 페이지 루프
                #info\.search\.page\.no1 ~ .no5
                page_links = self.driver.find_elements(By.CSS_SELECTOR, "#info\.search\.page a")
                pages = [link for link in page_links if "HIDDEN" not in link.get_attribute("class").split(" ")]
                # print(len(pages), "개의 페이지 있음")
                # pages를 하나씩 클릭하면서
                for i in range(1, 6):
                    xPath = '//*[@id="info.search.page.no' + str(i) + '"]'
                    try:
                        page = self.driver.find_element(By.XPATH, xPath)
                        page.send_keys(Keys.ENTER)
                    except ElementNotInteractableException:
                        print('End of Page')
                        break;
                    sleep(3)
                    place_lists = self.driver.find_elements(By.CSS_SELECTOR, '#info\.search\.place\.list > li')
                    self.GetData(place_lists)

                    print(i, ' of', ' [ ' , Page, ' ] ')
                next_btn = self.driver.find_element(By.ID, "info.search.page.next")
                has_next = "disabled" not in next_btn.get_attribute("class").split(" ")
                if not has_next:
                    print('Arrow is Disabled')
                    self.driver.close()
                    break # 다음 페이지 없으니까 종료
                else: # 다음 페이지 있으면
                    Page += 1
                    next_btn.send_keys(Keys.ENTER)
            print("End of Crawl")

gu_list = ['마포구','서대문구','은평구','종로구','중구','용산구','성동구','광진구',
           '동대문구','성북구','강북구','도봉구','노원구','중랑구','강동구','송파구',
           '강남구','서초구','관악구','동작구','영등포구','금천구','구로구','양천구','강서구']