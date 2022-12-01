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
                        and (wencai["竞价量"] * wencai["竞价换手率"] / wencai["昨日成交量"]) > 0.01 and float(wencai['竞价量比']) > 1 and float(wencai['竞价量比']) < 30 :

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
    ques_list = ["2022年6月7日_上市天数，2022年6月7日竞价实际换手率大于1%，2022年6月7日竞价涨幅，2022年6月6日成交量，2022年6月7日竞价换手率，2022年6月7日竞价量比，主板，2022年6月7日竞价额，2022年6月7日涨跌幅排序，非st，2022年6月7日竞价量",]
    for i in ques_list:
        main(i)
    # main(random.choice(ques_list))
    # main(ques_list[-1])
    # file_object1 = open("liti8.txt", 'r', encoding='UTF-8')
    # try:
    #     while True:
    #         line = file_object1.readline()
    #         if line:
    #             final_res_list.append(line)
    #         else:
    #             break
    # finally:
    #     file_object1.close()
    # # #
    # y_list = []
    # s_list = []
    # # # count = 0
    # # print(len(final_res_list))
    # # a =[]
    # # b=[]
    # for i in final_res_list:
    #     data_list = eval(i.strip())
    #     # at_list = list(filter(at, data_list))
    # #     # at_list = [d for d in data_list if d["竞价量"] * d["竞价换手率"] / d["昨日成交量"] > 0.01 and d['竞价涨幅']<8
    # #     #            and d['竞价量比']/d['竞价换手率']*d['竞价量']/d['昨日成交量']<1000] #106 72
    # #     at_list = [d for d in data_list if d["竞价量"] * d["竞价换手率"] / d["昨日成交量"] > 0.01 and d['竞价涨幅'] >1 and d['竞价涨幅'] <8
    # #                and d['竞价量比']/d['竞价换手率']*d['竞价量']/d['昨日成交量']<1000] # 107 71
    #     at_list = [d for d in data_list if d['竞价未匹配金额']<20000000
    #                and d['昨日涨跌幅']>9 and d['昨日换手率']>0.5
    #                and d['竞价量']/d['昨日封单量']*d['竞价量比']>2 and d['竞价量']/d['昨日封单量']>0.1 and d['竞价量']/d['昨日封单量']*d['昨日换手率']<100
    #                 and d['竞价额']/d['昨日成交额']*d['竞价量比']>0.3
    #                and d['竞价换手率']*d['昨日换手率']
    #                # and d['竞价额']/d["昨日成交额"]>0.3
    #                ]
    # #
    #     at_list.sort(key=lambda d: (d['竞价额'] * d["竞价量比"] * d["昨日成交量"] / d["竞价量"]/d["竞价换手率"]), reverse=True) # 104 74
    #     # for a in at_list:
    #     #     a['竞价量比*竞价量/昨日成交量/竞价换手率']= a["竞价量比"]*a["竞价量"] / a["昨日成交量"]/a['竞价换手率']
    #     #     a['竞价量比*昨日成交量/竞价量/竞价换手率']= a["竞价量比"]*a["昨日成交量"] / a["竞价量"]/a['竞价换手率']
    #     #     a_list.append(a)
    #     # file = codecs.open('liti7.txt', 'a', 'utf-8')
    #     # file.writelines(str(a_list) + "\n")
    #     # at_list.sort(key=lambda x: (x['竞价额'] * x["竞价量比"] * x["竞价换手率"] * x["竞价量"] / x["昨日成交量"]), reverse=True) # 89 88
    #     # at_list.sort(key=lambda x: (x['竞价额'] * x["竞价量比"] * x["竞价换手率"]), reverse=True) # 94 83
    #     # at_list.sort(key=lambda x: (x["竞价量比"] * x["竞价换手率"]), reverse=True) # 87 90
    #     # at_list.sort(key=lambda x: (x["竞价换手率"]),  reverse=True) # 97 85
    #     # at_list.sort(key=lambda x: (x["竞价换手率"]), reverse=True) # 97 85
    #
    #     # 竞价换手率 竞价量比 竞价额 竞价涨幅 竞价量 昨日成交量 当日涨幅 昨日封单量 昨日涨跌幅 昨日成交额 昨日换手率
    #
    #     if len(at_list)>0:
    #         d=at_list[0]
    #         if at_list[0]['当日涨幅']>9:
    #             y_list.append(d["竞价量比"]*d['竞价换手率'])
    #
    #         # print("++" + json.dumps(at_list[0], ensure_ascii=False))
    #         else:
    #             s_list.append(d["竞价量比"]*d['竞价换手率'])

        # print("--" + json.dumps(at_list[0], ensure_ascii=False))


        # for d in at_list:
        #     if d['当日涨幅']>9:
        #         y_list.append(d['昨日成交量']/d["竞价量"]/d["竞价量比"]*d['竞价涨幅'])
        #             # print("++"+str(at_list))
        #             # print("++"+json.dumps(at_list,  ensure_ascii=False))
        #     else:
        #         s_list.append(d['昨日成交量']/d["竞价量"]/d["竞价量比"]*d['竞价涨幅'])

                    # print("--"+str(at_list))
                    # print("--"+json.dumps(at_list,  ensure_ascii=False))

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

    # y_list.sort()
    # s_list.sort()
    # print(y_list)
    # print(s_list)
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
