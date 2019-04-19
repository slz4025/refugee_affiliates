# https://blog.henrypoon.com/blog/2017/06/18/running-selenium-webdriver-on-bash-for-windows/
import time

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import pandas as pd
pd.options.mode.chained_assignment = None # turn off warning

def execute_with_retry(method, max_attempts):
    e = None
    for i in range(0, max_attempts):
        try:
            return method()
        except Exception as e:
            print(e)
            time.sleep(1)
    if e is not None:
        raise e

def interact(region, state, place, trial):
    ele = browser.find_element_by_css_selector("#topban input")
    ele.clear()
    if trial == 0:
        ele.send_keys(place)
    if trial == 1:
        ele.send_keys(region)

    wait = WebDriverWait(browser, 1.5) # wait 0.25 seconds
    result = ""
    url = ""
    try:
        wait.until(EC.element_to_be_clickable((By.ID, 'ui-id-2')))
        options = browser.find_elements_by_xpath(".//ul[@id='ui-id-2']/li/a") 
        found = False
        for i in range(len(options)):
            o = options[i]
            text = o.get_attribute("innerText")
            if trial == 0:
                cond = place == text
            if trial == 1:
                t_raw = text.split(', ')
                cond = t_raw[1] == state and t_raw[0].startswith(region)
            if cond:
                found = o
                result = text
                break
            else:
                ele.send_keys(Keys.ARROW_DOWN) # move to next option
        if found:
            found.click()
            url = browser.current_url
        else:
            result = "no match"
            url = ""
    except:
        result = "no result"
        url = ""

    return result, url

capabilities = DesiredCapabilities.FIREFOX
capabilities["marionette"] = True
firefox_bin = "/usr/bin/firefox"
browser = execute_with_retry(lambda: webdriver.Firefox(
    firefox_binary=firefox_bin, capabilities=capabilities), 10)

locs = pd.read_csv("popfiltered.csv") #"locations.csv")
abbr = pd.read_csv("state_abbr.csv")
abbr = pd.Series(abbr.Abbreviation.values,index=abbr.State).to_dict()

# base url
base = "https://miami.craigslist.org/?search_distance=3.6&postal=33141"
browser.get(base)
breakers = ["CDP", "city", "town", "City", "village", "County", "urban",
        "county", "municipality", "borough"]

buffer_am = 70
inner_num = buffer_am
raw_number = locs['p_GEO.id2'].count()
number = int(raw_number / buffer_am)
for it in range(number + 1):
    state_buf = []
    abbr_buf = []
    region_buf = []
    result_buf = []
    url_buf = []
    if it == number:
        url_get = locs.iloc[buffer_am * it :]
        inner_num = raw_number - buffer_am * it # no need to change after
    else:
        url_get = locs.iloc[buffer_am * it : buffer_am * (it + 1)]
    for j in range(inner_num):
        label = url_get.iloc[j]['p_GEO.display-label']
        if ";" in label:
            raw = label.split('; ')
            region_raw = raw[0].split(' ')
            region = raw[0][0] # just take first
            full_state = raw[1]
            state = abbr[full_state]
        else:
            raw = label.split(', ')
            region_raw = raw[0].split(' ')
            region = ""
            for rr in region_raw:
                if rr in breakers:
                    break
                region += rr + " "
            region = region[:-1] # take out last space
            full_state = raw[1]
            state = abbr[full_state]

        place = region + ", " + state
        # reset
        browser.get(base)
        ele = browser.find_element_by_css_selector("#topban")
        browser.execute_script("arguments[0].setAttribute('class','enter')", ele)

        result, url = interact(region, state, place, 0)
        if url == "":
            result, url = interact(region, state, place, 1)

        state_buf.append(full_state)
        abbr_buf.append(state)
        region_buf.append(region)
        result_buf.append(result)
        url_buf.append(url)

    url_get['state'] = state_buf
    url_get['abbr'] = abbr_buf
    url_get['region'] = region_buf
    url_get['result'] = result_buf
    url_get['url'] = url_buf
    if it == 0: # first save
        with open('urls.csv', 'w') as f:
            url_get.to_csv(f, header=True)
    else:
        with open('urls.csv', 'a') as f:
            url_get.to_csv(f, header=False)
    time.sleep(10) # give it some time to cool off

browser.close()
