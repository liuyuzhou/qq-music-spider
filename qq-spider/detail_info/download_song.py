import requests
import json
import os
import urllib

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Host': 'dl.stream.qqmusic.qq.com',
           'Pragma': 'no-cache', 'Upgrade-Insecure-Requests': '1',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2717.400 QQBrowser/9.6.11133.400'}

MUSIC_URL = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?' \
            'g_tk=1400579671&jsonpCallback=MusicJsonCallback1725281637681917&loginUin=0&hostUin=0&format=json' \
            '&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&cid=205361747' \
            '&callback=MusicJsonCallback1725281637681917&uin=0&songmid=%s&' \
            'filename=%s.m4a&guid=7286222600'

SONG_DOWNLOAD_URL = 'http://dl.stream.qqmusic.qq.com/%s.m4a?vkey=%s&guid=7286222600&uin=0&fromtag=66'

OSS_SONG_PATH = 'http://source.edian66.com/'

SONG_STORE = 'prosong/'


# 下载歌曲
def get_file(file_url, song_mid, singer_id_str):
	curr_path = os.getcwd()
	# linux env access style
	file_down_path = '/home/source/musicfile/music-upload01/' + singer_id_str + '_' + song_mid + '.mp3'
	# other py file access this py file style
	# file_down_path = curr_path + '/detail_info/musicfile/' + singer_id_str + '_' + song_mid + '.mp3'
	# current py file access style
	# file_down_path = curr_path + '/musicfile/' + singer_id_str + '_' + song_mid + '.mp3'
	try:
		f = open(file_down_path, 'wb')
		f.write((urllib.request.urlopen(file_url)).read())
		f.close()

		f_size = os.path.getsize(file_down_path) / 1024
		# 若歌曲文件大小小于200k，则删除文件并返回False
		if f_size < 200:
			os.remove(file_down_path)
			return False

		return True
	except Exception as e:
		print('download exception', e)
		os.remove(file_down_path)
		return False


def download_song(song_id, song_mid, singer_id):
	file_name = 'C400' + song_mid
	req_url = MUSIC_URL % (song_mid, file_name)
	try:
		r = requests.get(req_url, headers=headers)
	except Exception as e:
		r = None
		print(e)

	if r is None or r.status_code != 200:
		return None

	res_content = r.text
	response_dict = json.loads(res_content[res_content.index('data') + 6: res_content.rindex('}')])
	if response_dict.__len__() <= 0:
		return None

	items = response_dict.get('items')
	if items.__len__() <= 0:
		return None

	detail_info_dict = items[0]
	vkey_val = detail_info_dict.get('vkey')

	song_download_url = SONG_DOWNLOAD_URL % (file_name, vkey_val)
	song_file_name = SONG_STORE + str(singer_id) + '/' + song_mid + '.mp3'

	is_down_succ = get_file(song_download_url, song_mid, str(singer_id))
	if is_down_succ is False:
		return None

	song_url = OSS_SONG_PATH + song_file_name
	return song_url


# song_url = download_song(4955364, '000rDT4L0HOWrZ', 165)
# song_url = download_song(471571, '001yjdX1322xwg', 165)
# song_url = download_song(204143008, '000jXg8T3vMdwe', 16957)
