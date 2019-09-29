from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options 
import time
import re
from tkinter import tkinter.messagebox
from tkinter import simpledialog 
import tkinter
from datetime import date

#setting up the env
opts = Options()
browser = Chrome(options=opts)
browser.get('https://mywipro.wipro.com')
time.sleep(2)

#opening the login page and filling the username and password
username = browser.find_element_by_xpath('//*[@id="i0116"]')
username.send_keys('SA40036603@wipro.com')
submit = browser.find_element_by_id('idSIButton9')
submit.click()
time.sleep(2) #sleep so that page can load fully
password = browser.find_element_by_id('i0118')
password.send_keys('feb@1998')
submit = browser.find_element_by_id('idSIButton9')
submit.click()
time.sleep(2) #sleep so that page can load fully

#GUI to ask for the otp

#opening the timesheet page #TODO scroll down a little bit 
timesheet = browser.find_element_by_xpath('/html/body/app-root/div/app-landing/div[1]/div/app-home/section/div[1]/div/div/div[2]/ul/li[3]')
timesheet.click()
time.sleep(8) #sleep so that page can load fully

#finding todays date
subprcs = str(subprocess.run(['date','|','cut','-f3','-d\"\\ \"'], capture_output=True)) #from datetime import date; date.today()
pattern = re.compile(r'\d\d')
today_date = pattern.search(subprcs)
today_date = int(today_date.group())

#finding the date col by col in the timesheet page 
#move to the iframe where the element resides
iframe = browser.find_element_by_xpath('/html/body/app-root/div/app-my-app/iframe')
browser.switch_to.frame(iframe)
timesheet = browser.find_element_by_xpath('//*[@id="app"]/div/div[16]/div[2]/div/div/div[1]/div[2]/div/div[1]/div/button')
found_day = timesheet.text
pattern_1 = re.compile(r'\d\d')
found_date = pattern_1.search(found_day)
found_date = int(found_date.group())

#finding the time on floor
time_on_floor_row = browser.find_element_by_xpath('//*[@id="app"]/div/div[16]/div[2]/div/div/div[1]/div[2]/div/div[2]/div/span[2]')
time_on_floor = time_on_floor_row.text
#TODO finding the time on floor eg 10.5, 9.50

#finding the right field to enter the value 
clsrm_traing = browser.find_element_by_xpath('//*[@id="0_3_nonproj"]')
clsrm_traing.send_keys(time_on_floor)




