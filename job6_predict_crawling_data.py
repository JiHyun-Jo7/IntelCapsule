from selenium import webdriver              # 웹사이트(및 웹 애플리케이션)의 유효성 검사에 사용되는 자동화 테스트 프레임워크
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
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

category = ['bladder','bone-joint-cartilage','brain-cognitive','colon','common-cold-flu','digestive-support','energy','heart','immune-support']
category_kr = ['방광','뼈 관절 연골','두뇌 인지','장건강','감기독감','소화기계','에너지','심혈관계','면역계']
# pages = [14, 13, 14, 16, 8, 16]  # 각 카테고리 별 총 페이지 수 # 학습을 위해 최대 페이지를 중간 값인 13 페이지로 제한함
df_titles = pd.DataFrame()

for i in range(len(category)):
    # 카테고리 변경
    section_url = 'https://kr.iherb.com/c/{}?p=20'.format(category[i])
    titles = []  # titles 초기화
    driver.get(section_url)
    time.sleep(2)

    for j in range(20,25):
        try:
            xpath_temp = '/html/body/div[7]/div/div[3]/div/div/div[1]/div[1]/div[2]/div[2]/div[{}]/div/div[2]/div[1]/a'.format(j)
            driver.find_element('xpath', xpath_temp).click()  # 클릭 시 사이트로 이동
            time.sleep(3)  # 클릭 후 사이트로 이동할 대기 시간 부여
            print('count = %d' %j)

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
            print(dt)
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

            driver.back()  # 사이트 뒤로 가기
            time.sleep(2)  # 이전 사이트로 이동할 대기 시간 부여

        except:
            # 오류가 발생할 경우 error + 카테고리, 페이지, 제품 번호 출력
            print('error c.{} product.{}'.format(i, j))

    df_section_title = pd.DataFrame(titles, columns=['effect'])
    df_section_title['category'] = category_kr[i]
    df_titles = pd.concat([df_titles, df_section_title], ignore_index=True)

    # crawling 폴더에 Nutrients_(카테고리)_(년월일).cvs 파일로 저장
df_titles.to_csv('./crawling_data/predict.csv',index=False)

# print(df_titles.head(20))  # 상위 제목 20개 출력
df_titles.info()
# print(df_titles['category'].value_counts())
