import json
import re
import time

import execjs
import requests
# import tushare as ts

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
        "question": quest,
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
    print("--"+quest)
    res = requests.post(url, headers=new_headers, data=json.dumps(data))
    # time.sleep(10)
    hsl_dict = {}
    hsl_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][0]["data"]["datas"]
    # ztfdl_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][1]["data"]["datas"]
    # zdf_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][2]["data"]["datas"]
    # cje_list = res.json()["data"]["answer"][0]["txt"][0]["content"]["components"][3]["data"]["datas"]
    h_list = []
    time.sleep(50)
    if len(hsl_list) > 0:
        res_list = []
        for origin_res in hsl_list:
            try:
                res_json = json.loads(json.dumps(origin_res, ensure_ascii=False))
                # res_json_new = {}
                # for item in res_json.items():
                #     key = re.sub(r"\(.*?\)|\{.*?\}|\[.*?\]", "", item[0])
                #     value = item[1]
                #     res_json_new[key] = value
                wencai = {}
                wencai['名称'] = res_json["名称"]
                wencai['昨日换手率'] = float(res_json["换手率"])
                if res_json['涨停封单量'] == '暂无':
                    wencai['昨日封单量'] = 0
                else:
                    wencai['昨日封单量'] = float(res_json["涨停封单量"])
                wencai['昨日涨跌幅'] = float(res_json["涨跌幅:前复权"])
                wencai['昨日成交额'] = float(res_json["成交额"])
                # for z in ztfdl_list:
                #     if z['名称'] == wencai['名称']:
                #         if '涨停封单量' in z.keys():
                #             if  z['涨停封单量'] == '暂无':
                #                 wencai['昨日封单量'] = 0
                #             else:
                #                 wencai['昨日封单量'] = float(z['涨停封单量'])
                # for z in zdf_list:
                #     if z['名称'] == wencai['名称']:
                #         if '涨跌幅:前复权' in z.keys():
                #             wencai['昨日涨跌幅']=float(z['涨跌幅:前复权'])
                # for z in cje_list:
                #     if z['名称'] == wencai['名称']:
                #         if '成交额' in z.keys():
                #             wencai['昨日成交额']=float(z['成交额'])
                h_list.append(wencai)
            except Exception as e:
                print(e)
        return h_list

def main(quest):
    sever_time = get_TOKEN_SERVER_TIME()
    hexin_v = get_hexin_v(sever_time)
    return run(quest, hexin_v)

if __name__ == '__main__':
    final_res_list = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }
    file_object1 = open("liti7.txt", 'r', encoding='UTF-8')
    try:
        while True:
            line = file_object1.readline()
            if line:
                final_res_list.append(line)
            else:
                break
    finally:
        file_object1.close()
    for i in final_res_list:
        data_list = eval(i.strip())

        at_list = [d for d in data_list if d["竞价量"] * d["竞价换手率"] / d["昨日成交量"] > 0.01 and d['竞价涨幅'] >1 and d['竞价涨幅'] <8
                       and d['竞价量比']/d['竞价换手率']*d['竞价量']/d['昨日成交量']<1000]
        at_list.sort(key=lambda x: (x['竞价额'] * x["竞价量比"] * x["昨日成交量"] / x["竞价量"]/x["竞价换手率"]), reverse=True) # 104 74

        a_list = []
        if len(at_list)>0:
            # if at_list[0]['当日涨幅']<9:
            # print(json.dumps(at_list, indent=2, ensure_ascii=False))
            h_list = main(at_list[0]['昨日'].replace('-', '年', 1).replace('-', '月', 1) + "日" + ','.join(
                    [d['名称'] for d in at_list]) + "换手率,封单量，涨跌幅，成交额")
            print(h_list)
            for d in at_list:
                mc = d['名称']
                for f in h_list:
                    if f['名称'] == d['名称']:
                        d['昨日封单量'] = f['昨日封单量']
                        d['昨日涨跌幅'] = f['昨日涨跌幅']
                        d['昨日成交额'] = f['昨日成交额']
                        d['昨日换手率'] = f['昨日换手率']
                        a_list.append(d)
            print(a_list)


        # if len(at_list)>0:
        #     if at_list[0]['当日涨幅']>9:
        #         print("++"+str(at_list))
        #     else:
        #         print("--"+str(at_list))
        #         print(data_list[0]['昨日'].replace('-', '年', 1).replace('-', '月', 1) + "日" + ','.join(
        #             [d['名称'] for d in data_list]) + "换手率,封单量，涨跌幅，成交额")

    # ts.set_token("457edc74bbfea198938b5b716f4a22a3b596a94593a3906aac42a3ac")
    # pro=ts.pro_api()
    # df = pro.daily(ts_code='600605.SH', start_date='20221010', end_date='20221010')

    # df = pro.daily_basic(ts_code='', trade_date='20180726',
    #                      fields='ts_code,trade_date,turnover_rate,volume_ratio,pe,pb')
    # df.to_csv('./600605.SZ.csv',index=None)