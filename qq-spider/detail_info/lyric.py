import requests
from xml.etree import ElementTree
from bs4 import BeautifulSoup
import oss2
import os
import time

headers = {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'zh-CN,zh;q=0.8',
           'cache-control': 'no-cache', 'pragma': 'pragma:no-cache',
           'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/60.0.3112.113 Safari/537.36'}
REFERER = 'https://y.qq.com/n/yqq/song/%s.html'

LYRIC_API_URL = 'http://music.qq.com/miniportal/static/lyric/%d/%d.xml'

LYRIC_QUERY_URL = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric.fcg?nobase64=1&musicid=%d&callback=jsonp1' \
                  '&g_tk=5381&jsonpCallback=jsonp1&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8' \
                  '&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'

OSS_LYRIC_PATH = 'http://source.edian66.com/'

LYRIC_STORE = 'prosong/'

# 设置oss
auth = oss2.Auth('LTAIgKpditaGe91a', '0IbKHUZFhz1rOGzXi76PWFjUdLxGT8')
bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com/', 'shujustore')


# 上传歌词
def get_file(file_upload_path, file_name):
    try:
        bucket.put_object_from_file(file_name, file_upload_path)
        return True
    except Exception as e:
        print(e, 'lyric error')
        return False


def get_lyric(qq_song_id, song_id, song_mid, singer_id):
	req_url = LYRIC_API_URL % (song_id % 100, song_id)
	try:
		r = requests.get(req_url)
	except Exception as e:
		r = None
		print(e, 'lyric error')
	pre_name = str(song_id)
	if r is not None and r.status_code == 200:
		lrc_down_url = get_lyric_by_api(r.text, pre_name, singer_id)
		if lrc_down_url is None:
			lrc_down_url = get_lyric_by_web_query(qq_song_id, song_mid, pre_name, singer_id)
	else:
		lrc_down_url = get_lyric_by_web_query(qq_song_id, song_mid, pre_name, singer_id)

	return lrc_down_url


# 需要单独拆分出该方法，否则ElementTree.ElementTree(file=xml_full_path_name)报错
def write_xml_file(text_content, pre_name):
	reponse_content = text_content.replace('GB2312', 'utf-8')
	curr_path = os.getcwd()
	# other py file access this file style
	xml_file_path = curr_path + '/detail_info/xmlfile/'
	# current py access style
	# xml_file_path = curr_path + '/xmlfile/'

	xml_full_path_name = xml_file_path + pre_name + '.xml'
	f = open(xml_full_path_name, 'w')
	f.write(reponse_content)
	f.close

	return xml_full_path_name


def get_lyric_by_api(text_content, pre_name, singer_id):
	xml_full_path_name = write_xml_file(text_content, pre_name)

	try:
		tree_val = ElementTree.ElementTree(file=xml_full_path_name)
	except Exception as e:
		tree_val = None
		print(e, 'lyric error')

	if tree_val is None:
		os.remove(xml_full_path_name)
		return None

	root_val = tree_val.getroot()
	if root_val is None or root_val.text is None:
		os.remove(xml_full_path_name)
		return None

	lrc_name = pre_name + '.lrc'
	curr_path = os.getcwd()
	# other py file access this file style
	lrc_file_path = curr_path + '/detail_info/lrcfile/'
	# current py file access style
	# lrc_file_path = curr_path + '/lrcfile/'
	lrc_full_path_name = lrc_file_path + lrc_name
	fp = open(lrc_full_path_name, 'w')
	fp.write(root_val.text)
	fp.close()

	upload_file_name = LYRIC_STORE + str(singer_id) + '/' + lrc_name
	f_size = os.path.getsize(lrc_full_path_name)
	# 若歌词文件大小小于400字节，则删除文件并返回None
	if f_size < 400:
		os.remove(xml_full_path_name)
		os.remove(lrc_full_path_name)
		return None

	is_success = get_file(lrc_full_path_name, upload_file_name)
	os.remove(xml_full_path_name)
	os.remove(lrc_full_path_name)
	if is_success is False:
		return None

	lrc_down_url = OSS_LYRIC_PATH + upload_file_name
	return lrc_down_url


def get_lyric_by_web_query(qq_song_id, song_mid, pre_name, singer_id):
	req_url = LYRIC_QUERY_URL % qq_song_id
	headers['referer'] = REFERER % song_mid
	try:
		r = requests.get(req_url, headers=headers)
	except Exception as e:
		r = None
		print(e, 'lyric error')

	if r is None or r.status_code != 200:
		return None

	reponse_content = r.text
	if reponse_content.find('lyric') <= 0:
		print('no lyric:', req_url)
		return None

	lyric_cont = str(reponse_content[reponse_content.find('lyric') + 8: reponse_content.rfind('}') - 1])
	lyric_cont = lrc_content_format(lyric_cont)

	curr_path = os.getcwd()
	# other py file access this file style
	lrc_file_path = curr_path + '/detail_info/lrcfile/'
	# current file access style
	# lrc_file_path = curr_path + '/lrcfile/'

	lrc_name = pre_name + '.lrc'
	lrc_full_path_name = lrc_file_path + lrc_name
	fp = open(lrc_full_path_name, 'w')
	fp.write(lyric_cont)
	fp.close()

	upload_file_name = LYRIC_STORE + str(singer_id) + '/' + lrc_name
	f_size = os.path.getsize(lrc_full_path_name)
	# 若歌词文件大小小于400字节，则删除文件并返回None
	if f_size < 400:
		os.remove(lrc_full_path_name)
		return None

	is_success = get_file(lrc_full_path_name, upload_file_name)
	os.remove(lrc_full_path_name)
	if is_success is False:
		return None

	lrc_down_url = OSS_LYRIC_PATH + upload_file_name
	return lrc_down_url


