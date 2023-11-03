from selenium import webdriver  # 웹사이트(및 웹 애플리케이션)의 유효성 검사에 사용되는 자동화 테스트 프레임워크
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import re
import time
import datetime

url = 'https://kr.iherb.com/'
options = ChromeOptions()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
options.add_argument('user-agent=' + user_agent)
options.add_argument('lang=ko_KR')

# 크롬 드라이버 최신 버전 설정
service = ChromeService(executble_path=ChromeDriverManager().install())
# 크롬 드라이버
driver = webdriver.Chrome(service=service, options=options)
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}

category = ['seasonal-allergies', 'sleep', 'weight-loss', 'childrens-health', 'mens-health', 'womens-health']
category_kr = ['계절성 알레르기', '불면증', '체중 조절', '어린이 건강', '남성 건강', '여성 건강']
# pages = [14, 13, 14, 16, 8, 16]  # 각 카테고리 별 총 페이지 수
pages = [13, 13, 13, 13, 8, 13]  # 학습을 위해 최대 페이지를 중간 값인 13 페이지로 제한함
df_titles = pd.DataFrame()

for i in range(6):
    # 카테고리 변경
    df_titles = pd.DataFrame()
    titles = []  # titles 초기화
    product_names = []
    for j in range(1, pages[i]+1):
        section_url = url + 'c/{}?p={}'.format(category[i], j)  # 페이지 변경
        driver.get(section_url)
        time.sleep(3)
        if i == 0 and j == 1:
            driver.find_element(By.XPATH, '//*[@id="truste-consent-button"]').click()
            print('cookie access')

        product = driver.find_elements(By.CLASS_NAME, 'product-cell-container')
        product = len(product)  # 제품 수 만큼 for 문 반복 (마지막 페이지 제품 수가 48개 미만)

        response = requests.get(section_url, headers=headers)
        response.raise_for_status()
        soup = bs(response.text, 'html.parser')

        product_url = []
        for z in soup.find_all('div', {'class': 'absolute-link-wrapper'}):
            for y in z.find_all({'a'}):
                if y.get('href') is not None:
                    product_url.append(y.get('href'))
        del product_url[0]
        time.sleep(2)
        for k in range(0, product):
            try:
                driver.get(product_url[k])
                product_name = driver.find_element(By.XPATH, '//*[@id="name"]')
                product_names.append(product_name)
                # 상품 설명 전체 크롤링
                # nutrient_data = driver.find_element('xpath',
                #                                     '/html/body/div[8]/article/div[2]/div/section/div[2]/div/div/div[1]/div[1]/div/div').text
                # 제품 설명 전처리 (한글, 영어(대,소문자), 숫자만 수집. 그 외는 공백 처리)
                # nutrient_data = re.compile('[^가-힣|a-z|A-Z|0-9]').sub(' ', nutrient_data)
                # titles.append(nutrient_data)

                # 상품 설명 요약 크롤링
                dt = ''
                nutrient_data = driver.find_elements(By.XPATH, '//div[@itemprop="description"]/ul')
                for data in nutrient_data:
                    if not data.text == '':
                        data = re.compile('[^가-힣|a-z|A-Z|0-9]').sub(' ', data.text)
                        dt += data
                titles.append(dt)

                # 상품 설명 크롤링
                # dt = ''
                # nutrient_data = driver.find_elements(By.XPATH, '//div[@itemprop="description"]/p')
                # if not nutrient_data == '':
                #     for data in nutrient_data:
                #         if not data.text == '':
                #             data = re.compile('[^가-힣|a-z|A-Z|0-9]').sub(' ', data.text)
                #             dt += data
                #     print(dt)
                #     titles.append(dt)

            except:
                # 오류가 발생할 경우 error + 카테고리, 페이지, 제품 번호 출력
                print('error c.{} p.{} p.{}'.format(category[i], j, k))

    df_section_title = pd.DataFrame({titles: 'effect'},{product_names: 'name'})
    df_section_title['category'] = category_kr[i]
    df_titles = pd.concat([df_titles, df_section_title], ignore_index=True)

    # crawling 폴더에 Nutrients_(카테고리)_(년월일).cvs 파일로 저장
    df_titles.to_csv(
        './crawling_data/nutrients_{}_{}.csv'.format(category[i], datetime.datetime.now().strftime('%Y%m%d')),
        index=False)

# print(df_titles.head(20))  # 상위 제목 20개 출력
df_titles.info()
# print(df_titles['category'].value_counts())
