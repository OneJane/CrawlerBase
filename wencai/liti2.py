import pandas as pd
import datetime
import random
import codecs
import ast
import time
from functools import partial
import subprocess

import chinese_calendar

subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs
import requests
import re
import json

ques = "上市天数，今日竞价实际换手率大于1%，今日竞价涨幅，昨日成交量，今日竞价换手率，今日竞价量比，去除今日开盘价等于涨停价，主板，今日竞价额，今日涨跌幅排序"

final_res_list = []
def get_previous_workday(year,month,day):
    now_day = datetime.date(year,month,day)
    yesterday = now_day+datetime.timedelta(days=-1)
    while not chinese_calendar.is_workday(yesterday):
        yesterday = yesterday+datetime.timedelta(days=-1)
    return yesterday

def get_TOKEN_SERVER_TIME():
    url = 'http://www.iwencai.com/unifiedwap/result'
    param = {
        'w': ques,
    }
    res = requests.get(url, params=param, headers=headers)
    js_url = re.search('<script type="text/javascript" src="(?P<js_url>.*?)"></script>', res.text, re.S).group('js_url')
    js_url = 'http:' + js_url
    js_res = requests.get(js_url, headers=headers)
    return js_res.text[:js_res.text.find(";") + 1]


def get_hexin_v(TOKEN_SERVER_TIME):
    js = execjs.compile(TOKEN_SERVER_TIME + '\n' + open('wencai.js', 'r', encoding='utf-8').read())
    result = js.call('get_result')
    return result


def run(quest, hexin_v):
    url = 'http://www.iwencai.com/customized/chart/get-robot-data'
    new_headers = {
        'Content-Type': 'application/json',
        'hexin-v': hexin_v,
        'Referer': 'http://www.iwencai.com/unifiedwap/result?w=20221002%E6%B6%A8%E5%81%9C',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    data = {
        "question": quest.split("_")[1],
        "perpage": 50,
        "page": 1,
        "secondary_intent": "stock",
        "log_info": '{"input_type":"typewrite"}',
        "source": "Ths_iwencai_Xuangu",
        "version": "2.0",
        "query_area": "",
        "block_list": "",
        "add_info": '{"urp":{"scene":1,"company":1,"business":1},"contentType":"json","searchInfo":true}',
        "rsh": "Ths_iwencai_Xuangu_8u4ruay23pannimfpojf53knu1zsovrp"
    }
    print(quest.split("_")[1])
    res = requests.post(url, headers=new_headers, data=json.dumps(data))
    # res = requests.post(url, headers=new_headers, data=json.dumps(data),proxies={"http":"http://223.247.46.49:4545"})

    origin_res_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][0]["data"]["datas"]
    time.sleep(50)
    if len(origin_res_list) > 0:
        res_list = []
        for origin_res in origin_res_list:
            try:
                res_json = json.loads(json.dumps(origin_res, ensure_ascii=False))
                res_json_new = {}
                for item in res_json.items():
                    key = re.sub(r"\(.*?\)|\{.*?\}|\[.*?\]", "", item[0])
                    value = item[1]
                    res_json_new[key] = value
                # res_json_sort = sortByKey(res_json)
                # res_info = [i for i in res_json_new.values()]

                wencai = {}
                wencai['日期'] = quest.split("_")[0].replace("年", "-").replace("月", "-").replace("日", "")
                r = re.search('竞价涨幅，(.*)成交量，', quest.split("_")[1])
                wencai['昨日']= r.group(1).replace("年", "-").replace("月", "-").replace("日", "")
                wencai['名称'] = res_json_new["股票简称"]
                wencai['股票代码'] = res_json_new["股票代码"]
                wencai['竞价换手率'] = float(res_json_new["分时换手率"])
                wencai['竞价量比'] = float(res_json_new["分时量比"])
                wencai['竞价额'] = float(res_json_new["竞价金额"])
                wencai['竞价涨幅'] = float(res_json_new["竞价涨幅"])
                wencai['竞价量'] = float(res_json_new["竞价量"])
                if "成交量" in res_json_new.keys():
                    wencai['昨日成交量'] = float(res_json_new["成交量"])
                else:
                    wencai['昨日成交量'] = 1

                wencai["竞价未匹配金额"] = float(res_json_new["竞价未匹配金额"])
                if float(wencai['竞价涨幅']) * float(wencai['竞价换手率']) > 1 and wencai['竞价额'] > 10000000 and res_json_new["上市天数"] > 50 \
                        and (wencai["竞价量"] * wencai["竞价换手率"] / wencai["昨日成交量"]) > 0.01:
                    # and float(wencai['竞价量比']) > 1 and float(wencai['竞价量比']) < 30 \
                    wencai['当日涨幅'] = float(res_json_new["涨跌幅:前复权"])
                    # if wencai['当日涨幅']>wencai['竞价涨幅'] :
                    #     # print("++"+str(wencai['竞价换手率']))
                    #     print("++涨："+str(wencai['竞价换手率']))
                    #     # print(json.dumps(wencai, indent=2, ensure_ascii=False))
                    # else:
                    #     print("--跌：" + str(wencai['竞价换手率'] ))
                    # print(json.dumps(wencai, indent=2, ensure_ascii=False))

                    res_list.append(wencai)
            except Exception as e:
                print(e)
        # res_list = [i for i in res_list if (float(i["竞价量"]) * float(i["竞价换手率"]) / float(i["昨日成交量"])) > 0.01]
        res_list.sort(key=lambda x: (x['竞价量比'] * x["竞价量"] / x['昨日成交量']), reverse=True)  # 169 78
        file = codecs.open('liti7.txt', 'a', 'utf-8')
        file.writelines(str(res_list) + "\n")
        final_res_list.append(res_list)
        # if len(res_list) > 0:
        #     file = codecs.open('liti6.txt', 'a','utf-8')
        #     file.writelines(str(res_list[0]) + "\n")
        #     final_res_list.append(res_list[0])
        #     if res_list[0]['当日涨幅']>9 :
        #         print(res_list[0]['名称']+"=="+str(res_list[0]['竞价量比']*res_list[0]["竞价量"]/res_list[0]['昨日成交量']))
        #     else:
        #         print(res_list[0]['名称'] + "--" + str(res_list[0]['竞价量比'] * res_list[0]["竞价量"] / res_list[0]['昨日成交量'])+"--"+str(res_list[0]['当日涨幅']))
        res_list.sort(key=lambda x: (float(x["当日涨幅"])), reverse=True)
        # res_list.sort(key=lambda x: ( x['竞价换手率']*x["竞价量比"]) ,reverse=True)# 169 84
        # if len(res_list)>0:
        #     file = codecs.open('liti.txt', 'a','utf-8')
        #     file.writelines(str(res_list[0])+"\n")
        #     final_res_list.append(res_list[0])
        #     if res_list[0]['当日涨幅']>9 :
        #         print("1涨停")
        #
        #     # print(json.dumps(res_list[0], indent=2, ensure_ascii=False))
        #
        # # 竞昨比高 换手率应该低
        # res_list.sort(key=lambda x: (x['竞价换手率']*x["昨日成交量"]/x['竞价量']),reverse=True) # 169 78
        # if len(res_list) > 0:
        #     file = codecs.open('liti2.txt', 'a','utf-8')
        #     file.writelines(str(res_list[0]) + "\n")
        #     final_res_list.append(res_list[0])
        #     # print(json.dumps(res_list[0], indent=2, ensure_ascii=False))
        #     if res_list[0]['当日涨幅']>9 :
        #         print("2涨停")
        #
        # res_list.sort(key=lambda x: (x['竞价额']*x["竞价量比"]*x["竞价换手率"]), reverse=True) # 169 87
        # if len(res_list) > 0:
        #     file = codecs.open('liti3.txt', 'a','utf-8')
        #     file.writelines(str(res_list[0]) + "\n")
        #     final_res_list.append(res_list[0])
        #     if res_list[0]['当日涨幅']>9 :
        #         print("3涨停")
        #
        # res_list.sort(key=lambda x: (x['竞价换手率']*x["竞价量比"]*x["昨日成交量"]/x["竞价量"]), reverse=True)  # 169 86 # 100/69
        # if len(res_list) > 0:
        #     file = codecs.open('liti4.txt', 'a','utf-8')
        #     file.writelines(str(res_list[0]) + "\n")
        #     final_res_list.append(res_list[0])
        #     if res_list[0]['当日涨幅']>9 :
        #         print("4涨停")

        # res_list.sort(key=lambda x: (x['竞价额']*x["竞价量比"]*x["竞价换手率"]*x["昨日成交量"]/x["竞价量"]), reverse=True)  # 171 89 52
        # if len(res_list) > 0:
        #     file = codecs.open('liti5.txt', 'a','utf-8')
        #     file.writelines(str(res_list[0]) + "\n")
        #     final_res_list.append(res_list[0])
        #     if res_list[0]['当日涨幅']>9 :
        #         print("5涨停")
        #
        # res_list.sort(key=lambda x: (x['竞价额']*x["竞价量比"]*x["竞价换手率"]*x["竞价量"]/x["昨日成交量"]), reverse=True)  #
        # if len(res_list) > 0:
        #     file = codecs.open('liti6.txt', 'a','utf-8')
        #     file.writelines(str(res_list[0]) + "\n")
        #     final_res_list.append(res_list[0])
        #     if res_list[0]['当日涨幅']>9 :
        #         print("6涨停")


