import time
from functools import partial
import subprocess

subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs
import requests
import re
import json

res_list = []
ques = "上市天数，今日竞价实际换手率大于1%，今日竞价涨幅，昨日成交量，今日竞价换手率，今日竞价量比，去除今日开盘价等于涨停价，主板，今日竞价额，今日涨跌幅排序"


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
    res = requests.post(url, headers=new_headers, data=json.dumps(data))
    time.sleep(10)
    origin_res_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][0]["data"]["datas"]
    res_list = []
    for origin_res in origin_res_list:
        try:

            res_json = json.loads(json.dumps(origin_res, ensure_ascii=False))
            # res_json_sort = sortByKey(res_json)
            # res_info = [i for i in res_json_sort.values()]
            res_json_new = {}
            for item in res_json.items():
                key = re.sub(r"\(.*?\)|\{.*?\}|\[.*?\]", "", item[0])
                value = item[1]
                res_json_new[key] = value
            wencai = {}

            wencai['日期'] = quest.split("_")[0]
            wencai['竞价额'] = float(res_json_new["竞价金额"])
            if "成交量" in res_json_new.keys():
                wencai['昨日成交量'] = float(res_json_new["成交量"])
            else:
                wencai['昨日成交量'] = 1
            wencai['竞价量'] = float(res_json_new["竞价量"])
            wencai['竞价换手率'] = float(res_json_new["分时换手率"])
            wencai['昨日振幅'] = float(res_json_new["振幅"])
            wencai['竞价量比'] = float(res_json_new["分时量比"])
            wencai['竞价涨幅'] = float(res_json_new["竞价涨幅"])
            wencai['当日涨幅'] = float(res_json_new["涨跌幅:前复权"])
            wencai['名称'] = res_json_new["股票简称"]
            if wencai['昨日振幅'] > 0 and wencai['昨日振幅'] < 15 and wencai['竞价额'] > 500 * 10000 and wencai['竞价量'] / wencai[
                '昨日成交量'] > 0.04 \
                    and wencai['竞价量'] / wencai['昨日成交量'] < 0.4 and wencai['竞价涨幅'] < 9 and wencai['竞价涨幅'] > -2:
                res_list.append(wencai)
        except Exception as e:
            print(e)

    # if "." in wencai['昨日成交量']:
    #     wencai['昨日成交量'] = float(res_info[4][0:7]) * 100000000
    #     if float(res_info[-6]) * float(wencai['竞价换手率']) > 1 and float(wencai['竞价量比']) > 1 and float(
    #             wencai['竞价量比']) < 30 and \
    #             wencai['竞价额'] > 10000000 and res_info[2] > 50:
    #         wencai['当日涨幅'] = res_info[-11]
    #         res_list.append(wencai)
    # res_list = [i for i in res_list if (float(i["竞价量"]) * float(i["竞价换手率"]) / float(i["昨日成交量"])) > 0.01]
    res_list.sort(key=lambda x: (float(x["竞价量"]) * float(x["竞价换手率"]) * float(x["竞价量比"]) / float(x["昨日成交量"])),
                  reverse=True)
    if len(res_list) > 0:
        print("++" + str(res_list[0]))
        if res_list[0]['当日涨幅'] > 9:
            print("涨停")


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


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    ques_list = [
        "2022年6月14日_主板，非st，上市天数，流通市值小于150亿，2022年6月13日首板，2022年6月13日振幅，2022年6月14日竞价强度>7，2022年6月14日竞价换手率，2022年6月14日竞价量，2022年6月13日成交量，2022年6月14日竞价额，2022年6月14日竞价量比",
    ]
    for i in ques_list:
        main(i)
    # print(len(res_list))
    # y_list = []
    # s_list = []
    # for i in res_list:
    #     if i["当日涨幅"] > 9:
    #         y_list.append(i)
    #     elif i["当日涨幅"] < 0:
    #         s_list.append(i)
    # print(len(y_list))
    # print(len(s_list))
