import requests
from bs4 import BeautifulSoup
import json
import oss2
import modles

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/60.0.3112.113 Safari/537.36'}

ALBUM_INFO_URL = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?albummid=%s&g_tk=5381' \
                 '&jsonpCallback=getAlbumInfoCallback&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8' \
                 '&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'

OSS_SONG_PATH = 'http://source.edian66.com/'
SONG_STORE = 'prosong/'

IMAGE_URL_START = 'http://y.gtimg.cn/music/photo_new/'
IMAGE_NAME_BEG = 'T002R300x300M000'
IMAGE_NAME_END = '.jpg'


# 设置oss
auth = oss2.Auth('LTAIgKpditaGe91a', '0IbKHUZFhz1rOGzXi76PWFjUdLxGT8')
bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com/', 'shujustore')


# 下载歌曲图片
def get_file(r_content, file_name):
    try:
        bucket.put_object(file_name, r_content)
    except Exception as e:
        print('song detail exception:', e)


def get_song_detail(album_mid, singer_id):
    req_url = ALBUM_INFO_URL % album_mid
    try:
        r = requests.get(req_url)
    except Exception as e:
        r = None
        print('song detail exception:', e)

    if r is None or r.status_code != 200:
        return init_song_detail()

    res_content = r.text
    if res_content.find('data') <= 0 or res_content.rfind('message') <= 0:
        return init_song_detail()

    response_dict = json.loads(res_content[res_content.find('data') + 6: res_content.rfind('message') - 2])
    song_time = response_dict.get('aDate')
    genre_info = response_dict.get('genre')

    lab1, lab2, lab3, lab4, lab5 = get_label_val(genre_info)

    lan = response_dict.get('lan')

    song_image = download_image(album_mid, str(singer_id))

    song_detail_dict = {'song_time': song_time}
    song_detail_dict['song_lan'] = lan
    song_detail_dict['song_image'] = song_image
    song_detail_dict['song_lable1'] = lab1
    song_detail_dict['song_lable2'] = lab2
    song_detail_dict['song_lable3'] = lab3
    song_detail_dict['song_lable4'] = lab4
    song_detail_dict['song_lable5'] = lab5

    return song_detail_dict


def init_song_detail():
    song_detail_dict = {'song_time': None}
    song_detail_dict['song_lan'] = None
    song_detail_dict['song_image'] = None
    song_detail_dict['song_lable1'] = None
    song_detail_dict['song_lable2'] = None
    song_detail_dict['song_lable3'] = None
    song_detail_dict['song_lable4'] = None
    song_detail_dict['song_lable5'] = None
    return song_detail_dict


def get_label_val(genre_info):
    genre_list = genre_info.split(' ')

    lab1 = None
    lab2 = None
    lab3 = None
    lab4 = None
    lab5 = None

    if genre_list.__len__() >= 1:
        lab1 = genre_list[0]
    if genre_list.__len__() >= 2:
        lab2 = genre_list[1]
    if genre_list.__len__() >= 3:
        lab3 = genre_list[2]
    if genre_list.__len__() >= 4:
        lab4 = genre_list[3]
    if genre_list.__len__() >= 5:
        lab5 = genre_list[4]

    return lab1, lab2, lab3, lab4, lab5


def download_image(album_mid, singer_id_str):
    file_name = SONG_STORE + singer_id_str + '/' + album_mid + IMAGE_NAME_END
    image_web_url = IMAGE_URL_START + IMAGE_NAME_BEG + album_mid + IMAGE_NAME_END
    try:
        req = requests.get(image_web_url, headers=headers)
        status_code = req.status_code
    except Exception as e:
        status_code = 404

    if status_code == 200:
        get_file(req.content, file_name)
    else:
        return None

    song_image = OSS_SONG_PATH + file_name;

    return song_image


# query_result = modles.query_songqq()
# for item in query_result:
#     album_mid, singer_id_str = item[0], str(item[1])
#     download_image(album_mid, singer_id_str)
#     print(album_mid, singer_id_str)
#     break
# result = get_song_detail('004XWK8X2snvBQ', 560462)
# print(result)
