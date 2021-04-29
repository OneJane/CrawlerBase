import hashlib
import json
import time

import requests

# coding: utf-8
import json
import random

import pymongo
import requests
from fake_useragent import UserAgent
from selenium.webdriver import Chrome, ActionChains
import time
from selenium.webdriver.chrome.options import Options

COOKIES_FILE_PATH = 'cookies.txt'


# mongoexport -h localhost:27017 -d jddmoto -c income_rate  -o income_rate.json --type json
class AlimamaIncomeRate:

    def __init__(self, session, browser):

        # 起始共用的浏览器登录查找都在这里操作
        self.cookies = ""
        self.session = session
        self.browser = browser
        self.client = pymongo.MongoClient(host='127.0.0.1', port=27017)
        self.alimama_collection = self.client["jddmoto"]["income_rate"]
        self.url_collection = self.client["jddmoto"]["income_rate_url"]
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"
        self.headers = {
            'user-agent': self.ua,
            'cookie': self.cookies
        }
        self.adnet_login_url = 'https://sso.e.qq.com/login/hub?sso_redirect_uri=https%3A%2F%2Fe.qq.com%2Fdev%2Flogin&service_tag=14'
        self.get_date_url = 'https://adnet.qq.com/eros/report/report_table_data'
        self.data = {"start_date": "2021-04-10", "end_date": "2021-04-28",
                "biz_filter": {"medium": [], "placement_type": [], "placement": []}, "group_by": ["report_day"],
                "order_by": "", "page": 1, "page_size": 100}

    def save_cookies(self):
        self.browser.implicitly_wait(10)
        self.browser.maximize_window()
        self.browser.find_element_by_xpath('//a[@id="qqLogin"]').click()
        # el_frame = self.browser.find_element_by_xpath('//*[@id="qqLoginFrame"]')
        # print(self.browser.page_source)
        self.browser.switch_to.frame('qqLoginFrame')
        self.browser.switch_to.frame('ptlogin_iframe')
        time.sleep(5)
        self.browser.find_element_by_xpath('//a[contains(text(),"帐号密码登录")]').click()
        self.browser.find_element_by_xpath('//*[@id="u"]').send_keys('*')
        self.browser.find_element_by_xpath('//*[@id="p"]').send_keys('*')
        self.browser.find_element_by_xpath('//*[@id="loginform"]/div[@class="submit"]/a').click()
        time.sleep(5)
        self.cookies = '; '.join(
            item for item in [item["name"] + "=" + item["value"] for item in self.browser.get_cookies()])
        with open(COOKIES_FILE_PATH, 'w', encoding='utf-8') as file:
            file.write(self.cookies)
            print("cookie写入成功：", self.cookies)

    def adnet_login(self):
        print("登录中。。。。。")
        ok = False
        while not ok:
            with open(COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
                self.headers["cookie"] = file.read()
            response = self.session.post(self.get_date_url, data=json.dumps(self.data), headers=self.headers, verify=False)
            try:
                res = json.loads(response.text)
                ok = True
            except:
                self.browser.get(self.adnet_login_url)
                self.browser.delete_all_cookies()
                self.save_cookies()
            self.browser.close()
            self.browser.quit()

    def get_report_list(self):
        # 获取所有shop plan
        while True:
            try:
                response = self.session.post(self.get_date_url, data=json.dumps(self.data), headers=self.headers, verify=False)
                print(json.loads(response.text)["data"]["list"])
                response.raise_for_status()
            except Exception as e:
                print('获取优量汇主页请求失败！')
                self.adnet_login()
                raise e


if __name__ == '__main__':
    session = requests.session()
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')
    # 屏蔽'CHROME正受到组件控制'的提示
    chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # 屏蔽保存密码
    prefs = {"": ""}
    prefs["credentials_enable_service"] = False
    prefs["profile.password_manager_enabled"] = False
    chrome_options.add_experimental_option("prefs", prefs)
    driver = Chrome('./chromedriver', options=chrome_options)
    driver.set_page_load_timeout(10)
    with open('./stealth.min.js') as f:
        js = f.read()

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": js
    })

    alimama = AlimamaIncomeRate(session, driver)
    alimama.adnet_login()
    alimama.get_report_list()
