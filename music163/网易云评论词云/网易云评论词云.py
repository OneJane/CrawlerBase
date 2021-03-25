import re
import time

import imageio
import jieba
import wordcloud
from selenium import webdriver

driver = webdriver.Chrome('chromedriver.exe')
driver.get("https://music.163.com/#/song?id=548808659")
def get_comments():
    driver.switch_to.frame(0)  # contentFrame
    """页面下拉"""
    js = "document.documentElement.scrollTop = document.documentElement.scrollHeight"
    driver.execute_script(js)
    """解析数据"""
    divs = driver.find_elements_by_css_selector('.itm')
    for div in divs:
        cnt = div.find_element_by_css_selector('.cnt.f-brk').text.replace('\n',' ')
        cnt = re.findall('：(.*)',cnt)[0]
        print(cnt)
        # 数据保存
        with open('评论.txt',mode='a',encoding='utf-8') as f:
            f.write(cnt + '\n')


get_comments()
"""点击下一页"""
while driver.find_element_by_xpath(".//*[contains(@class,'znxt') and not(contains(@class,'js-disabled'))]").is_displayed():
    driver.find_element_by_css_selector(".znxt").click()
    time.sleep(1)
    driver.switch_to.default_content()
    get_comments()
driver.quit()


img = imageio.imread('logo.jpg')
f = open("评论.txt",encoding="utf-8")
txt = f.read()
txt_list = jieba.lcut(txt)
print("分词结果：",txt_list)
combine = " ".join(txt_list)
print("合并分词：", combine)
wc = wordcloud.WordCloud(
    width=1000, # 词云图宽
    height=800, # 高
    background_color='white', # 背景色
    font_path='msyh.ttc', # 微软雅黑
    mask=img, # 指定词云形状
    scale=15, # 词云图大小
    stopwords=set([line.strip() for line in (open('cn_stopwords.txt',mode='r',encoding='utf-8').readlines())])
)
wc.generate(combine)
wc.to_file('out.png')

# pip install -i https://pypi.tuna.tsinghua.edu.cn/simple imageio wordcloud jieba