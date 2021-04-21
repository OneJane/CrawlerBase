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
        self.alimama_login_url = 'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&from=alimama'
        self.shop_plan_url = 'https://pub.alimama.com/campaign/joinedSpecialCampaigns.json?toPage=1&status=2&perPageSize=40'
        self.item_url = 'https://pub.alimama.com/openapi/param2/1/gateway.unionpub/mkt.commission.itemList.json?&pageNo={}&pageSize=20&campaignId={}&sellerId={}&shopKeeperId={}&productTypes=%5B19%5D&publicRanges=%5B3%5D'

    def save_cookies(self):
        self.browser.implicitly_wait(10)
        self.browser.maximize_window()
        self.browser.find_element_by_xpath('//input[@name="fm-login-id"]').send_keys('***')
        self.browser.find_element_by_xpath('//input[@name="fm-login-password"]').send_keys('***')
        # 解决滑块
        slide_block = self.browser.find_element_by_xpath('//*[@id="nc_1_n1z"]')
        if (slide_block.is_displayed()):
            action = ActionChains(self.browser)
            action.click_and_hold(on_element=slide_block)
            action.move_by_offset(xoffset=258, yoffset=0)
            action.pause(0.5).release().perform()  # perform指定动作链
        self.browser.find_element_by_xpath('//button[@class="fm-button fm-submit password-login"]').click()
        time.sleep(5)
        if "login_unusual" in self.browser.current_url:
            print("gg了，要手机验证码了，救命啊啊啊啊啊")
            input("输入手机验证码啦：")
        self.cookies = '; '.join(
            item for item in [item["name"] + "=" + item["value"] for item in self.browser.get_cookies()])
        with open(COOKIES_FILE_PATH, 'w', encoding='utf-8') as file:
            file.write(self.cookies)
            print("cookie写入成功：", self.cookies)

    def taobao_login(self):
        print("登录中。。。。。")
        ok = False
        while not ok:
            with open(COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
                self.headers["cookie"] = file.read()
            response = self.session.get(self.shop_plan_url, headers=self.headers, verify=False)
            try:
                ok = json.loads(response.text)
            except:
                self.browser.get(self.alimama_login_url)
                self.browser.delete_all_cookies()
                self.save_cookies()
            self.browser.close()
            self.browser.quit()

    def get_shop_list(self):
        ids = input("请输入商品id:")
        if ids == '0':
            res = requests.get("http://manager.jddmoto.com/mall/oss/adminMallGoodsController/getAllTaoBaoItemId")
            ids = json.loads(res.text)["data"]
        else:
            ids = [int(id) for id in ids.split(",")]
        # 获取所有shop plan
        try:
            response = self.session.get(self.shop_plan_url, headers=self.headers, verify=False)
            shop_list = json.loads(response.text)["data"]["pagelist"]
            response.raise_for_status()
        except Exception as e:
            print('获取阿里妈妈主页请求失败！')
            # new_cookie = input("被强制校验啦，只能手动处理:")
            # self.headers["cookie"] = new_cookie
            # self.headers["user-agent"] = self.ua
            self.taobao_login()
            raise e
        # 根据每个shop plan获取所有商品
        for shop in shop_list:
            # campaignId = shop["campaignId"]
            # shopKeeperId = shop["campaignId"]
            # oriMemberId = shop["oriMemberId"]
            item_list_url = self.item_url.format(1, shop["campaignId"], shop["oriMemberId"], shop["shopKeeperId"])
            time.sleep(random.randint(1, 4))
            print("正在抓取商铺：", item_list_url)

            while True:
                item_list_response = self.session.get(item_list_url, headers=self.headers, verify=False)
                try:
                    time.sleep(random.randint(1, 4))
                    last_page = int(json.loads(item_list_response.text)["data"]["totalPages"])
                    break
                except Exception as e:
                    # new_cookie = input("被强制校验啦，只能手动处理:")
                    # self.headers["cookie"] = new_cookie
                    # self.headers["user-agent"] = self.ua
                    self.taobao_login()

            for page in range(1, last_page + 1):
                if page != 1:
                    item_list_url = self.item_url.format(page, shop["campaignId"], shop["oriMemberId"],
                                                         shop["shopKeeperId"])
                url_count = self.url_collection.count({"url": item_list_url})
                if url_count > 0:
                    print("该url已经爬过：", item_list_url)
                    continue
                else:
                    self.url_collection.insert_one({"url": item_list_url})
                while True:
                    if page != 1:
                        item_list_response = self.session.get(item_list_url, headers=self.headers, verify=False)
                    try:
                        print("正在抓取商铺页：", item_list_url)
                        time.sleep(random.randint(10, 15))
                        item_list = json.loads(item_list_response.text)["data"]['result']
                        break
                    except Exception as e:
                        # new_cookie = input("被强制校验啦，只能手动处理:")
                        self.taobao_login()
                        # self.headers["cookie"] = new_cookie
                        # self.headers["user-agent"] = self.ua

                for item in item_list:
                    print("正在抓取商品：", item)
                    if int(item["itemId"]) not in ids:
                        print("该商品不在选品库中：", item["itemId"])
                        continue
                    product = {}
                    product["_id"] = str(item["itemId"])
                    product["goodsNum"] = str(item["itemId"])
                    count = self.alimama_collection.count({"_id": product["_id"]})
                    if count > 0:
                        print("该商品已经存在mongo里：", product["_id"])
                        continue
                    product["commissionRatio"] = str(item["commissionRate"])
                    product["name"] = "commissionRatio"
                    print("已抓取商品：", str(product))
                    # with open("taobaoke.txt", "a",encoding="utf-8") as file:
                    #     file.write(str(product) + "\n")
                    # print(product)
                    self.alimama_collection.insert_one(product)


if __name__ == '__main__':
    session = requests.session()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
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
    alimama.taobao_login()
    alimama.get_shop_list()
