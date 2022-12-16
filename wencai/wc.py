import datetime
from functools import partial
import subprocess

subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs
import requests
import re
import json

from flask import Flask
app = Flask(__name__)
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


def run(hexin_v):
    url = 'http://www.iwencai.com/customized/chart/get-robot-data'
    new_headers = {
        'Content-Type': 'application/json',
        'hexin-v': hexin_v,
        'Referer': 'http://www.iwencai.com/unifiedwap/result?w=20221002%E6%B6%A8%E5%81%9C',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    data = {
        "question": ques,
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
    origin_res_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][0]["data"]["datas"]
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
            wencai['竞价换手率'] = float(res_json_new["分时换手率"])
            wencai['竞价量比'] = float(res_json_new["分时量比"])
            wencai['竞价额'] = float(res_json_new["竞价金额"])
            wencai['竞价涨幅'] = float(res_json_new["竞价涨幅"])
            wencai['竞价量'] = float(res_json_new["竞价量"])
            if "成交量" in res_json_new.keys():
                wencai['昨日成交量'] = float(res_json_new["成交量"])
            else:
                wencai['昨日成交量'] = 1

            if float(wencai['竞价涨幅']) * float(wencai['竞价换手率']) > 1 and float(wencai['竞价量比']) > 1 and float(
                    wencai['竞价量比']) < 30 and wencai['竞价额'] > 10000000 and res_json_new["上市天数"] > 50:
                wencai['当日涨幅'] = float(res_json_new["涨跌幅:前复权"])
                res_list.append(wencai)
        except Exception as e:
             print(e)
    res_list = [d for d in res_list if d["竞价量"] * d["竞价换手率"] / d["昨日成交量"] > 0.01 and d['竞价涨幅'] > 1 and d['竞价涨幅'] < 8
               and d['竞价量比'] / d['竞价换手率'] * d['竞价量'] / d['昨日成交量'] < 1000 and d['竞价换手率']>0.5]
    res_list.sort(key=lambda x: (x['竞价额']*x["竞价量比"]*x["昨日成交量"]/x["竞价量"]/x["竞价换手率"]),
                  reverse=True)
    # print(json.dumps(res_list, indent=2, ensure_ascii=False))
    h_list = []
    if len(res_list)>0:
        q = ','.join([d['名称'] for d in res_list]) + "竞价未匹配金额，昨日的换手率,封单量，涨跌幅，成交额，基本面评分"
        data = {
            "question": q,
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
        try:
            show_type = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][0]["show_type"]
            if show_type == 'bar3':
                # 分开
                jjwpp_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][0]["data"]["datas"]
                ztfdl_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][1]["data"]["datas"]
                h_list = []
                for h in ztfdl_list:
                    wencai = {}
                    wencai['名称'] = h["名称"]
                    wencai['昨日换手率'] = float(h["换手率"])
                    wencai['昨日涨跌幅'] = float(h["涨跌幅:前复权"])
                    if wencai['昨日涨跌幅'] > 9 and h["涨停封单量"] != '暂无':
                        wencai['昨日封单量'] = float(h["涨停封单量"])
                        wencai['昨日成交额'] = float(h["成交额"])
                        wencai['基本面评分'] = float(h["基本面评分"])
                        h_list.append(wencai)
                for h in h_list:
                    for j in jjwpp_list:
                        if h["名称"] == j["名称"]:
                            h['竞价未匹配金额'] = j['竞价未匹配金额']


            elif show_type == 'tab4':
                hsl_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][0]["tab_list"]
                for r in res_list:
                    wencai = {}

                    for h in hsl_list:

                        if h['tab_name'] == "竞价未匹配金额":
                            for l in h['list'][0]['data']['datas']:
                                if l['名称'] == r['名称']:
                                    wencai['名称'] = l["名称"]
                                    wencai['竞价未匹配金额'] = float(l["竞价未匹配金额"])

                        if h['tab_name'] == "换手率":
                            for l in h['list'][0]['data']['datas']:
                                if l['名称'] == r['名称']:
                                    wencai['名称'] = l["名称"]
                                    wencai['昨日换手率'] = float(l["换手率"])

                        if h['tab_name'] == "涨跌幅:前复权":
                            for l in h['list'][0]['data']['datas']:
                                if l['名称'] == r['名称']:
                                    wencai['名称'] = l["名称"]
                                    wencai['昨日涨跌幅'] = float(l["涨跌幅:前复权"])

                        if h['tab_name'] == "涨跌幅:前复权":
                            for l in h['list'][0]['data']['datas']:
                                if l['名称'] == r['名称']:
                                    wencai['名称'] = l["名称"]
                                    wencai['昨日涨跌幅'] = float(l["涨跌幅:前复权"])

                        if h['tab_name'] == "基本面评分":
                            for l in h['list'][0]['data']['datas']:
                                if l['名称'] == r['名称']:
                                    wencai['名称'] = l["名称"]
                                    wencai['基本面评分'] = float(l["基本面评分"])
                    h_list.append(wencai)
                for w in h_list:
                    if w['昨日涨跌幅'] > 9:
                        for h in hsl_list:
                            if h['tab_name'] == "涨停封单量":
                                for l in h['list'][0]['data']['datas']:
                                    if l['名称'] == w['名称']:
                                        w['名称'] = l["名称"]
                                        w['昨日封单量'] = float(l["涨停封单量"])
                            if h['tab_name'] == "成交额":
                                for l in h['list'][0]['data']['datas']:
                                    if l['名称'] == w['名称']:
                                        w['名称'] = l["名称"]
                                        w['昨日成交额'] = float(l["成交额"])
        except Exception as e:
            res = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][1]['data']['datas'][0]
            # print(json.dumps(res, indent=2, ensure_ascii=False))
            wencai = {}
            wencai['名称'] = res["股票简称"]
            wencai['昨日换手率'] = float(0)
            wencai['昨日涨跌幅'] = float(0)
            wencai['昨日封单量'] = float(0)
            wencai['昨日成交额'] = float(0)
            wencai['竞价未匹配金额'] = float(0)
            wencai['基本面评分'] = float(0)
            h_list.append(wencai)

        if h_list is not None and len(h_list) > 0:
            for d in h_list:
                for f in res_list:
                    if f['名称'] == d['名称']:
                        d['竞价量比'] = f['竞价量比']
                        d['竞价量'] = f['竞价量']
                        d['竞价额'] = f['竞价额']
                        d['竞价换手率'] = f['竞价换手率']
                        d['昨日成交量'] = f['昨日成交量']
                        d['当日涨幅'] = f['当日涨幅']
                        d['竞价涨幅'] = f['竞价涨幅']
                        d['日期'] = datetime.datetime.now().strftime('%Y-%m-%d')

        print("============================================")
        # print(json.dumps(h_list, indent=2, ensure_ascii=False))
        print("============================================")
        res_list = [d for d in h_list if  d['竞价未匹配金额']<20000000
                   and d['竞价未匹配金额'] > -10000000
                   and d['昨日涨跌幅']>9 and d['昨日换手率']>1
                   and d['竞价量']/d['昨日封单量']*d['竞价量比']>2 and d['竞价量']/d['昨日封单量']>0.1 and d['竞价量']/d['昨日封单量']*d['昨日换手率']<100
                    and d['竞价额']/d['昨日成交额']*d['竞价量比']>0.3 and d['基本面评分']>5
                    and d["竞价量比"]*d['竞价涨幅']*d['竞价换手率']/d['昨日换手率']>0.6
                    and d['竞价量'] / d['昨日封单量'] * d['竞价量比'] > 3
                    and d['竞价量'] / d['昨日封单量'] * d['昨日换手率'] / d['竞价涨幅'] > 0.06
                    and d['昨日成交量'] / d['竞价量'] * d['竞价换手率'] * d['竞价涨幅'] > 5
                    and d['竞价量']/d['昨日封单量']<2
                    ]
        res_list.sort(key=lambda x: (x['竞价额'] * x["竞价量比"] * x["昨日成交量"] / x["竞价量"] / x["竞价换手率"]),
                      reverse=True)
        print(json.dumps(res_list, indent=2, ensure_ascii=False))
        return json.dumps(res_list, indent=2, ensure_ascii=False)


