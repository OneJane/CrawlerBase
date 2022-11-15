from functools import partial
import subprocess

subprocess.Popen = partial(subprocess.Popen, encoding='utf-8')
import execjs
import requests
import re
import json

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
    try:
        origin_res_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][0]["data"]["datas"]
        res_list = []
        for origin_res in origin_res_list:
            res_json = json.loads(json.dumps(origin_res, ensure_ascii=False))
            res_json_sort = sortByKey(res_json)
            res_info = [i for i in res_json_sort.values()]

            wencai = {}
            wencai['名称'] = res_info[-2]
            wencai['竞价换手率'] = res_info[4][0:5]
            wencai['竞价量比'] = res_info[5]
            wencai['竞价额'] = res_info[-4]
            wencai['竞价涨幅'] = res_info[-6]
            wencai['竞价量'] = res_info[-5]
            wencai['昨日成交量'] = res_info[6]
            if "." in wencai['昨日成交量']:
                wencai['昨日成交量'] = float(res_info[4][0:7]) * 100000000
                if float(res_info[-6]) * float(wencai['竞价换手率']) > 1 and float(wencai['竞价量比']) > 1 and float(
                        wencai['竞价量比']) < 30 and \
                        wencai['竞价额'] > 10000000 and res_info[2] > 50:
                    wencai['当日涨幅'] = res_info[-11]
                    res_list.append(wencai)
        res_list = [i for i in res_list if (float(i["竞价量"]) * float(i["竞价换手率"]) / float(i["昨日成交量"])) > 0.01]
        res_list.sort(key=lambda x: (float(x["竞价涨幅"]) * float(x["竞价换手率"]) * float(x["竞价额"]) * float(x["竞价量比"])),
                      reverse=True)
        print(str(res_list))
    except Exception as e:
        print(e)

def sortByKey(dictVar):
    sortedTuple = sorted(dictVar.items(), key=lambda x: x[0])
    sortedDict = {}
    for tupleItem in sortedTuple:
        sortedDict[tupleItem[0]] = tupleItem[1]
    return sortedDict

def main():
    sever_time = get_TOKEN_SERVER_TIME()
    hexin_v = get_hexin_v(sever_time)
    run(hexin_v)


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    main()