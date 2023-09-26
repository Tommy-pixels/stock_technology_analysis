#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2021/9/12 18:29
Desc: 巨潮资讯-数据中心-评级预测-投资评级
http://webapi.cninfo.com.cn/#/thematicStatistics?name=%E6%8A%95%E8%B5%84%E8%AF%84%E7%BA%A7
"""
import time
from py_mini_racer import py_mini_racer
import requests
import pandas as pd

js_str = """
    function mcode(input) {  
                var keyStr = "ABCDEFGHIJKLMNOP" + "QRSTUVWXYZabcdef" + "ghijklmnopqrstuv"   + "wxyz0123456789+/" + "=";  
                var output = "";  
                var chr1, chr2, chr3 = "";  
                var enc1, enc2, enc3, enc4 = "";  
                var i = 0;  
                do {  
                    chr1 = input.charCodeAt(i++);  
                    chr2 = input.charCodeAt(i++);  
                    chr3 = input.charCodeAt(i++);  
                    enc1 = chr1 >> 2;  
                    enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);  
                    enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);  
                    enc4 = chr3 & 63;  
                    if (isNaN(chr2)) {  
                        enc3 = enc4 = 64;  
                    } else if (isNaN(chr3)) {  
                        enc4 = 64;  
                    }  
                    output = output + keyStr.charAt(enc1) + keyStr.charAt(enc2)  
                            + keyStr.charAt(enc3) + keyStr.charAt(enc4);  
                    chr1 = chr2 = chr3 = "";  
                    enc1 = enc2 = enc3 = enc4 = "";  
                } while (i < input.length);  
          
                return output;  
            }  
"""


def stock_rank_forecast_cninfo(date: str = "20210910") -> pd.DataFrame:
    """
    巨潮资讯-数据中心-评级预测-投资评级
    http://webapi.cninfo.com.cn/#/thematicStatistics?name=%E6%8A%95%E8%B5%84%E8%AF%84%E7%BA%A7
    :param date: 查询日期
    :type date: str
    :return: 投资评级
    :rtype: pandas.DataFrame
    """
    url = "http://webapi.cninfo.com.cn/api/sysapi/p_sysapi1089"
    params = {"tdate": "-".join([date[:4], date[4:6], date[6:]])}
    random_time_str = str(int(time.time()))
    js_code = py_mini_racer.MiniRacer()
    js_code.eval(js_str)
    mcode = js_code.call("mcode", random_time_str)
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Content-Length": "0",
        "Host": "webapi.cninfo.com.cn",
        "mcode": mcode,
        "Origin": "http://webapi.cninfo.com.cn",
        "Pragma": "no-cache",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://webapi.cninfo.com.cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    r = requests.post(url, params=params, headers=headers)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["records"])
    temp_df.columns = [
        "证券简称",
        "发布日期",
        "前一次投资评级",
        "评级变化",
        "目标价格-上限",
        "是否首次评级",
        "投资评级",
        "研究员名称",
        "研究机构简称",
        "目标价格-下限",
        "证券代码",
    ]
    temp_df = temp_df[[
        "证券代码",
        "证券简称",
        "发布日期",
        "研究机构简称",
        "研究员名称",
        "投资评级",
        "是否首次评级",
        "评级变化",
        "前一次投资评级",
        "目标价格-下限",
        "目标价格-上限",
    ]]
    temp_df["目标价格-上限"] = pd.to_numeric(temp_df["目标价格-上限"], errors="coerce")
    temp_df["目标价格-下限"] = pd.to_numeric(temp_df["目标价格-下限"], errors="coerce")
    return temp_df


if __name__ == "__main__":
    stock_rank_forecast_cninfo_df = stock_rank_forecast_cninfo(date="20210907")
    print(stock_rank_forecast_cninfo_df)
