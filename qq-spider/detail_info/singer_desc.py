import requests
import modles
import os
from xml.etree import ElementTree

headers = {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'zh-CN,zh;q=0.8',
           'cache-control': 'no-cache', 'pragma': 'pragma:no-cache',
           'referer': 'https://c.y.qq.com/xhr_proxy_utf8.html',
           'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/60.0.3112.113 Safari/537.36'}

SINGER_DESC_URL = 'https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_singer_desc.fcg?' \
                  'singermid=%s&utf8=1&outCharset=utf-8&format=xml'


def write_xml_file(singer_mid, response_content):
    curr_path = os.getcwd()
    # linux file access style
    xml_full_path_name = curr_path + '/detail_info/xmlfile/' + singer_mid + '.xml'
    # local file access style
    # xml_full_path_name = curr_path + '/xmlfile/' + singer_mid + '.xml'
    f = open(xml_full_path_name, 'w')
    f.write(response_content)
    f.close

    return xml_full_path_name


def get_singer_desc_info(singer_mid, singer_id):
    req_url = SINGER_DESC_URL % singer_mid
    try:
        r = requests.get(req_url, headers=headers)
    except Exception as e:
        r = None
        print(e)
    if r is None:
        return
    response_content = r.text
    # print(response_content)

    xml_full_path_name = write_xml_file(singer_mid, response_content)

    try:
        tree = ElementTree.ElementTree(file=xml_full_path_name)
    except Exception as e:
        tree = None
        print(e)

    if tree is None:
        os.remove(xml_full_path_name)
        return

    root = tree.getroot()
    singer_desc_dict = {'singer_homeplace': None}
    singer_desc_dict['singer_desc'] = None
    singer_desc_dict['singer_nationality'] = None
    singer_desc_dict['singer_constellation'] = None
    singer_desc_dict['singer_birth'] = None
    for r_item in root:
        if 'data' != r_item.tag:
            continue

        data = r_item
        for d_item in data:
            if 'info' != d_item.tag:
                continue

            info = d_item
            for i_item in info:
                if 'desc' == i_item.tag:
                    singer_desc = i_item.text
                    singer_desc_dict['singer_desc'] = singer_desc
                elif 'basic' == i_item.tag:
                    basic = i_item

                    for item in basic:
                        key_val = item[0].text
                        value_val = item[1].text
                        if '国籍' == key_val:
                            singer_desc_dict['singer_nationality'] = value_val
                        elif '出生地' == key_val:
                            singer_desc_dict['singer_homeplace'] = value_val
                        elif '星座' == key_val:
                            singer_desc_dict['singer_constellation'] = value_val
                        elif '出生日期' == key_val:
                            singer_desc_dict['singer_birth'] = value_val

    singer_desc_dict['singer_id'] = singer_id
    try:
        modles.insert_record(singer_desc_dict, 'singerdetail')
        os.remove(xml_full_path_name)
        modles.update_singer_classify(singer_id)
    except Exception as e:
        print(e)


# get_singer_desc_info('003vyG9q2klWs4', 4351)
