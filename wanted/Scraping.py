from selenium import webdriver
from selenium.webdriver.common.by import By


driver = webdriver.Chrome()
# driver.get('https://www.wanted.co.kr/wdlist/518?country=kr&job_sort=company.response_rate_order&years=0&skill_tags=1554&selected=1634&selected=1024&selected=655&selected=899&selected=1025&locations=seoul.all')
driver.get('https://www.wanted.co.kr/wd/142384')
company_name = driver.find_element(By.CLASS_NAME,'JobHeader_className__HttDA').find_element(By.TAG_NAME,'a') #기업 이름
job_name = driver.find_element(By.CLASS_NAME,'JobHeader_className__HttDA').find_element(By.TAG_NAME,'h2') # 채용직군 이름
job_description = driver.find_element(By.XPATH,'//*[@id="__next"]/div[3]/div[1]/div[1]/div[1]/div[2]/section/p[2]/span') # 주요 업무
requirements = driver.find_element(By.XPATH,'//*[@id="__next"]/div[3]/div[1]/div[1]/div/div[2]/section/p[3]/span') # 자격요건
option = driver.find_element(By.XPATH,'//*[@id="__next"]/div[3]/div[1]/div[1]/div/div[2]/section/p[4]/span') # 자격요건
skill= driver.find_element(By.XPATH,'//*[@id="__next"]/div[3]/div[1]/div[1]/div/div[2]/section/p[6]/div') # skill

print(company_name.text,job_name.text)
print(job_description.text,requirements.text,option.text)
print(skill.text)