def sortByKey(dictVar):
    sortedTuple = sorted(dictVar.items(), key=lambda x: x[0])
    sortedDict = {}
    for tupleItem in sortedTuple:
        sortedDict[tupleItem[0]] = tupleItem[1]
    return sortedDict


def main(quest):
    sever_time = get_TOKEN_SERVER_TIME()
    hexin_v = get_hexin_v(sever_time)
    run(quest, hexin_v)


def zt(n):
    return n["当日涨幅"] > 9


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    ques_list = ["2022年3月1日_上市天数，2022年3月1日竞价实际换手率大于1%，2022年3月1日竞价涨幅，2022年2月28日成交量，2022年3月1日竞价换手率，2022年3月1日竞价量比，主板，2022年3月1日竞价额，2022年3月1日涨跌幅排序，非st，2022年3月1日竞价量",
"2022年3月2日_上市天数，2022年3月2日竞价实际换手率大于1%，2022年3月2日竞价涨幅，2022年3月1日成交量，2022年3月2日竞价换手率，2022年3月2日竞价量比，主板，2022年3月2日竞价额，2022年3月2日涨跌幅排序，非st，2022年3月2日竞价量",
"2022年3月3日_上市天数，2022年3月3日竞价实际换手率大于1%，2022年3月3日竞价涨幅，2022年3月2日成交量，2022年3月3日竞价换手率，2022年3月3日竞价量比，主板，2022年3月3日竞价额，2022年3月3日涨跌幅排序，非st，2022年3月3日竞价量",
"2022年3月4日_上市天数，2022年3月4日竞价实际换手率大于1%，2022年3月4日竞价涨幅，2022年3月3日成交量，2022年3月4日竞价换手率，2022年3月4日竞价量比，主板，2022年3月4日竞价额，2022年3月4日涨跌幅排序，非st，2022年3月4日竞价量",
"2022年3月7日_上市天数，2022年3月7日竞价实际换手率大于1%，2022年3月7日竞价涨幅，2022年3月4日成交量，2022年3月7日竞价换手率，2022年3月7日竞价量比，主板，2022年3月7日竞价额，2022年3月7日涨跌幅排序，非st，2022年3月7日竞价量",
"2022年3月8日_上市天数，2022年3月8日竞价实际换手率大于1%，2022年3月8日竞价涨幅，2022年3月7日成交量，2022年3月8日竞价换手率，2022年3月8日竞价量比，主板，2022年3月8日竞价额，2022年3月8日涨跌幅排序，非st，2022年3月8日竞价量",
"2022年3月9日_上市天数，2022年3月9日竞价实际换手率大于1%，2022年3月9日竞价涨幅，2022年3月8日成交量，2022年3月9日竞价换手率，2022年3月9日竞价量比，主板，2022年3月9日竞价额，2022年3月9日涨跌幅排序，非st，2022年3月9日竞价量",
"2022年3月10日_上市天数，2022年3月10日竞价实际换手率大于1%，2022年3月10日竞价涨幅，2022年3月9日成交量，2022年3月10日竞价换手率，2022年3月10日竞价量比，主板，2022年3月10日竞价额，2022年3月10日涨跌幅排序，非st，2022年3月10日竞价量",
"2022年3月11日_上市天数，2022年3月11日竞价实际换手率大于1%，2022年3月11日竞价涨幅，2022年3月10日成交量，2022年3月11日竞价换手率，2022年3月11日竞价量比，主板，2022年3月11日竞价额，2022年3月11日涨跌幅排序，非st，2022年3月11日竞价量",
"2022年3月14日_上市天数，2022年3月14日竞价实际换手率大于1%，2022年3月14日竞价涨幅，2022年3月11日成交量，2022年3月14日竞价换手率，2022年3月14日竞价量比，主板，2022年3月14日竞价额，2022年3月14日涨跌幅排序，非st，2022年3月14日竞价量",
"2022年3月15日_上市天数，2022年3月15日竞价实际换手率大于1%，2022年3月15日竞价涨幅，2022年3月14日成交量，2022年3月15日竞价换手率，2022年3月15日竞价量比，主板，2022年3月15日竞价额，2022年3月15日涨跌幅排序，非st，2022年3月15日竞价量",
"2022年3月16日_上市天数，2022年3月16日竞价实际换手率大于1%，2022年3月16日竞价涨幅，2022年3月15日成交量，2022年3月16日竞价换手率，2022年3月16日竞价量比，主板，2022年3月16日竞价额，2022年3月16日涨跌幅排序，非st，2022年3月16日竞价量",
"2022年3月17日_上市天数，2022年3月17日竞价实际换手率大于1%，2022年3月17日竞价涨幅，2022年3月16日成交量，2022年3月17日竞价换手率，2022年3月17日竞价量比，主板，2022年3月17日竞价额，2022年3月17日涨跌幅排序，非st，2022年3月17日竞价量",
"2022年3月18日_上市天数，2022年3月18日竞价实际换手率大于1%，2022年3月18日竞价涨幅，2022年3月17日成交量，2022年3月18日竞价换手率，2022年3月18日竞价量比，主板，2022年3月18日竞价额，2022年3月18日涨跌幅排序，非st，2022年3月18日竞价量",
"2022年3月21日_上市天数，2022年3月21日竞价实际换手率大于1%，2022年3月21日竞价涨幅，2022年3月18日成交量，2022年3月21日竞价换手率，2022年3月21日竞价量比，主板，2022年3月21日竞价额，2022年3月21日涨跌幅排序，非st，2022年3月21日竞价量",
"2022年3月22日_上市天数，2022年3月22日竞价实际换手率大于1%，2022年3月22日竞价涨幅，2022年3月21日成交量，2022年3月22日竞价换手率，2022年3月22日竞价量比，主板，2022年3月22日竞价额，2022年3月22日涨跌幅排序，非st，2022年3月22日竞价量",
"2022年3月23日_上市天数，2022年3月23日竞价实际换手率大于1%，2022年3月23日竞价涨幅，2022年3月22日成交量，2022年3月23日竞价换手率，2022年3月23日竞价量比，主板，2022年3月23日竞价额，2022年3月23日涨跌幅排序，非st，2022年3月23日竞价量",
"2022年3月24日_上市天数，2022年3月24日竞价实际换手率大于1%，2022年3月24日竞价涨幅，2022年3月23日成交量，2022年3月24日竞价换手率，2022年3月24日竞价量比，主板，2022年3月24日竞价额，2022年3月24日涨跌幅排序，非st，2022年3月24日竞价量",
"2022年3月25日_上市天数，2022年3月25日竞价实际换手率大于1%，2022年3月25日竞价涨幅，2022年3月24日成交量，2022年3月25日竞价换手率，2022年3月25日竞价量比，主板，2022年3月25日竞价额，2022年3月25日涨跌幅排序，非st，2022年3月25日竞价量",
"2022年3月28日_上市天数，2022年3月28日竞价实际换手率大于1%，2022年3月28日竞价涨幅，2022年3月25日成交量，2022年3月28日竞价换手率，2022年3月28日竞价量比，主板，2022年3月28日竞价额，2022年3月28日涨跌幅排序，非st，2022年3月28日竞价量",
"2022年3月29日_上市天数，2022年3月29日竞价实际换手率大于1%，2022年3月29日竞价涨幅，2022年3月28日成交量，2022年3月29日竞价换手率，2022年3月29日竞价量比，主板，2022年3月29日竞价额，2022年3月29日涨跌幅排序，非st，2022年3月29日竞价量",
"2022年3月30日_上市天数，2022年3月30日竞价实际换手率大于1%，2022年3月30日竞价涨幅，2022年3月29日成交量，2022年3月30日竞价换手率，2022年3月30日竞价量比，主板，2022年3月30日竞价额，2022年3月30日涨跌幅排序，非st，2022年3月30日竞价量",
"2022年3月31日_上市天数，2022年3月31日竞价实际换手率大于1%，2022年3月31日竞价涨幅，2022年3月30日成交量，2022年3月31日竞价换手率，2022年3月31日竞价量比，主板，2022年3月31日竞价额，2022年3月31日涨跌幅排序，非st，2022年3月31日竞价量",
"2022年4月1日_上市天数，2022年4月1日竞价实际换手率大于1%，2022年4月1日竞价涨幅，2022年3月31日成交量，2022年4月1日竞价换手率，2022年4月1日竞价量比，主板，2022年4月1日竞价额，2022年4月1日涨跌幅排序，非st，2022年4月1日竞价量",
"2022年4月6日_上市天数，2022年4月6日竞价实际换手率大于1%，2022年4月6日竞价涨幅，2022年4月1日成交量，2022年4月6日竞价换手率，2022年4月6日竞价量比，主板，2022年4月6日竞价额，2022年4月6日涨跌幅排序，非st，2022年4月6日竞价量",
"2022年4月7日_上市天数，2022年4月7日竞价实际换手率大于1%，2022年4月7日竞价涨幅，2022年4月6日成交量，2022年4月7日竞价换手率，2022年4月7日竞价量比，主板，2022年4月7日竞价额，2022年4月7日涨跌幅排序，非st，2022年4月7日竞价量",
"2022年4月8日_上市天数，2022年4月8日竞价实际换手率大于1%，2022年4月8日竞价涨幅，2022年4月7日成交量，2022年4月8日竞价换手率，2022年4月8日竞价量比，主板，2022年4月8日竞价额，2022年4月8日涨跌幅排序，非st，2022年4月8日竞价量",
"2022年4月11日_上市天数，2022年4月11日竞价实际换手率大于1%，2022年4月11日竞价涨幅，2022年4月8日成交量，2022年4月11日竞价换手率，2022年4月11日竞价量比，主板，2022年4月11日竞价额，2022年4月11日涨跌幅排序，非st，2022年4月11日竞价量",
"2022年4月12日_上市天数，2022年4月12日竞价实际换手率大于1%，2022年4月12日竞价涨幅，2022年4月11日成交量，2022年4月12日竞价换手率，2022年4月12日竞价量比，主板，2022年4月12日竞价额，2022年4月12日涨跌幅排序，非st，2022年4月12日竞价量",
"2022年4月13日_上市天数，2022年4月13日竞价实际换手率大于1%，2022年4月13日竞价涨幅，2022年4月12日成交量，2022年4月13日竞价换手率，2022年4月13日竞价量比，主板，2022年4月13日竞价额，2022年4月13日涨跌幅排序，非st，2022年4月13日竞价量",
"2022年4月14日_上市天数，2022年4月14日竞价实际换手率大于1%，2022年4月14日竞价涨幅，2022年4月13日成交量，2022年4月14日竞价换手率，2022年4月14日竞价量比，主板，2022年4月14日竞价额，2022年4月14日涨跌幅排序，非st，2022年4月14日竞价量",
"2022年4月15日_上市天数，2022年4月15日竞价实际换手率大于1%，2022年4月15日竞价涨幅，2022年4月14日成交量，2022年4月15日竞价换手率，2022年4月15日竞价量比，主板，2022年4月15日竞价额，2022年4月15日涨跌幅排序，非st，2022年4月15日竞价量",
"2022年4月18日_上市天数，2022年4月18日竞价实际换手率大于1%，2022年4月18日竞价涨幅，2022年4月15日成交量，2022年4月18日竞价换手率，2022年4月18日竞价量比，主板，2022年4月18日竞价额，2022年4月18日涨跌幅排序，非st，2022年4月18日竞价量",
"2022年4月19日_上市天数，2022年4月19日竞价实际换手率大于1%，2022年4月19日竞价涨幅，2022年4月18日成交量，2022年4月19日竞价换手率，2022年4月19日竞价量比，主板，2022年4月19日竞价额，2022年4月19日涨跌幅排序，非st，2022年4月19日竞价量",
"2022年4月20日_上市天数，2022年4月20日竞价实际换手率大于1%，2022年4月20日竞价涨幅，2022年4月19日成交量，2022年4月20日竞价换手率，2022年4月20日竞价量比，主板，2022年4月20日竞价额，2022年4月20日涨跌幅排序，非st，2022年4月20日竞价量",
"2022年4月21日_上市天数，2022年4月21日竞价实际换手率大于1%，2022年4月21日竞价涨幅，2022年4月20日成交量，2022年4月21日竞价换手率，2022年4月21日竞价量比，主板，2022年4月21日竞价额，2022年4月21日涨跌幅排序，非st，2022年4月21日竞价量",
"2022年4月22日_上市天数，2022年4月22日竞价实际换手率大于1%，2022年4月22日竞价涨幅，2022年4月21日成交量，2022年4月22日竞价换手率，2022年4月22日竞价量比，主板，2022年4月22日竞价额，2022年4月22日涨跌幅排序，非st，2022年4月22日竞价量",
"2022年4月25日_上市天数，2022年4月25日竞价实际换手率大于1%，2022年4月25日竞价涨幅，2022年4月22日成交量，2022年4月25日竞价换手率，2022年4月25日竞价量比，主板，2022年4月25日竞价额，2022年4月25日涨跌幅排序，非st，2022年4月25日竞价量",
"2022年4月26日_上市天数，2022年4月26日竞价实际换手率大于1%，2022年4月26日竞价涨幅，2022年4月25日成交量，2022年4月26日竞价换手率，2022年4月26日竞价量比，主板，2022年4月26日竞价额，2022年4月26日涨跌幅排序，非st，2022年4月26日竞价量",
"2022年4月27日_上市天数，2022年4月27日竞价实际换手率大于1%，2022年4月27日竞价涨幅，2022年4月26日成交量，2022年4月27日竞价换手率，2022年4月27日竞价量比，主板，2022年4月27日竞价额，2022年4月27日涨跌幅排序，非st，2022年4月27日竞价量",
"2022年4月28日_上市天数，2022年4月28日竞价实际换手率大于1%，2022年4月28日竞价涨幅，2022年4月27日成交量，2022年4月28日竞价换手率，2022年4月28日竞价量比，主板，2022年4月28日竞价额，2022年4月28日涨跌幅排序，非st，2022年4月28日竞价量",
"2022年4月29日_上市天数，2022年4月29日竞价实际换手率大于1%，2022年4月29日竞价涨幅，2022年4月28日成交量，2022年4月29日竞价换手率，2022年4月29日竞价量比，主板，2022年4月29日竞价额，2022年4月29日涨跌幅排序，非st，2022年4月29日竞价量",
"2022年5月5日_上市天数，2022年5月5日竞价实际换手率大于1%，2022年5月5日竞价涨幅，2022年4月29日成交量，2022年5月5日竞价换手率，2022年5月5日竞价量比，主板，2022年5月5日竞价额，2022年5月5日涨跌幅排序，非st，2022年5月5日竞价量",
"2022年5月6日_上市天数，2022年5月6日竞价实际换手率大于1%，2022年5月6日竞价涨幅，2022年5月5日成交量，2022年5月6日竞价换手率，2022年5月6日竞价量比，主板，2022年5月6日竞价额，2022年5月6日涨跌幅排序，非st，2022年5月6日竞价量",
"2022年5月9日_上市天数，2022年5月9日竞价实际换手率大于1%，2022年5月9日竞价涨幅，2022年5月6日成交量，2022年5月9日竞价换手率，2022年5月9日竞价量比，主板，2022年5月9日竞价额，2022年5月9日涨跌幅排序，非st，2022年5月9日竞价量",
"2022年5月10日_上市天数，2022年5月10日竞价实际换手率大于1%，2022年5月10日竞价涨幅，2022年5月9日成交量，2022年5月10日竞价换手率，2022年5月10日竞价量比，主板，2022年5月10日竞价额，2022年5月10日涨跌幅排序，非st，2022年5月10日竞价量",
"2022年5月11日_上市天数，2022年5月11日竞价实际换手率大于1%，2022年5月11日竞价涨幅，2022年5月10日成交量，2022年5月11日竞价换手率，2022年5月11日竞价量比，主板，2022年5月11日竞价额，2022年5月11日涨跌幅排序，非st，2022年5月11日竞价量",
"2022年5月12日_上市天数，2022年5月12日竞价实际换手率大于1%，2022年5月12日竞价涨幅，2022年5月11日成交量，2022年5月12日竞价换手率，2022年5月12日竞价量比，主板，2022年5月12日竞价额，2022年5月12日涨跌幅排序，非st，2022年5月12日竞价量",
"2022年5月13日_上市天数，2022年5月13日竞价实际换手率大于1%，2022年5月13日竞价涨幅，2022年5月12日成交量，2022年5月13日竞价换手率，2022年5月13日竞价量比，主板，2022年5月13日竞价额，2022年5月13日涨跌幅排序，非st，2022年5月13日竞价量",
"2022年5月16日_上市天数，2022年5月16日竞价实际换手率大于1%，2022年5月16日竞价涨幅，2022年5月13日成交量，2022年5月16日竞价换手率，2022年5月16日竞价量比，主板，2022年5月16日竞价额，2022年5月16日涨跌幅排序，非st，2022年5月16日竞价量",
"2022年5月17日_上市天数，2022年5月17日竞价实际换手率大于1%，2022年5月17日竞价涨幅，2022年5月16日成交量，2022年5月17日竞价换手率，2022年5月17日竞价量比，主板，2022年5月17日竞价额，2022年5月17日涨跌幅排序，非st，2022年5月17日竞价量",
"2022年5月18日_上市天数，2022年5月18日竞价实际换手率大于1%，2022年5月18日竞价涨幅，2022年5月17日成交量，2022年5月18日竞价换手率，2022年5月18日竞价量比，主板，2022年5月18日竞价额，2022年5月18日涨跌幅排序，非st，2022年5月18日竞价量",
"2022年5月19日_上市天数，2022年5月19日竞价实际换手率大于1%，2022年5月19日竞价涨幅，2022年5月18日成交量，2022年5月19日竞价换手率，2022年5月19日竞价量比，主板，2022年5月19日竞价额，2022年5月19日涨跌幅排序，非st，2022年5月19日竞价量",
"2022年5月20日_上市天数，2022年5月20日竞价实际换手率大于1%，2022年5月20日竞价涨幅，2022年5月19日成交量，2022年5月20日竞价换手率，2022年5月20日竞价量比，主板，2022年5月20日竞价额，2022年5月20日涨跌幅排序，非st，2022年5月20日竞价量",
"2022年5月23日_上市天数，2022年5月23日竞价实际换手率大于1%，2022年5月23日竞价涨幅，2022年5月20日成交量，2022年5月23日竞价换手率，2022年5月23日竞价量比，主板，2022年5月23日竞价额，2022年5月23日涨跌幅排序，非st，2022年5月23日竞价量",
"2022年5月24日_上市天数，2022年5月24日竞价实际换手率大于1%，2022年5月24日竞价涨幅，2022年5月23日成交量，2022年5月24日竞价换手率，2022年5月24日竞价量比，主板，2022年5月24日竞价额，2022年5月24日涨跌幅排序，非st，2022年5月24日竞价量",
"2022年5月25日_上市天数，2022年5月25日竞价实际换手率大于1%，2022年5月25日竞价涨幅，2022年5月24日成交量，2022年5月25日竞价换手率，2022年5月25日竞价量比，主板，2022年5月25日竞价额，2022年5月25日涨跌幅排序，非st，2022年5月25日竞价量",
"2022年5月26日_上市天数，2022年5月26日竞价实际换手率大于1%，2022年5月26日竞价涨幅，2022年5月25日成交量，2022年5月26日竞价换手率，2022年5月26日竞价量比，主板，2022年5月26日竞价额，2022年5月26日涨跌幅排序，非st，2022年5月26日竞价量",
"2022年5月27日_上市天数，2022年5月27日竞价实际换手率大于1%，2022年5月27日竞价涨幅，2022年5月26日成交量，2022年5月27日竞价换手率，2022年5月27日竞价量比，主板，2022年5月27日竞价额，2022年5月27日涨跌幅排序，非st，2022年5月27日竞价量",
"2022年5月30日_上市天数，2022年5月30日竞价实际换手率大于1%，2022年5月30日竞价涨幅，2022年5月27日成交量，2022年5月30日竞价换手率，2022年5月30日竞价量比，主板，2022年5月30日竞价额，2022年5月30日涨跌幅排序，非st，2022年5月30日竞价量",
"2022年5月31日_上市天数，2022年5月31日竞价实际换手率大于1%，2022年5月31日竞价涨幅，2022年5月30日成交量，2022年5月31日竞价换手率，2022年5月31日竞价量比，主板，2022年5月31日竞价额，2022年5月31日涨跌幅排序，非st，2022年5月31日竞价量",
"2022年6月1日_上市天数，2022年6月1日竞价实际换手率大于1%，2022年6月1日竞价涨幅，2022年5月31日成交量，2022年6月1日竞价换手率，2022年6月1日竞价量比，主板，2022年6月1日竞价额，2022年6月1日涨跌幅排序，非st，2022年6月1日竞价量",
"2022年6月2日_上市天数，2022年6月2日竞价实际换手率大于1%，2022年6月2日竞价涨幅，2022年6月1日成交量，2022年6月2日竞价换手率，2022年6月2日竞价量比，主板，2022年6月2日竞价额，2022年6月2日涨跌幅排序，非st，2022年6月2日竞价量",
"2022年6月6日_上市天数，2022年6月6日竞价实际换手率大于1%，2022年6月6日竞价涨幅，2022年6月2日成交量，2022年6月6日竞价换手率，2022年6月6日竞价量比，主板，2022年6月6日竞价额，2022年6月6日涨跌幅排序，非st，2022年6月6日竞价量",
"2022年6月7日_上市天数，2022年6月7日竞价实际换手率大于1%，2022年6月7日竞价涨幅，2022年6月6日成交量，2022年6月7日竞价换手率，2022年6月7日竞价量比，主板，2022年6月7日竞价额，2022年6月7日涨跌幅排序，非st，2022年6月7日竞价量",
"2022年6月8日_上市天数，2022年6月8日竞价实际换手率大于1%，2022年6月8日竞价涨幅，2022年6月7日成交量，2022年6月8日竞价换手率，2022年6月8日竞价量比，主板，2022年6月8日竞价额，2022年6月8日涨跌幅排序，非st，2022年6月8日竞价量",
"2022年6月9日_上市天数，2022年6月9日竞价实际换手率大于1%，2022年6月9日竞价涨幅，2022年6月8日成交量，2022年6月9日竞价换手率，2022年6月9日竞价量比，主板，2022年6月9日竞价额，2022年6月9日涨跌幅排序，非st，2022年6月9日竞价量",
"2022年6月10日_上市天数，2022年6月10日竞价实际换手率大于1%，2022年6月10日竞价涨幅，2022年6月9日成交量，2022年6月10日竞价换手率，2022年6月10日竞价量比，主板，2022年6月10日竞价额，2022年6月10日涨跌幅排序，非st，2022年6月10日竞价量",
"2022年6月13日_上市天数，2022年6月13日竞价实际换手率大于1%，2022年6月13日竞价涨幅，2022年6月10日成交量，2022年6月13日竞价换手率，2022年6月13日竞价量比，主板，2022年6月13日竞价额，2022年6月13日涨跌幅排序，非st，2022年6月13日竞价量",
"2022年6月14日_上市天数，2022年6月14日竞价实际换手率大于1%，2022年6月14日竞价涨幅，2022年6月13日成交量，2022年6月14日竞价换手率，2022年6月14日竞价量比，主板，2022年6月14日竞价额，2022年6月14日涨跌幅排序，非st，2022年6月14日竞价量",
"2022年6月15日_上市天数，2022年6月15日竞价实际换手率大于1%，2022年6月15日竞价涨幅，2022年6月14日成交量，2022年6月15日竞价换手率，2022年6月15日竞价量比，主板，2022年6月15日竞价额，2022年6月15日涨跌幅排序，非st，2022年6月15日竞价量",
"2022年6月16日_上市天数，2022年6月16日竞价实际换手率大于1%，2022年6月16日竞价涨幅，2022年6月15日成交量，2022年6月16日竞价换手率，2022年6月16日竞价量比，主板，2022年6月16日竞价额，2022年6月16日涨跌幅排序，非st，2022年6月16日竞价量",
"2022年6月17日_上市天数，2022年6月17日竞价实际换手率大于1%，2022年6月17日竞价涨幅，2022年6月16日成交量，2022年6月17日竞价换手率，2022年6月17日竞价量比，主板，2022年6月17日竞价额，2022年6月17日涨跌幅排序，非st，2022年6月17日竞价量",
"2022年6月20日_上市天数，2022年6月20日竞价实际换手率大于1%，2022年6月20日竞价涨幅，2022年6月17日成交量，2022年6月20日竞价换手率，2022年6月20日竞价量比，主板，2022年6月20日竞价额，2022年6月20日涨跌幅排序，非st，2022年6月20日竞价量",
"2022年6月21日_上市天数，2022年6月21日竞价实际换手率大于1%，2022年6月21日竞价涨幅，2022年6月20日成交量，2022年6月21日竞价换手率，2022年6月21日竞价量比，主板，2022年6月21日竞价额，2022年6月21日涨跌幅排序，非st，2022年6月21日竞价量",
"2022年6月22日_上市天数，2022年6月22日竞价实际换手率大于1%，2022年6月22日竞价涨幅，2022年6月21日成交量，2022年6月22日竞价换手率，2022年6月22日竞价量比，主板，2022年6月22日竞价额，2022年6月22日涨跌幅排序，非st，2022年6月22日竞价量",
"2022年6月23日_上市天数，2022年6月23日竞价实际换手率大于1%，2022年6月23日竞价涨幅，2022年6月22日成交量，2022年6月23日竞价换手率，2022年6月23日竞价量比，主板，2022年6月23日竞价额，2022年6月23日涨跌幅排序，非st，2022年6月23日竞价量",
"2022年6月24日_上市天数，2022年6月24日竞价实际换手率大于1%，2022年6月24日竞价涨幅，2022年6月23日成交量，2022年6月24日竞价换手率，2022年6月24日竞价量比，主板，2022年6月24日竞价额，2022年6月24日涨跌幅排序，非st，2022年6月24日竞价量",
"2022年6月27日_上市天数，2022年6月27日竞价实际换手率大于1%，2022年6月27日竞价涨幅，2022年6月24日成交量，2022年6月27日竞价换手率，2022年6月27日竞价量比，主板，2022年6月27日竞价额，2022年6月27日涨跌幅排序，非st，2022年6月27日竞价量",
"2022年6月28日_上市天数，2022年6月28日竞价实际换手率大于1%，2022年6月28日竞价涨幅，2022年6月27日成交量，2022年6月28日竞价换手率，2022年6月28日竞价量比，主板，2022年6月28日竞价额，2022年6月28日涨跌幅排序，非st，2022年6月28日竞价量",
"2022年6月29日_上市天数，2022年6月29日竞价实际换手率大于1%，2022年6月29日竞价涨幅，2022年6月28日成交量，2022年6月29日竞价换手率，2022年6月29日竞价量比，主板，2022年6月29日竞价额，2022年6月29日涨跌幅排序，非st，2022年6月29日竞价量",
"2022年6月30日_上市天数，2022年6月30日竞价实际换手率大于1%，2022年6月30日竞价涨幅，2022年6月29日成交量，2022年6月30日竞价换手率，2022年6月30日竞价量比，主板，2022年6月30日竞价额，2022年6月30日涨跌幅排序，非st，2022年6月30日竞价量",
"2022年7月1日_上市天数，2022年7月1日竞价实际换手率大于1%，2022年7月1日竞价涨幅，2022年6月30日成交量，2022年7月1日竞价换手率，2022年7月1日竞价量比，主板，2022年7月1日竞价额，2022年7月1日涨跌幅排序，非st，2022年7月1日竞价量",
"2022年7月4日_上市天数，2022年7月4日竞价实际换手率大于1%，2022年7月4日竞价涨幅，2022年7月1日成交量，2022年7月4日竞价换手率，2022年7月4日竞价量比，主板，2022年7月4日竞价额，2022年7月4日涨跌幅排序，非st，2022年7月4日竞价量",
"2022年7月5日_上市天数，2022年7月5日竞价实际换手率大于1%，2022年7月5日竞价涨幅，2022年7月4日成交量，2022年7月5日竞价换手率，2022年7月5日竞价量比，主板，2022年7月5日竞价额，2022年7月5日涨跌幅排序，非st，2022年7月5日竞价量",
"2022年7月6日_上市天数，2022年7月6日竞价实际换手率大于1%，2022年7月6日竞价涨幅，2022年7月5日成交量，2022年7月6日竞价换手率，2022年7月6日竞价量比，主板，2022年7月6日竞价额，2022年7月6日涨跌幅排序，非st，2022年7月6日竞价量",
"2022年7月7日_上市天数，2022年7月7日竞价实际换手率大于1%，2022年7月7日竞价涨幅，2022年7月6日成交量，2022年7月7日竞价换手率，2022年7月7日竞价量比，主板，2022年7月7日竞价额，2022年7月7日涨跌幅排序，非st，2022年7月7日竞价量",
"2022年7月8日_上市天数，2022年7月8日竞价实际换手率大于1%，2022年7月8日竞价涨幅，2022年7月7日成交量，2022年7月8日竞价换手率，2022年7月8日竞价量比，主板，2022年7月8日竞价额，2022年7月8日涨跌幅排序，非st，2022年7月8日竞价量",
"2022年7月11日_上市天数，2022年7月11日竞价实际换手率大于1%，2022年7月11日竞价涨幅，2022年7月8日成交量，2022年7月11日竞价换手率，2022年7月11日竞价量比，主板，2022年7月11日竞价额，2022年7月11日涨跌幅排序，非st，2022年7月11日竞价量",
"2022年7月12日_上市天数，2022年7月12日竞价实际换手率大于1%，2022年7月12日竞价涨幅，2022年7月11日成交量，2022年7月12日竞价换手率，2022年7月12日竞价量比，主板，2022年7月12日竞价额，2022年7月12日涨跌幅排序，非st，2022年7月12日竞价量",
"2022年7月13日_上市天数，2022年7月13日竞价实际换手率大于1%，2022年7月13日竞价涨幅，2022年7月12日成交量，2022年7月13日竞价换手率，2022年7月13日竞价量比，主板，2022年7月13日竞价额，2022年7月13日涨跌幅排序，非st，2022年7月13日竞价量",
"2022年7月14日_上市天数，2022年7月14日竞价实际换手率大于1%，2022年7月14日竞价涨幅，2022年7月13日成交量，2022年7月14日竞价换手率，2022年7月14日竞价量比，主板，2022年7月14日竞价额，2022年7月14日涨跌幅排序，非st，2022年7月14日竞价量",
"2022年7月15日_上市天数，2022年7月15日竞价实际换手率大于1%，2022年7月15日竞价涨幅，2022年7月14日成交量，2022年7月15日竞价换手率，2022年7月15日竞价量比，主板，2022年7月15日竞价额，2022年7月15日涨跌幅排序，非st，2022年7月15日竞价量",
"2022年7月18日_上市天数，2022年7月18日竞价实际换手率大于1%，2022年7月18日竞价涨幅，2022年7月15日成交量，2022年7月18日竞价换手率，2022年7月18日竞价量比，主板，2022年7月18日竞价额，2022年7月18日涨跌幅排序，非st，2022年7月18日竞价量",
"2022年7月19日_上市天数，2022年7月19日竞价实际换手率大于1%，2022年7月19日竞价涨幅，2022年7月18日成交量，2022年7月19日竞价换手率，2022年7月19日竞价量比，主板，2022年7月19日竞价额，2022年7月19日涨跌幅排序，非st，2022年7月19日竞价量",
"2022年7月20日_上市天数，2022年7月20日竞价实际换手率大于1%，2022年7月20日竞价涨幅，2022年7月19日成交量，2022年7月20日竞价换手率，2022年7月20日竞价量比，主板，2022年7月20日竞价额，2022年7月20日涨跌幅排序，非st，2022年7月20日竞价量",
"2022年7月21日_上市天数，2022年7月21日竞价实际换手率大于1%，2022年7月21日竞价涨幅，2022年7月20日成交量，2022年7月21日竞价换手率，2022年7月21日竞价量比，主板，2022年7月21日竞价额，2022年7月21日涨跌幅排序，非st，2022年7月21日竞价量",
"2022年7月22日_上市天数，2022年7月22日竞价实际换手率大于1%，2022年7月22日竞价涨幅，2022年7月21日成交量，2022年7月22日竞价换手率，2022年7月22日竞价量比，主板，2022年7月22日竞价额，2022年7月22日涨跌幅排序，非st，2022年7月22日竞价量",
"2022年7月25日_上市天数，2022年7月25日竞价实际换手率大于1%，2022年7月25日竞价涨幅，2022年7月22日成交量，2022年7月25日竞价换手率，2022年7月25日竞价量比，主板，2022年7月25日竞价额，2022年7月25日涨跌幅排序，非st，2022年7月25日竞价量",
"2022年7月26日_上市天数，2022年7月26日竞价实际换手率大于1%，2022年7月26日竞价涨幅，2022年7月25日成交量，2022年7月26日竞价换手率，2022年7月26日竞价量比，主板，2022年7月26日竞价额，2022年7月26日涨跌幅排序，非st，2022年7月26日竞价量",
"2022年7月27日_上市天数，2022年7月27日竞价实际换手率大于1%，2022年7月27日竞价涨幅，2022年7月26日成交量，2022年7月27日竞价换手率，2022年7月27日竞价量比，主板，2022年7月27日竞价额，2022年7月27日涨跌幅排序，非st，2022年7月27日竞价量",
"2022年7月28日_上市天数，2022年7月28日竞价实际换手率大于1%，2022年7月28日竞价涨幅，2022年7月27日成交量，2022年7月28日竞价换手率，2022年7月28日竞价量比，主板，2022年7月28日竞价额，2022年7月28日涨跌幅排序，非st，2022年7月28日竞价量",
"2022年7月29日_上市天数，2022年7月29日竞价实际换手率大于1%，2022年7月29日竞价涨幅，2022年7月28日成交量，2022年7月29日竞价换手率，2022年7月29日竞价量比，主板，2022年7月29日竞价额，2022年7月29日涨跌幅排序，非st，2022年7月29日竞价量",
"2022年8月1日_上市天数，2022年8月1日竞价实际换手率大于1%，2022年8月1日竞价涨幅，2022年7月29日成交量，2022年8月1日竞价换手率，2022年8月1日竞价量比，主板，2022年8月1日竞价额，2022年8月1日涨跌幅排序，非st，2022年8月1日竞价量",
"2022年8月2日_上市天数，2022年8月2日竞价实际换手率大于1%，2022年8月2日竞价涨幅，2022年8月1日成交量，2022年8月2日竞价换手率，2022年8月2日竞价量比，主板，2022年8月2日竞价额，2022年8月2日涨跌幅排序，非st，2022年8月2日竞价量",
"2022年8月3日_上市天数，2022年8月3日竞价实际换手率大于1%，2022年8月3日竞价涨幅，2022年8月2日成交量，2022年8月3日竞价换手率，2022年8月3日竞价量比，主板，2022年8月3日竞价额，2022年8月3日涨跌幅排序，非st，2022年8月3日竞价量",
"2022年8月4日_上市天数，2022年8月4日竞价实际换手率大于1%，2022年8月4日竞价涨幅，2022年8月3日成交量，2022年8月4日竞价换手率，2022年8月4日竞价量比，主板，2022年8月4日竞价额，2022年8月4日涨跌幅排序，非st，2022年8月4日竞价量",
"2022年8月5日_上市天数，2022年8月5日竞价实际换手率大于1%，2022年8月5日竞价涨幅，2022年8月4日成交量，2022年8月5日竞价换手率，2022年8月5日竞价量比，主板，2022年8月5日竞价额，2022年8月5日涨跌幅排序，非st，2022年8月5日竞价量",
"2022年8月8日_上市天数，2022年8月8日竞价实际换手率大于1%，2022年8月8日竞价涨幅，2022年8月5日成交量，2022年8月8日竞价换手率，2022年8月8日竞价量比，主板，2022年8月8日竞价额，2022年8月8日涨跌幅排序，非st，2022年8月8日竞价量",
"2022年8月9日_上市天数，2022年8月9日竞价实际换手率大于1%，2022年8月9日竞价涨幅，2022年8月8日成交量，2022年8月9日竞价换手率，2022年8月9日竞价量比，主板，2022年8月9日竞价额，2022年8月9日涨跌幅排序，非st，2022年8月9日竞价量",
"2022年8月10日_上市天数，2022年8月10日竞价实际换手率大于1%，2022年8月10日竞价涨幅，2022年8月9日成交量，2022年8月10日竞价换手率，2022年8月10日竞价量比，主板，2022年8月10日竞价额，2022年8月10日涨跌幅排序，非st，2022年8月10日竞价量",
"2022年8月11日_上市天数，2022年8月11日竞价实际换手率大于1%，2022年8月11日竞价涨幅，2022年8月10日成交量，2022年8月11日竞价换手率，2022年8月11日竞价量比，主板，2022年8月11日竞价额，2022年8月11日涨跌幅排序，非st，2022年8月11日竞价量",
"2022年8月12日_上市天数，2022年8月12日竞价实际换手率大于1%，2022年8月12日竞价涨幅，2022年8月11日成交量，2022年8月12日竞价换手率，2022年8月12日竞价量比，主板，2022年8月12日竞价额，2022年8月12日涨跌幅排序，非st，2022年8月12日竞价量",
"2022年8月15日_上市天数，2022年8月15日竞价实际换手率大于1%，2022年8月15日竞价涨幅，2022年8月12日成交量，2022年8月15日竞价换手率，2022年8月15日竞价量比，主板，2022年8月15日竞价额，2022年8月15日涨跌幅排序，非st，2022年8月15日竞价量",
"2022年8月16日_上市天数，2022年8月16日竞价实际换手率大于1%，2022年8月16日竞价涨幅，2022年8月15日成交量，2022年8月16日竞价换手率，2022年8月16日竞价量比，主板，2022年8月16日竞价额，2022年8月16日涨跌幅排序，非st，2022年8月16日竞价量",
"2022年8月17日_上市天数，2022年8月17日竞价实际换手率大于1%，2022年8月17日竞价涨幅，2022年8月16日成交量，2022年8月17日竞价换手率，2022年8月17日竞价量比，主板，2022年8月17日竞价额，2022年8月17日涨跌幅排序，非st，2022年8月17日竞价量",
"2022年8月18日_上市天数，2022年8月18日竞价实际换手率大于1%，2022年8月18日竞价涨幅，2022年8月17日成交量，2022年8月18日竞价换手率，2022年8月18日竞价量比，主板，2022年8月18日竞价额，2022年8月18日涨跌幅排序，非st，2022年8月18日竞价量",
"2022年8月19日_上市天数，2022年8月19日竞价实际换手率大于1%，2022年8月19日竞价涨幅，2022年8月18日成交量，2022年8月19日竞价换手率，2022年8月19日竞价量比，主板，2022年8月19日竞价额，2022年8月19日涨跌幅排序，非st，2022年8月19日竞价量",
"2022年8月22日_上市天数，2022年8月22日竞价实际换手率大于1%，2022年8月22日竞价涨幅，2022年8月19日成交量，2022年8月22日竞价换手率，2022年8月22日竞价量比，主板，2022年8月22日竞价额，2022年8月22日涨跌幅排序，非st，2022年8月22日竞价量",
"2022年8月23日_上市天数，2022年8月23日竞价实际换手率大于1%，2022年8月23日竞价涨幅，2022年8月22日成交量，2022年8月23日竞价换手率，2022年8月23日竞价量比，主板，2022年8月23日竞价额，2022年8月23日涨跌幅排序，非st，2022年8月23日竞价量",
"2022年8月24日_上市天数，2022年8月24日竞价实际换手率大于1%，2022年8月24日竞价涨幅，2022年8月23日成交量，2022年8月24日竞价换手率，2022年8月24日竞价量比，主板，2022年8月24日竞价额，2022年8月24日涨跌幅排序，非st，2022年8月24日竞价量",
"2022年8月25日_上市天数，2022年8月25日竞价实际换手率大于1%，2022年8月25日竞价涨幅，2022年8月24日成交量，2022年8月25日竞价换手率，2022年8月25日竞价量比，主板，2022年8月25日竞价额，2022年8月25日涨跌幅排序，非st，2022年8月25日竞价量",
"2022年8月26日_上市天数，2022年8月26日竞价实际换手率大于1%，2022年8月26日竞价涨幅，2022年8月25日成交量，2022年8月26日竞价换手率，2022年8月26日竞价量比，主板，2022年8月26日竞价额，2022年8月26日涨跌幅排序，非st，2022年8月26日竞价量",
"2022年8月29日_上市天数，2022年8月29日竞价实际换手率大于1%，2022年8月29日竞价涨幅，2022年8月26日成交量，2022年8月29日竞价换手率，2022年8月29日竞价量比，主板，2022年8月29日竞价额，2022年8月29日涨跌幅排序，非st，2022年8月29日竞价量",
"2022年8月30日_上市天数，2022年8月30日竞价实际换手率大于1%，2022年8月30日竞价涨幅，2022年8月29日成交量，2022年8月30日竞价换手率，2022年8月30日竞价量比，主板，2022年8月30日竞价额，2022年8月30日涨跌幅排序，非st，2022年8月30日竞价量",
"2022年8月31日_上市天数，2022年8月31日竞价实际换手率大于1%，2022年8月31日竞价涨幅，2022年8月30日成交量，2022年8月31日竞价换手率，2022年8月31日竞价量比，主板，2022年8月31日竞价额，2022年8月31日涨跌幅排序，非st，2022年8月31日竞价量",
"2022年9月1日_上市天数，2022年9月1日竞价实际换手率大于1%，2022年9月1日竞价涨幅，2022年8月31日成交量，2022年9月1日竞价换手率，2022年9月1日竞价量比，主板，2022年9月1日竞价额，2022年9月1日涨跌幅排序，非st，2022年9月1日竞价量",
"2022年9月2日_上市天数，2022年9月2日竞价实际换手率大于1%，2022年9月2日竞价涨幅，2022年9月1日成交量，2022年9月2日竞价换手率，2022年9月2日竞价量比，主板，2022年9月2日竞价额，2022年9月2日涨跌幅排序，非st，2022年9月2日竞价量",
"2022年9月5日_上市天数，2022年9月5日竞价实际换手率大于1%，2022年9月5日竞价涨幅，2022年9月2日成交量，2022年9月5日竞价换手率，2022年9月5日竞价量比，主板，2022年9月5日竞价额，2022年9月5日涨跌幅排序，非st，2022年9月5日竞价量",
"2022年9月6日_上市天数，2022年9月6日竞价实际换手率大于1%，2022年9月6日竞价涨幅，2022年9月5日成交量，2022年9月6日竞价换手率，2022年9月6日竞价量比，主板，2022年9月6日竞价额，2022年9月6日涨跌幅排序，非st，2022年9月6日竞价量",
"2022年9月7日_上市天数，2022年9月7日竞价实际换手率大于1%，2022年9月7日竞价涨幅，2022年9月6日成交量，2022年9月7日竞价换手率，2022年9月7日竞价量比，主板，2022年9月7日竞价额，2022年9月7日涨跌幅排序，非st，2022年9月7日竞价量",
"2022年9月8日_上市天数，2022年9月8日竞价实际换手率大于1%，2022年9月8日竞价涨幅，2022年9月7日成交量，2022年9月8日竞价换手率，2022年9月8日竞价量比，主板，2022年9月8日竞价额，2022年9月8日涨跌幅排序，非st，2022年9月8日竞价量",
"2022年9月9日_上市天数，2022年9月9日竞价实际换手率大于1%，2022年9月9日竞价涨幅，2022年9月8日成交量，2022年9月9日竞价换手率，2022年9月9日竞价量比，主板，2022年9月9日竞价额，2022年9月9日涨跌幅排序，非st，2022年9月9日竞价量",
"2022年9月13日_上市天数，2022年9月13日竞价实际换手率大于1%，2022年9月13日竞价涨幅，2022年9月9日成交量，2022年9月13日竞价换手率，2022年9月13日竞价量比，主板，2022年9月13日竞价额，2022年9月13日涨跌幅排序，非st，2022年9月13日竞价量",
"2022年9月14日_上市天数，2022年9月14日竞价实际换手率大于1%，2022年9月14日竞价涨幅，2022年9月13日成交量，2022年9月14日竞价换手率，2022年9月14日竞价量比，主板，2022年9月14日竞价额，2022年9月14日涨跌幅排序，非st，2022年9月14日竞价量",
"2022年9月15日_上市天数，2022年9月15日竞价实际换手率大于1%，2022年9月15日竞价涨幅，2022年9月14日成交量，2022年9月15日竞价换手率，2022年9月15日竞价量比，主板，2022年9月15日竞价额，2022年9月15日涨跌幅排序，非st，2022年9月15日竞价量",
"2022年9月16日_上市天数，2022年9月16日竞价实际换手率大于1%，2022年9月16日竞价涨幅，2022年9月15日成交量，2022年9月16日竞价换手率，2022年9月16日竞价量比，主板，2022年9月16日竞价额，2022年9月16日涨跌幅排序，非st，2022年9月16日竞价量",
"2022年9月19日_上市天数，2022年9月19日竞价实际换手率大于1%，2022年9月19日竞价涨幅，2022年9月16日成交量，2022年9月19日竞价换手率，2022年9月19日竞价量比，主板，2022年9月19日竞价额，2022年9月19日涨跌幅排序，非st，2022年9月19日竞价量",
"2022年9月20日_上市天数，2022年9月20日竞价实际换手率大于1%，2022年9月20日竞价涨幅，2022年9月19日成交量，2022年9月20日竞价换手率，2022年9月20日竞价量比，主板，2022年9月20日竞价额，2022年9月20日涨跌幅排序，非st，2022年9月20日竞价量",
"2022年9月21日_上市天数，2022年9月21日竞价实际换手率大于1%，2022年9月21日竞价涨幅，2022年9月20日成交量，2022年9月21日竞价换手率，2022年9月21日竞价量比，主板，2022年9月21日竞价额，2022年9月21日涨跌幅排序，非st，2022年9月21日竞价量",
"2022年9月22日_上市天数，2022年9月22日竞价实际换手率大于1%，2022年9月22日竞价涨幅，2022年9月21日成交量，2022年9月22日竞价换手率，2022年9月22日竞价量比，主板，2022年9月22日竞价额，2022年9月22日涨跌幅排序，非st，2022年9月22日竞价量",
"2022年9月23日_上市天数，2022年9月23日竞价实际换手率大于1%，2022年9月23日竞价涨幅，2022年9月22日成交量，2022年9月23日竞价换手率，2022年9月23日竞价量比，主板，2022年9月23日竞价额，2022年9月23日涨跌幅排序，非st，2022年9月23日竞价量",
"2022年9月26日_上市天数，2022年9月26日竞价实际换手率大于1%，2022年9月26日竞价涨幅，2022年9月23日成交量，2022年9月26日竞价换手率，2022年9月26日竞价量比，主板，2022年9月26日竞价额，2022年9月26日涨跌幅排序，非st，2022年9月26日竞价量",
"2022年9月27日_上市天数，2022年9月27日竞价实际换手率大于1%，2022年9月27日竞价涨幅，2022年9月26日成交量，2022年9月27日竞价换手率，2022年9月27日竞价量比，主板，2022年9月27日竞价额，2022年9月27日涨跌幅排序，非st，2022年9月27日竞价量",
"2022年9月28日_上市天数，2022年9月28日竞价实际换手率大于1%，2022年9月28日竞价涨幅，2022年9月27日成交量，2022年9月28日竞价换手率，2022年9月28日竞价量比，主板，2022年9月28日竞价额，2022年9月28日涨跌幅排序，非st，2022年9月28日竞价量",
"2022年9月29日_上市天数，2022年9月29日竞价实际换手率大于1%，2022年9月29日竞价涨幅，2022年9月28日成交量，2022年9月29日竞价换手率，2022年9月29日竞价量比，主板，2022年9月29日竞价额，2022年9月29日涨跌幅排序，非st，2022年9月29日竞价量",
"2022年9月30日_上市天数，2022年9月30日竞价实际换手率大于1%，2022年9月30日竞价涨幅，2022年9月29日成交量，2022年9月30日竞价换手率，2022年9月30日竞价量比，主板，2022年9月30日竞价额，2022年9月30日涨跌幅排序，非st，2022年9月30日竞价量",
"2022年10月10日_上市天数，2022年10月10日竞价实际换手率大于1%，2022年10月10日竞价涨幅，2022年9月30日成交量，2022年10月10日竞价换手率，2022年10月10日竞价量比，主板，2022年10月10日竞价额，2022年10月10日涨跌幅排序，非st，2022年10月10日竞价量",
"2022年10月11日_上市天数，2022年10月11日竞价实际换手率大于1%，2022年10月11日竞价涨幅，2022年10月10日成交量，2022年10月11日竞价换手率，2022年10月11日竞价量比，主板，2022年10月11日竞价额，2022年10月11日涨跌幅排序，非st，2022年10月11日竞价量",
"2022年10月12日_上市天数，2022年10月12日竞价实际换手率大于1%，2022年10月12日竞价涨幅，2022年10月11日成交量，2022年10月12日竞价换手率，2022年10月12日竞价量比，主板，2022年10月12日竞价额，2022年10月12日涨跌幅排序，非st，2022年10月12日竞价量",
"2022年10月13日_上市天数，2022年10月13日竞价实际换手率大于1%，2022年10月13日竞价涨幅，2022年10月12日成交量，2022年10月13日竞价换手率，2022年10月13日竞价量比，主板，2022年10月13日竞价额，2022年10月13日涨跌幅排序，非st，2022年10月13日竞价量",
"2022年10月14日_上市天数，2022年10月14日竞价实际换手率大于1%，2022年10月14日竞价涨幅，2022年10月13日成交量，2022年10月14日竞价换手率，2022年10月14日竞价量比，主板，2022年10月14日竞价额，2022年10月14日涨跌幅排序，非st，2022年10月14日竞价量",
"2022年10月17日_上市天数，2022年10月17日竞价实际换手率大于1%，2022年10月17日竞价涨幅，2022年10月14日成交量，2022年10月17日竞价换手率，2022年10月17日竞价量比，主板，2022年10月17日竞价额，2022年10月17日涨跌幅排序，非st，2022年10月17日竞价量",
"2022年10月18日_上市天数，2022年10月18日竞价实际换手率大于1%，2022年10月18日竞价涨幅，2022年10月17日成交量，2022年10月18日竞价换手率，2022年10月18日竞价量比，主板，2022年10月18日竞价额，2022年10月18日涨跌幅排序，非st，2022年10月18日竞价量",
"2022年10月19日_上市天数，2022年10月19日竞价实际换手率大于1%，2022年10月19日竞价涨幅，2022年10月18日成交量，2022年10月19日竞价换手率，2022年10月19日竞价量比，主板，2022年10月19日竞价额，2022年10月19日涨跌幅排序，非st，2022年10月19日竞价量",
"2022年10月20日_上市天数，2022年10月20日竞价实际换手率大于1%，2022年10月20日竞价涨幅，2022年10月19日成交量，2022年10月20日竞价换手率，2022年10月20日竞价量比，主板，2022年10月20日竞价额，2022年10月20日涨跌幅排序，非st，2022年10月20日竞价量",
"2022年10月21日_上市天数，2022年10月21日竞价实际换手率大于1%，2022年10月21日竞价涨幅，2022年10月20日成交量，2022年10月21日竞价换手率，2022年10月21日竞价量比，主板，2022年10月21日竞价额，2022年10月21日涨跌幅排序，非st，2022年10月21日竞价量",
"2022年10月24日_上市天数，2022年10月24日竞价实际换手率大于1%，2022年10月24日竞价涨幅，2022年10月21日成交量，2022年10月24日竞价换手率，2022年10月24日竞价量比，主板，2022年10月24日竞价额，2022年10月24日涨跌幅排序，非st，2022年10月24日竞价量",
"2022年10月25日_上市天数，2022年10月25日竞价实际换手率大于1%，2022年10月25日竞价涨幅，2022年10月24日成交量，2022年10月25日竞价换手率，2022年10月25日竞价量比，主板，2022年10月25日竞价额，2022年10月25日涨跌幅排序，非st，2022年10月25日竞价量",
"2022年10月26日_上市天数，2022年10月26日竞价实际换手率大于1%，2022年10月26日竞价涨幅，2022年10月25日成交量，2022年10月26日竞价换手率，2022年10月26日竞价量比，主板，2022年10月26日竞价额，2022年10月26日涨跌幅排序，非st，2022年10月26日竞价量",
"2022年10月27日_上市天数，2022年10月27日竞价实际换手率大于1%，2022年10月27日竞价涨幅，2022年10月26日成交量，2022年10月27日竞价换手率，2022年10月27日竞价量比，主板，2022年10月27日竞价额，2022年10月27日涨跌幅排序，非st，2022年10月27日竞价量",
"2022年10月28日_上市天数，2022年10月28日竞价实际换手率大于1%，2022年10月28日竞价涨幅，2022年10月27日成交量，2022年10月28日竞价换手率，2022年10月28日竞价量比，主板，2022年10月28日竞价额，2022年10月28日涨跌幅排序，非st，2022年10月28日竞价量",
"2022年10月31日_上市天数，2022年10月31日竞价实际换手率大于1%，2022年10月31日竞价涨幅，2022年10月28日成交量，2022年10月31日竞价换手率，2022年10月31日竞价量比，主板，2022年10月31日竞价额，2022年10月31日涨跌幅排序，非st，2022年10月31日竞价量",
"2022年11月1日_上市天数，2022年11月1日竞价实际换手率大于1%，2022年11月1日竞价涨幅，2022年10月31日成交量，2022年11月1日竞价换手率，2022年11月1日竞价量比，主板，2022年11月1日竞价额，2022年11月1日涨跌幅排序，非st，2022年11月1日竞价量",
"2022年11月2日_上市天数，2022年11月2日竞价实际换手率大于1%，2022年11月2日竞价涨幅，2022年11月1日成交量，2022年11月2日竞价换手率，2022年11月2日竞价量比，主板，2022年11月2日竞价额，2022年11月2日涨跌幅排序，非st，2022年11月2日竞价量",
"2022年11月3日_上市天数，2022年11月3日竞价实际换手率大于1%，2022年11月3日竞价涨幅，2022年11月2日成交量，2022年11月3日竞价换手率，2022年11月3日竞价量比，主板，2022年11月3日竞价额，2022年11月3日涨跌幅排序，非st，2022年11月3日竞价量",
"2022年11月4日_上市天数，2022年11月4日竞价实际换手率大于1%，2022年11月4日竞价涨幅，2022年11月3日成交量，2022年11月4日竞价换手率，2022年11月4日竞价量比，主板，2022年11月4日竞价额，2022年11月4日涨跌幅排序，非st，2022年11月4日竞价量",
"2022年11月7日_上市天数，2022年11月7日竞价实际换手率大于1%，2022年11月7日竞价涨幅，2022年11月4日成交量，2022年11月7日竞价换手率，2022年11月7日竞价量比，主板，2022年11月7日竞价额，2022年11月7日涨跌幅排序，非st，2022年11月7日竞价量",
"2022年11月8日_上市天数，2022年11月8日竞价实际换手率大于1%，2022年11月8日竞价涨幅，2022年11月7日成交量，2022年11月8日竞价换手率，2022年11月8日竞价量比，主板，2022年11月8日竞价额，2022年11月8日涨跌幅排序，非st，2022年11月8日竞价量",
"2022年11月9日_上市天数，2022年11月9日竞价实际换手率大于1%，2022年11月9日竞价涨幅，2022年11月8日成交量，2022年11月9日竞价换手率，2022年11月9日竞价量比，主板，2022年11月9日竞价额，2022年11月9日涨跌幅排序，非st，2022年11月9日竞价量",
"2022年11月10日_上市天数，2022年11月10日竞价实际换手率大于1%，2022年11月10日竞价涨幅，2022年11月9日成交量，2022年11月10日竞价换手率，2022年11月10日竞价量比，主板，2022年11月10日竞价额，2022年11月10日涨跌幅排序，非st，2022年11月10日竞价量",
"2022年11月11日_上市天数，2022年11月11日竞价实际换手率大于1%，2022年11月11日竞价涨幅，2022年11月10日成交量，2022年11月11日竞价换手率，2022年11月11日竞价量比，主板，2022年11月11日竞价额，2022年11月11日涨跌幅排序，非st，2022年11月11日竞价量",
"2022年11月14日_上市天数，2022年11月14日竞价实际换手率大于1%，2022年11月14日竞价涨幅，2022年11月11日成交量，2022年11月14日竞价换手率，2022年11月14日竞价量比，主板，2022年11月14日竞价额，2022年11月14日涨跌幅排序，非st，2022年11月14日竞价量",
"2022年11月15日_上市天数，2022年11月15日竞价实际换手率大于1%，2022年11月15日竞价涨幅，2022年11月14日成交量，2022年11月15日竞价换手率，2022年11月15日竞价量比，主板，2022年11月15日竞价额，2022年11月15日涨跌幅排序，非st，2022年11月15日竞价量",
"2022年11月16日_上市天数，2022年11月16日竞价实际换手率大于1%，2022年11月16日竞价涨幅，2022年11月15日成交量，2022年11月16日竞价换手率，2022年11月16日竞价量比，主板，2022年11月16日竞价额，2022年11月16日涨跌幅排序，非st，2022年11月16日竞价量",
"2022年11月17日_上市天数，2022年11月17日竞价实际换手率大于1%，2022年11月17日竞价涨幅，2022年11月16日成交量，2022年11月17日竞价换手率，2022年11月17日竞价量比，主板，2022年11月17日竞价额，2022年11月17日涨跌幅排序，非st，2022年11月17日竞价量",
"2022年11月18日_上市天数，2022年11月18日竞价实际换手率大于1%，2022年11月18日竞价涨幅，2022年11月17日成交量，2022年11月18日竞价换手率，2022年11月18日竞价量比，主板，2022年11月18日竞价额，2022年11月18日涨跌幅排序，非st，2022年11月18日竞价量",
"2022年11月21日_上市天数，2022年11月21日竞价实际换手率大于1%，2022年11月21日竞价涨幅，2022年11月18日成交量，2022年11月21日竞价换手率，2022年11月21日竞价量比，主板，2022年11月21日竞价额，2022年11月21日涨跌幅排序，非st，2022年11月21日竞价量",
"2022年11月22日_上市天数，2022年11月22日竞价实际换手率大于1%，2022年11月22日竞价涨幅，2022年11月21日成交量，2022年11月22日竞价换手率，2022年11月22日竞价量比，主板，2022年11月22日竞价额，2022年11月22日涨跌幅排序，非st，2022年11月22日竞价量"]
    for i in ques_list:
        main(i)
    # main(random.choice(ques_list))
    # main(ques_list[-1])
    # file_object1 = open("liti7.txt", 'r', encoding='UTF-8')
    # try:
    #     while True:
    #         line = file_object1.readline()
    #         if line:
    #             final_res_list.append(line)
    #         else:
    #             break
    # finally:
    #     file_object1.close()
    # #
    # # y_list = []
    # # s_list = []
    # # count = 0
    # print(len(final_res_list))
    # a =[]
    # b=[]
    # for i in final_res_list:
    #     data_list = eval(i.strip())
    #     # at_list = list(filter(at, data_list))
    #     # at_list = [d for d in data_list if d["竞价量"] * d["竞价换手率"] / d["昨日成交量"] > 0.01 and d['竞价涨幅']<8
    #     #            and d['竞价量比']/d['竞价换手率']*d['竞价量']/d['昨日成交量']<1000] #106 72
    #     at_list = [d for d in data_list if d["竞价量"] * d["竞价换手率"] / d["昨日成交量"] > 0.01 and d['竞价涨幅'] >1 and d['竞价涨幅'] <8
    #                and d['竞价量比']/d['竞价换手率']*d['竞价量']/d['昨日成交量']<1000] # 107 71
    #
    #     at_list.sort(key=lambda x: (x['竞价额'] * x["竞价量比"] * x["昨日成交量"] / x["竞价量"]/x["竞价换手率"]), reverse=True) # 104 74
        # for a in at_list:
        #     a['竞价量比*竞价量/昨日成交量/竞价换手率']= a["竞价量比"]*a["竞价量"] / a["昨日成交量"]/a['竞价换手率']
        #     a['竞价量比*昨日成交量/竞价量/竞价换手率']= a["竞价量比"]*a["昨日成交量"] / a["竞价量"]/a['竞价换手率']
        #     a_list.append(a)
        # file = codecs.open('liti7.txt', 'a', 'utf-8')
        # file.writelines(str(a_list) + "\n")
        # at_list.sort(key=lambda x: (x['竞价额'] * x["竞价量比"] * x["竞价换手率"] * x["竞价量"] / x["昨日成交量"]), reverse=True) # 89 88
        # at_list.sort(key=lambda x: (x['竞价额'] * x["竞价量比"] * x["竞价换手率"]), reverse=True) # 94 83
        # at_list.sort(key=lambda x: (x["竞价量比"] * x["竞价换手率"]), reverse=True) # 87 90
        # at_list.sort(key=lambda x: (x["竞价换手率"]),  reverse=True) # 97 85
        # at_list.sort(key=lambda x: (x["竞价换手率"]), reverse=True) # 97 85
        # if len(at_list)>0:
        #     if at_list[0]['当日涨幅']>9:
        #         print("++"+str(at_list))
        #     else:
        #         print("--"+str(at_list))
        # for d in at_list:
            #print(d)
            # if (d["竞价量"] * d["竞价换手率"] / d["昨日成交量"]) > 0.01:
            #     print(d['竞价换手率'])
            # if d['当日涨幅']>9:
            #     print(d)
                # now_date = d['日期'].replace("年","-").replace("月","-").replace("日","")
                # print("当日："+now_date+",昨日："+str(get_previous_workday(2022,int(now_date.split("-")[1]),int(now_date.split("-")[2])))+"，名称："+d['名称'])
            #     a.append(d['竞价量比']/d['竞价换手率']*d['昨日成交量']/d['竞价量'])
            # else:
            #     b.append(d['竞价量比']/d['竞价换手率']*d['昨日成交量']/d['竞价量'])

    # a.sort()
    # b.sort()
    # print(a)
    # print(b)
        # data_list.sort(key=lambda x: (float(x["当日涨幅"])),reverse=True)
        # if data_list[0]['当日涨幅']<9:
        #     print(data_list)
        # for j in data_list:
        #     if float(j["当日涨幅"]) > 9:
        #         y_list.append(i)
        # elif float(data_list["当日涨幅"]) < 0:
        #     s_list.append(i)
        # if data_list["当日涨幅"]<data_list["竞价涨幅"]:
        #     print(i)
    # print(len(y_list))
    # print(len(s_list))
    # 判断每一天都有涨停

    # 判断去除(wencai["竞价量"] * wencai["竞价换手率"] / wencai["昨日成交量"]) > 0.01每一天都有涨停
    # 判断去除    res_list = [i for i in res_list if
    #                 (float(i["竞价量"]) * float(i["竞价换手率"]) / float(i["昨日成交量"])) > 0.01 and float(i["竞价换手率"]) < 2]每一天都有涨停
    # 寻找必涨停模式
