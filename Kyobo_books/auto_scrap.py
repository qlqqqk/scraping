from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse,parse_qsl,urlunparse,urlencode,quote
from datetime import datetime
import time, argparse
import pandas as pd
import shutil
from openpyxl import load_workbook
'''
user-agent 필요시 http://m.avalon.co.kr/check.html
'''

# parser = argparse.ArgumentParser(description='Default는 가장 최근 신간을 기준으로 진행됩니다.')
# parser.add_argument('')

# #특정 시기 신작 목록이 필요할때
year = 2023
month = '05'
week = 1
page = 1
default_url = f'https://product.kyobobook.co.kr/new/#?page={page}&sort=new&year={year}&month={month}&week={week}&per=20&saleCmdtDvsnCode=KOR&gubun=newGubun&saleCmdtClstCode='
opt = webdriver.ChromeOptions()
opt.add_argument('headless')
driver = webdriver.Chrome(chrome_options=opt)
driver.implicitly_wait(20)
# default_url = 'https://product.kyobobook.co.kr/new'
driver.get(default_url)

#page num list create
num = driver.find_element(By.CLASS_NAME,'page_num').text
splitnum = num.split()
num_str = list(str(int(splitnum[1])))
num_str.insert(0,splitnum[0]) #첫 페이지는 디폴트
num_str.append(splitnum[-1])
numbers = list(map(int,num_str))

url_list = []
for n in numbers:
    url = driver.current_url
    q = urlparse(url,allow_fragments=False).query
    unpack = dict(parse_qsl(q))
    unpack['page'] = n
    ch_url = 'https://product.kyobobook.co.kr/new#?'+urlencode(unpack)

    driver.get(ch_url)
    WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,'prod_list')))
    time.sleep(2)
                                   
    for item in driver.find_element(By.CLASS_NAME,'prod_list').find_elements(By.CLASS_NAME,'prod_item'):
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.TAG_NAME,'a')))
        url = item.find_element(By.CLASS_NAME,'prod_area.horizontal').find_element(By.CLASS_NAME,'prod_thumb_box.size_lg').find_element(By.TAG_NAME,'a').get_attribute('href')
        url_list.append(url) # 각 페이지마다 url 수집


print(len(url_list))

#수집된 전체 url을 토대로 데이터 스크랩


def book_scan(url):
    driver.get(url)
    book_name = driver.find_element(By.CLASS_NAME,'prod_title_box.auto_overflow_wrap').text
    ISBN = driver.find_element(By.CLASS_NAME,'tbl_row_wrap').find_element(By.TAG_NAME,'td').text

    keyword_lst = []
    for i in driver.find_element(By.CLASS_NAME,'prod_author_box.auto_overflow_wrap').find_elements(By.TAG_NAME,'a'):
        print(i.text)
        keyword_lst.append(i.text)
    keyword = ','.join(keyword_lst)

    maker = driver.find_element(By.CLASS_NAME,'prod_info_text.publish_date').find_element(By.TAG_NAME,'a').text
    date = driver.find_element(By.CLASS_NAME,'tbl_row_wrap').find_elements(By.TAG_NAME,'td')[1].get_attribute('innerHTML')
    date = ' '.join(date.split()[:3])
    d = datetime.strptime(date,'%Y년 %m월 %d일')
    make_date = d.strftime('%Y%m%d')
    add_info = '저자^|^'+driver.find_element(By.CLASS_NAME,'prod_author_box.auto_overflow_wrap').text
    goods_price = driver.find_element(By.CLASS_NAME,'prod_price_box').text.split()[1][:-1].replace(',','')
    fixed_price = driver.find_element(By.CLASS_NAME,'prod_price_box').text.split()[2][:-1].replace(',','')

    img_store = 'https://jigoobooks.smilecast.co.kr/Book_cover_sqr/'
    # try: #img None error
    #     main_img = driver.find_element(By.CLASS_NAME,'portrait_img_box.portrait').find_element(By.TAG_NAME,'img').get_attribute('src')
    # except:
    #     main_img = driver.find_element(By.CLASS_NAME,'blur_img_box').find_element(By.TAG_NAME,'img').get_attribute('src')
    try:
        main_img = driver.find_element(By.CLASS_NAME,'col_prod_info.thumb').find_element(By.TAG_NAME,'img').get_attribute('src')
    except:
        main_img = ''
    main_img = img_store+main_img.split('/')[-1]
    main = f'''main^|^{main_img}
    list^|^{main_img}
    detail^|^{main_img}
    magnify^|^{main_img}
    '''


    def recombination(classname): #html 구성
        try:    
            main = driver.find_element(By.CLASS_NAME,classname)
            h2 = main.find_element(By.CLASS_NAME,'title_heading').get_attribute('outerHTML')
            contents = main.find_element(By.CLASS_NAME,'auto_overflow_inner').get_attribute('outerHTML')
            return h2 + '\n' + contents
        except:
            return ''

    try:
        detail_img = driver.find_element(By.CLASS_NAME,'product_detail_area.detail_img').get_attribute('outerHTML')
    except:
        detail_img = ''
    contents_lst = recombination('product_detail_area.book_contents')
    pub_review = recombination('product_detail_area.book_publish_review')

    detail_page = [detail_img,contents_lst,pub_review]
    style = '<style>ul{list-style:none;padding-left:0px;}</style>'
    goods_desc = '<html>'+ style + '\n'.join(detail_page)+'</html>'
    
    return [book_name,ISBN,keyword,maker,'한국',make_date,make_date,add_info,'f',goods_price,fixed_price,img_store,main,goods_desc,goods_desc,ISBN,book_name]

t = ''.join([unpack['year']+'년',unpack['month']+'월',unpack['week']+'주차'])
ori = '신간주문_고도몰_default.xlsx'
copy = f'신간주문_고도몰_{t}.xlsx'
df = pd.read_excel(ori)
c = load_workbook(ori)
c.save(copy)
c.close()


for idx,url in enumerate(url_list):
    print(url)
    data = book_scan(url)
    add_col =['상품명_기본','자체상품코드','검색,키워드','제조사','원산지','제조일','출시일','추가항목','과세/면세','판매가','정가','이미지 저장소','이미지명','PC쇼핑몰 상세 설명','모바일쇼핑몰 상세 설명','ISBN코드','타이틀']
    df.loc[2+idx,add_col] = data

with pd.ExcelWriter(copy,mode='a',engine='openpyxl',if_sheet_exists='overlay') as w:
    df[2:].to_excel(w,header=False,index=False,startrow=3)

    