import json
import re
import time

import execjs
import requests
import tushare as ts

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
    print(quest.split("_")[1])
    res = requests.post(url, headers=new_headers, data=json.dumps(data))

    origin_res_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][0]["data"]["datas"]
    # time.sleep(50)
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


                wencai = {}
                wencai['名称'] = res_json_new["股票简称"]
                wencai['股票代码'] = res_json_new["股票代码"]
            except Exception as e:
                print(e)

def main(quest):
    sever_time = get_TOKEN_SERVER_TIME()
    hexin_v = get_hexin_v(sever_time)
    run(quest, hexin_v)

if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    ts.set_token("457edc74bbfea198938b5b716f4a22a3b596a94593a3906aac42a3ac")
    pro=ts.pro_api()
    # df = pro.daily(ts_code='600605.SH', start_date='20221010', end_date='20221010')

    df = pro.daily_basic(ts_code='', trade_date='20180726',
                         fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pb')
    df.to_csv('./600605.SZ.csv',index=None)