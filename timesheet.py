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
browser.get('')
time.sleep(2)

#opening the login page and filling the username and password
username = browser.find_element_by_xpath('')
username.send_keys('')
submit = browser.find_element_by_id('')
submit.click()
time.sleep(2) #sleep so that page can load fully
password = browser.find_element_by_id('')
password.send_keys('')
submit = browser.find_element_by_id('')
submit.click()
time.sleep(2) #sleep so that page can load fully

#GUI to ask for the otp

#opening the timesheet page #TODO scroll down a little bit 
timesheet = browser.find_element_by_xpath('')
timesheet.click()
time.sleep(8) #sleep so that page can load fully

#finding todays date
subprcs = str(subprocess.run(['date','|','cut','-f3','-d\"\\ \"'], capture_output=True)) #from datetime import date; date.today()
pattern = re.compile(r'\d\d')
today_date = pattern.search(subprcs)
today_date = int(today_date.group())

#finding the date col by col in the timesheet page 
#move to the iframe where the element resides
iframe = browser.find_element_by_xpath('')
browser.switch_to.frame(iframe)
timesheet = browser.find_element_by_xpath('')
found_day = timesheet.text
pattern_1 = re.compile(r'\d\d')
found_date = pattern_1.search(found_day)
found_date = int(found_date.group())

#finding the time on floor
time_on_floor_row = browser.find_element_by_xpath('')
time_on_floor = time_on_floor_row.text
#TODO finding the time on floor eg 10.5, 9.50

#finding the right field to enter the value 
clsrm_traing = browser.find_element_by_xpath('')
clsrm_traing.send_keys(time_on_floor)




