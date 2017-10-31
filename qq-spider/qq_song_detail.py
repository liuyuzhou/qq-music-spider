import json
import random
import requests
import time
import os
import threading

import modles
from detail_info import singer_desc, download_song, song_detail, lyric
from modles import *

SINGER_SONG_LIST_URL ='https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?g_tk=5381' \
                      '&jsonpCallback=MusicJsonCallbacksinger_track&loginUin=0&hostUin=0' \
                      '&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0' \
                      '&singermid=%s&order=listen&begin=%d&num=30&songstatus=1'

SONG_LIST_HEADERS = {'referer': 'https://y.qq.com/n/yqq/singer/002J4UUk29y8BY.html',
                      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 '
                                    '(KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

PER_PAGE_NUM = 30
SONG_IMAGE_NOF_FOUND = 'http://source.edian66.com/prosong/img/singer_300.png'


def query_singer(page_num):
	query_result = query_record(page_num)
	return query_result


# 如果传人song_name 不为空，则表示指定找某一首歌
def singer_song_list(singer_id, singer_name, singer_mid, song_name=None):
	r_singer_id = read_singer_id()
	if r_singer_id is not None and r_singer_id != '' and r_singer_id > singer_id:
		return

	try:
		r = requests.get(SINGER_SONG_LIST_URL % (singer_mid, 0), headers=SONG_LIST_HEADERS)
	except Exception as e:
		r = None
		print(e)

	if r is None or r.status_code != 200:
		save_songfindfail(singer_id, singer_name, singer_mid, song_name, '歌手歌曲查找失败。')
		return

	detail_content = str(r.text)
	if detail_content.find('data') < 0:
		save_songfindfail(singer_id, singer_name, singer_mid, song_name, '歌手没有歌曲信息。')
		return

	json_obj = json.loads(detail_content[detail_content.find('data') + 6: detail_content.rfind('message') - 2])
	total_song = json_obj['total']
	if total_song < 1:
		save_songfindfail(singer_id, singer_name, singer_mid, song_name, '歌手没有歌曲。')
		return

	write_singer_id(str(singer_id))
	if r_singer_id != singer_id:
		write_song_id([])

	total_page = total_song//PER_PAGE_NUM + 1

	singer_desc.get_singer_desc_info(singer_mid, singer_id)

	structure_detail_info(singer_mid, singer_id, singer_name, total_page, song_name)


# 歌曲查找失败记录
def save_songfindfail(singer_id, singer_name, singer_mid, song_name, fail_reason):
	songfindfail_dict = {}
	songfindfail_dict['singer_id'] = singer_id
	songfindfail_dict['singer_name'] = singer_name
	songfindfail_dict['singer_mid'] = singer_mid
	songfindfail_dict['song_name'] = song_name
	songfindfail_dict['fail_reason'] = fail_reason
	try:
		modles.insert_record(songfindfail_dict, 'songfindfail')
	except Exception as e:
		print(e)


def write_singer_id(singer_id_str):
	f = open('singer.txt', 'w')
	f.write(singer_id_str)
	f.close


def read_singer_id():
	if os.path.exists('singer.txt') is False:
		fw = open('singer.txt', 'w')
		fw.write('')
		fw.close()

	f = open('singer.txt', 'r')
	singer_id = f.read()
	f.close

	if singer_id is not None and singer_id != '':
		singer_id = int(singer_id)

	return singer_id


def write_song_id(song_id_list):
	song_id_str = ','.join(song_id_list)

	f = open('song.txt', 'w')
	f.write(song_id_str)
	f.close


def read_song_id():
	f = open('song.txt', 'r')
	song_id_str = f.read()
	f.close

	song_id_list = []
	if song_id_str is not None and song_id_str != '':
		song_id_list = song_id_str.split(',')

	return song_id_list


def structure_detail_info(singer_mid, singer_id, singer_name, total_page, song_name=None):
	for page_num in range(total_page):
		try:
			r = requests.get(SINGER_SONG_LIST_URL % (singer_mid, page_num*PER_PAGE_NUM), headers=SONG_LIST_HEADERS)
		except Exception as e:
			r = None
			print(e)

		if r is None or r.status_code != 200:
			continue

		detail_content = str(r.text)
		if detail_content.find('data') < 0:
			return

		json_obj = json.loads(detail_content[detail_content.find('data') + 6: detail_content.rfind('message') - 2])
		song_list = json_obj['list']
		for song in song_list:
			music_data = song.get('musicData')
			song_detail_info(singer_id, singer_name, music_data, song_name)


# 判断txt文件中是否已经存在对应的 歌曲id-song_id，True存在，则已经爬取过，False不存在，需要爬取
def song_id_judge(song_id_str):
	song_id_list = read_song_id()
	if song_id_str in song_id_list:
		return True

	song_id_list.append(song_id_str)

	write_song_id(song_id_list)
	return False


def song_detail_info(singer_id, singer_name, music_data, song_name=None):
	# 如果song_name 不为空，则表示指定找某一首歌
	if song_name is not None:
		qq_song_name = music_data.get('songname')
		if song_name != qq_song_name:
			return

	qq_song_id = music_data.get('songid')
	if song_id_judge(str(qq_song_id)):
		return

	singer_list = music_data.get('singer')

	if singer_list.__len__() > 1:
		qq_album_id = music_data.get('albumid')
		s_song_id = qq_song_id
		# 若s_song_id 超过11位，取前11位，生成一个最大16位等正整数
		s_song_id = int(str(s_song_id)[0:11] + str(random.randint(10000, 99999)))

		query_result = modles.query_song_info(qq_song_id, qq_album_id)

		if query_result is not None:
			song_detail_dict = make_record_by_query_result(singer_id, singer_name, query_result)
		else:
			song_detail_dict = make_new_record(singer_id, singer_name, s_song_id, music_data, singer_list)
	else:
		song_detail_dict = make_new_record(singer_id, singer_name, None, music_data, None)

	if song_detail_dict is None:
		return

	modles.insert_record(song_detail_dict, 'song')
	modles.add_singer_classify(singer_id)


def make_record_by_query_result(singer_id, singer_name, query_result):
	song_detail_dict = {}
	song_detail_dict['song_url'] = query_result[1]
	song_detail_dict['song_time'] = query_result[2]
	song_detail_dict['song_blum'] = query_result[3]
	song_detail_dict['song_image'] = query_result[4]
	song_detail_dict['song_lan'] = query_result[5]
	song_detail_dict['song_name'] = query_result[6]
	song_detail_dict['song_artist'] = singer_name
	song_detail_dict['song_lable2'] = query_result[8]
	song_detail_dict['song_lable1'] = query_result[9]
	song_detail_dict['singer_id'] = singer_id
	song_detail_dict['song_play_time'] = query_result[11]
	song_detail_dict['lrc_down_url'] = query_result[12]
	song_detail_dict['song_lable3'] = query_result[13]
	song_detail_dict['song_lable4'] = query_result[14]
	song_detail_dict['song_lable5'] = query_result[15]
	song_detail_dict['s_song_id'] = query_result[17]
	song_detail_dict['s_song_mid'] = query_result[18]
	song_detail_dict['s_album_mid'] = query_result[19]
	song_detail_dict['s_album_id'] = query_result[20]
	song_detail_dict['multiple_singer'] = query_result[21]
	song_detail_dict['song_singers'] = query_result[22]

	return song_detail_dict


def make_new_record(singer_id, singer_name, s_song_id, music_data, singer_list):
	# 从qq音乐拿到的时间是秒，需转换为分秒形式
	song_play_time_seconds = music_data.get('interval')
	song_play_time = time.strftime("%M:%S", time.localtime(song_play_time_seconds))

	qq_song_mid = music_data.get('songmid')
	qq_song_id = music_data.get('songid')
	qq_song_name = music_data.get('songname')

	qq_album_mid = music_data.get('albummid')
	qq_album_id = music_data.get('albumid')
	qq_album_name = music_data.get('albumname')

	if s_song_id is None:
		s_song_id = qq_song_id

	if qq_song_mid is None:
		return None

	lrc_down_url = down_load_lrc(qq_song_id, s_song_id, qq_song_mid, singer_id)
	if lrc_down_url is None:
		# record detail info
		save_song_imperfect(qq_song_name, singer_id, singer_name, qq_album_name, 'qqmusic', 0, 1, 0)
		return None

	song_url = down_load_song(s_song_id, qq_song_mid, singer_id)
	if song_url is None:
		# record detail info
		save_song_imperfect(qq_song_name, singer_id, singer_name, qq_album_name, 'qqmusic', 1, 0, 0)
		return None

	song_detail_dict = get_song_detail(qq_album_mid, singer_id)
	if song_detail_dict.get('song_image') is None:
		# record detail info
		save_song_imperfect(qq_song_name, singer_id, singer_name, qq_album_name, 'qqmusic', 0, 0, 1)
		song_detail_dict['song_image'] = SONG_IMAGE_NOF_FOUND

	song_detail_dict['song_url'] = song_url
	song_detail_dict['song_blum'] = qq_album_name
	song_detail_dict['song_name'] = qq_song_name
	song_detail_dict['song_artist'] = singer_name
	song_detail_dict['singer_id'] = singer_id
	song_detail_dict['song_play_time'] = song_play_time
	song_detail_dict['lrc_down_url'] = lrc_down_url
	song_detail_dict['s_song_id'] = qq_song_id
	song_detail_dict['s_song_mid'] = qq_song_mid
	song_detail_dict['s_album_mid'] = qq_album_mid
	song_detail_dict['s_album_id'] = qq_album_id
	song_detail_dict['multiple_singer'] = 0
	song_detail_dict['song_singers'] = 0

	if singer_list is not None:
		song_detail_dict['multiple_singer'] = 1
		song_detail_dict['song_singers'] = s_song_id
		save_singer_info(s_song_id, singer_list)

	return song_detail_dict


def save_song_imperfect(song_name, singer_id, singer_name, album_name, s_platform, song_miss=0, lyc_miss=0,
                        image_miss=0):
	song_imperfect_dict = {}
	song_imperfect_dict['song_name'] = song_name
	song_imperfect_dict['singer_id'] = singer_id
	song_imperfect_dict['singer_name'] = singer_name
	song_imperfect_dict['album_name'] = album_name
	song_imperfect_dict['s_platform'] = s_platform
	song_imperfect_dict['song_miss'] = song_miss
	song_imperfect_dict['lyc_miss'] = lyc_miss
	song_imperfect_dict['image_miss'] = image_miss
	try:
		modles.insert_record(song_imperfect_dict, 'songimperfect')
	except Exception as e:
		print(e)


def save_singer_info(song_singers, singer_list):
	for singer_item in singer_list:
		song_singer_dict = {}
		song_singer_dict['song_singers'] = song_singers

		s_singer_id = str(singer_item.get('id'))
		s_singer_mid = singer_item.get('mid')
		singer_name = singer_item.get('name')
		singer_id_list = modles.query_singer_id(s_singer_id)
		singer_id = 0
		if singer_id_list is not None and singer_id_list.__len__() > 0:
			singer_id = singer_id_list[0]

		song_singer_dict['s_singer_id'] = s_singer_id
		song_singer_dict['s_singer_mid'] = s_singer_mid
		song_singer_dict['singer_name'] = singer_name
		song_singer_dict['singer_id'] = singer_id

		try:
			modles.insert_record(song_singer_dict, 'songsinger')
		except Exception as e:
			print(e)


def down_load_lrc(qq_song_id, song_id, song_mid, singer_id):
	return lyric.get_lyric(qq_song_id, song_id, song_mid, singer_id)


def get_song_detail(album_mid, singer_id):
	return song_detail.get_song_detail(album_mid, singer_id)


def down_load_song(song_id, song_mid, singer_id):
	return download_song.download_song(song_id, song_mid, singer_id)


def execute():
	total_num = query_total()
	total_page = total_num//100 + 1
	per_num = 100
	for page_num in range(total_page):
		query_result = query_record(None, page_num*per_num, per_num)

		for ite in query_result:
			singer_song_list(ite[0], ite[1], ite[2])

		# query_resutl_list = list(query_resutl)
		# threads = []
		# for index in range(5):
		# 	t = threading.Thread(target=do_execute, args=(query_resutl_list[index * 20:index * 20 + 20],))
		# 	threads.append(t)
		#
		# for t in threads:
		# 	t.setDaemon(True)
		# 	t.start()
		# t.join()


def do_execute(result_list):
	for ite in result_list:
		singer_song_list(ite[0], ite[1], ite[2])


# def point_singer_execute():
# 	singer_id = 560462
# 	query_resutl = query_record(singer_id, 0, 1)
# 	for ite in query_resutl:
# 		singer_song_list(ite[0], ite[1], ite[2])

if __name__ == "__main__":
	execute()