def sortByKey(dictVar):
    sortedTuple = sorted(dictVar.items(), key=lambda x: x[0])
    sortedDict = {}
    for tupleItem in sortedTuple:
        sortedDict[tupleItem[0]] = tupleItem[1]
    return sortedDict

@app.route('/')
def main():
    sever_time = get_TOKEN_SERVER_TIME()
    hexin_v = get_hexin_v(sever_time)
    return run(hexin_v)



if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    a_list = main()
    import win32api, win32gui
    ct = win32api.GetConsoleTitle()
    hd = win32gui.FindWindow(0, ct)
    win32gui.ShowWindow(hd, 0)  # 隐藏dos窗
    app.run(host="0.0.0.0", debug=True)
    # res = [
    #       {
    #         "名称": "安奈儿",
    #         "昨日换手率": 48.411131,
    #         "昨日涨跌幅": 10,
    #         "昨日封单量": 765052,
    #         "昨日成交额": 110000000,
    #         "竞价未匹配金额": 5603614,
    #         "基本面评分": 4.4,
    #         "竞价量比": 18.368909832442004,
    #         "竞价量": 1681579.0,
    #         "竞价额": 30453396.0,
    #         "竞价换手率": 1.3793681322444697,
    #         "昨日成交量": 59017706.0,
    #         "当日涨幅": 10.012,
    #         "竞价涨幅": 4.2,
    #         "日期": "2022-12-02"
    #       }
    #     ]
    # res_list = [d for d in h_list if d['竞价未匹配金额'] < 20000000
    #             and d['竞价未匹配金额'] > -10000000
    #             and d['昨日涨跌幅'] > 9 and d['昨日换手率'] > 1
    #             and d['竞价量'] / d['昨日封单量'] * d['竞价量比'] > 2 and d['竞价量'] / d['昨日封单量'] > 0.1 and d['竞价量'] / d['昨日封单量'] * d[
    #                 '昨日换手率'] < 100
    #             and d['竞价额'] / d['昨日成交额'] * d['竞价量比'] > 0.3 and d['基本面评分'] > 5
    #             and d["竞价量比"] * d['竞价涨幅'] * d['竞价换手率'] / d['昨日换手率'] > 0.6
    #             and d['竞价量'] / d['昨日封单量'] * d['竞价量比'] > 3
    #             and d['竞价量'] / d['昨日封单量'] * d['昨日换手率'] / d['竞价涨幅'] > 0.06
    #             and d['昨日成交量'] / d['竞价量'] * d['竞价换手率'] * d['竞价涨幅'] > 5
    #             and d['竞价量'] / d['昨日封单量'] < 2
    #
    #             ]
    # res_list.sort(key=lambda x: (x['竞价额'] * x["竞价量比"] * x["昨日成交量"] / x["竞价量"] / x["竞价换手率"]),
    #               reverse=True)
    # print(json.dumps(res_list, indent=2, ensure_ascii=False))