def lrc_content_format(lyric_cont):
	if lyric_cont.find('&#10;') > 0:
		lyric_cont = lyric_cont.replace('&#10;', '\n')
	if lyric_cont.find('&#32;') > 0:
		lyric_cont = lyric_cont.replace('&#32;', ' ')
	if lyric_cont.find('&#33;') > 0:
		lyric_cont = lyric_cont.replace('&#33;', '!')
	if lyric_cont.find('&#34;') > 0:
		lyric_cont = lyric_cont.replace('&#34;', '\"')
	if lyric_cont.find('&#35;') > 0:
		lyric_cont = lyric_cont.replace('&#35;', '#')
	if lyric_cont.find('&#36;') > 0:
		lyric_cont = lyric_cont.replace('&#36;', '$')
	if lyric_cont.find('&#37;') > 0:
		lyric_cont = lyric_cont.replace('&#37;', '%')
	if lyric_cont.find('&#38;') > 0:
		lyric_cont = lyric_cont.replace('&#38;', '&')
	if lyric_cont.find('&#39;') > 0:
		lyric_cont = lyric_cont.replace('&#39;', '\'')
	if lyric_cont.find('&#40;') > 0:
		lyric_cont = lyric_cont.replace('&#40;', '(')
	if lyric_cont.find('&#41;') > 0:
		lyric_cont = lyric_cont.replace('&#41;', ')')
	if lyric_cont.find('&#42;') > 0:
		lyric_cont = lyric_cont.replace('&#42;', '*')
	if lyric_cont.find('&#43;') > 0:
		lyric_cont = lyric_cont.replace('&#43;', '+')
	if lyric_cont.find('&#44;') > 0:
		lyric_cont = lyric_cont.replace('&#44;', ',')
	if lyric_cont.find('&#45;') > 0:
		lyric_cont = lyric_cont.replace('&#45;', '-')
	if lyric_cont.find('&#46;') > 0:
		lyric_cont = lyric_cont.replace('&#46;', '.')
	if lyric_cont.find('&#47;') > 0:
		lyric_cont = lyric_cont.replace('&#47;', '/')
	if lyric_cont.find('&#48;') > 0:
		lyric_cont = lyric_cont.replace('&#48;', '0')
	if lyric_cont.find('&#49;') > 0:
		lyric_cont = lyric_cont.replace('&#49;', '1')
	if lyric_cont.find('&#50;') > 0:
		lyric_cont = lyric_cont.replace('&#50;', '2')
	if lyric_cont.find('&#51;') > 0:
		lyric_cont = lyric_cont.replace('&#51;', '3')
	if lyric_cont.find('&#52;') > 0:
		lyric_cont = lyric_cont.replace('&#52;', '4')
	if lyric_cont.find('&#53;') > 0:
		lyric_cont = lyric_cont.replace('&#53;', '5')
	if lyric_cont.find('&#54;') > 0:
		lyric_cont = lyric_cont.replace('&#54;', '6')
	if lyric_cont.find('&#55;') > 0:
		lyric_cont = lyric_cont.replace('&#55;', '7')
	if lyric_cont.find('&#56;') > 0:
		lyric_cont = lyric_cont.replace('&#56;', '8')
	if lyric_cont.find('&#57;') > 0:
		lyric_cont = lyric_cont.replace('&#57;', '9')
	if lyric_cont.find('&#58;') > 0:
		lyric_cont = lyric_cont.replace('&#58;', ':')
	if lyric_cont.find('&#59;') > 0:
		lyric_cont = lyric_cont.replace('&#59;', ';')
	if lyric_cont.find('&#60;') > 0:
		lyric_cont = lyric_cont.replace('&#60;', '<')
	if lyric_cont.find('&#61;') > 0:
		lyric_cont = lyric_cont.replace('&#61;', '=')
	if lyric_cont.find('&#62;') > 0:
		lyric_cont = lyric_cont.replace('&#62;', '>')
	if lyric_cont.find('&#63;') > 0:
		lyric_cont = lyric_cont.replace('&#63;', '?')

	return lyric_cont


# lrc_down_url = get_lyric(258620, 258620, '000rDT4L0HOWrZ', 165)
# print(lrc_down_url)
