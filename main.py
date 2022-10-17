# -*- coding: utf-8 -*-

from encodings import utf_8
import json
import requests
import hashlib
import time
import csv
import os.path
timestamp = str(time.time()).split('.')[0]

def crypo_sha256(timestamp):
    e = str(timestamp)
    a = '23y0ufFl5YxIyGrI8hWRUZmKkvtSjLQA'
    i = '123456789abcdefg'
    s = 'zdww'
    ts = (e + a + i + e).encode('utf-8')
    r = hashlib.sha256(ts).hexdigest().upper()
    return r


def get_x_wif_signature(timestamp):
    ts = (str(timestamp) + 'fTN2pfuisxTavbTuYVSsNJHetwq5bJvCQkjjtiLM2dCratiA' +
           str(timestamp)).encode('utf-8')
    r = hashlib.sha256(ts).hexdigest().upper()
    return r


def get_risk_zones():
    headers = {
        'x-wif-nonce': 'QkjjtiLM2dCratiA',
        'x-wif-signature': get_x_wif_signature(timestamp),
        'x-wif-timestamp': str(timestamp),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62',
        'x-wif-paasid': 'smt-application',
        'Content-Type': 'application/json; charset=UTF-8',
    }

    data = {
        'appId': 'NcApplication',
        'paasHeader': 'zdww',
        'timestampHeader': str(timestamp),
        'nonceHeader': '123456789abcdefg',
        'signatureHeader': crypo_sha256(timestamp),
        'key': '3C502C97ABDA40D0A60FBEE50FAAD1DA'}
    district_dict = {}

    try:
        res = requests.post('http://bmfw.www.gov.cn/bjww/interface/interfaceJson',
                            headers=headers, data=json.dumps(data), verify=False)
        if res.status_code == 200:
            res_json = res.json()
            write_json('data.json', res_json)
            msg = '目前有高风险地区{}个，中风险地区{}个，以下所列地区为中高风险地区。\n'.format(
                res_json['data']['hcount'], res_json['data']['mcount'])
            print(msg)
            write_csv('data.csv', res_json['data'])
            for i in range(2):
                if i == 0:
                    dict_to_do = res_json['data']['highlist']
                else:
                    dict_to_do = res_json['data']['middlelist']
                for district in dict_to_do:
                    province = district['province']
                    city = district['city']
                    county = district['county']
                    if province not in district_dict.keys():
                        district_dict[province] = {city: [county]}
                    else:
                        city_dict = district_dict[province]
                        if city not in city_dict.keys():
                            district_dict[province][city] = [county]
                        else:
                            if county not in city_dict[city]:
                                district_dict[province][city] = district_dict[province][city]+[county]
            print(district_dict)
            for province in district_dict.keys():
                msg = msg+'\n\n《{}》\n\n'.format(province)
                province_dict = district_dict[province]
                for city in province_dict.keys():
                    msg = msg + '【{}】'.format(city)
                    county_list_str = ''
                    county_list = province_dict[city]
                    for county in county_list:
                        county_list_str = county_list_str + county+'、'
                    if county_list_str[-1] == '、':
                        county_list_str = county_list_str[:len(
                            county_list_str)-1]
                    msg = msg+county_list_str+'\n'
                msg = msg+'\n'
            print(msg)
            return msg
        else:
            print(res.status_code)
            return res.status_code
    except Exception as e:
        return '{}'.format(e)


def write_csv(filename, data):
    if os.path.isfile(filename) == False:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(['date', '风险', '省','市','区'])
       
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        date = data['end_update_time'].split(' ')[0]
        for risk in ['高','中', '低']:
            if risk == '高':
                dataToWrite = data['highlist']
            elif risk == '中':
                dataToWrite = data['middlelist']
            else:
                dataToWrite = data['lowlist']
            for row_data in dataToWrite:
                spamwriter.writerow([date, risk, row_data['province'], row_data['city'], row_data['county']])
    
def write_json(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False)
        
def job():
    res = get_risk_zones()


if __name__ == '__main__':    
    job()
