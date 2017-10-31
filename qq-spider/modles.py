from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine('mysql+pymysql://music_pro_root:!QAZ2wsx#EDC@rm-wz9ig417esevyu3yi.mysql.rds.aliyuncs.com/music-yd'
                       '?charset=utf8', echo=False, pool_size=20)


DBSession = sessionmaker(bind=engine)
session = DBSession()
Base = declarative_base()


class singerdetail(Base):
    __tablename__ = 'singerdetail'
    sdt_id = Column(Integer, primary_key=True)
    singer_id = Column(Integer)
    singer_nationality = Column(String(20))
    singer_birth = Column(String(30))
    singer_constellation = Column(String(10))
    singer_homeplace = Column(String(20))
    singer_desc = Column(String(2000))


class song(Base):
	__tablename__ = 'song'
	song_id = Column(Integer, primary_key=True)
	song_url = Column(String(200))
	song_time = Column(String(50))
	song_blum = Column(String(100))
	song_image = Column(String(200))
	song_lan = Column(String(50))
	song_name = Column(String(50))
	song_artist = Column(String(50))
	song_lable1 = Column(String(20))
	song_lable2 = Column(String(20))
	song_lable3 = Column(String(20))
	song_lable4 = Column(String(20))
	song_lable5 = Column(String(20))
	singer_id = Column(Integer)
	song_play_time = Column(String(50))
	lrc_down_url = Column(String(200))
	s_song_id = Column(Integer)
	s_song_mid = Column(String(50))
	s_album_mid = Column(String(50))
	s_album_id = Column(Integer)
	multiple_singer = Column(Integer)
	song_singers = Column(Integer)


class songsinger(Base):
	__tablename__ = 'songsinger'
	song_singer_id = Column(Integer, primary_key=True)
	song_singers = Column(Integer)
	s_singer_id = Column(Integer)
	s_singer_mid = Column(String(50))
	singer_name = Column(String(50))
	singer_id = Column(Integer)


class songclassify(Base):
	__tablename__ = 'songclassify'
	song_classify_id = Column(Integer, primary_key=True)
	classify_type = Column(String(20))
	type_name = Column(String(20))
	singer_name = Column(String(50))
	song_name = Column(String(50))
	song_id = Column(Integer)
	song_alpha = Column(String(8))
	type_name_pinyin = Column(String(30))


class songimperfect(Base):
	__tablename__ = 'songimperfect'
	s_impft_id = Column(Integer, primary_key=True)
	song_name = Column(String(50))
	singer_id = Column(Integer)
	singer_name = Column(String(50))
	album_name = Column(String(50))
	s_platform = Column(String(20))
	song_miss = Column(Integer)
	lyc_miss = Column(Integer)
	image_miss = Column(Integer)


class songfindfail(Base):
	__tablename__ = 'songfindfail'
	id = Column(Integer, primary_key=True)
	singer_id = Column(Integer)
	singer_name = Column(String(50))
	singer_mid = Column(String(50))
	song_name = Column(String(50))
	fail_reason = Column(String(100))

Base.metadata.create_all(engine)


def insert_record(dict_value, type='singerdetail'):
	engine = create_engine(
		'mysql+pymysql://music_pro_root:!QAZ2wsx#EDC@rm-wz9ig417esevyu3yi.mysql.rds.aliyuncs.com/music-yd?charset=utf8',
		echo=False, pool_size=20)
	DBSession = sessionmaker(bind=engine)
	session = DBSession()
	Base = declarative_base()

	if type == 'song' and dict_value:
		song_add = song(song_url=dict_value['song_url'],
						song_time=dict_value['song_time'],
						song_blum=dict_value['song_blum'],
						song_image=dict_value['song_image'],
						song_lan=dict_value['song_lan'],
						song_name=dict_value['song_name'],
						song_artist=dict_value['song_artist'],
						song_lable1=dict_value['song_lable1'],
						song_lable2=dict_value['song_lable2'],
						song_lable3=dict_value['song_lable3'],
						song_lable4=dict_value['song_lable4'],
						song_lable5=dict_value['song_lable5'],
						singer_id=dict_value['singer_id'],
						song_play_time=dict_value['song_play_time'],
						lrc_down_url=dict_value['lrc_down_url'],
						s_song_id = dict_value['s_song_id'],
						s_song_mid = dict_value['s_song_mid'],
						s_album_mid = dict_value['s_album_mid'],
						s_album_id = dict_value['s_album_id'],
						multiple_singer = dict_value['multiple_singer'],
						song_singers = dict_value['song_singers'])
		session.add(song_add)
		session.commit()
	elif type == 'songsinger' and dict_value:
		songsinger_add = songsinger(song_singers=dict_value['song_singers'],
									s_singer_id=dict_value['s_singer_id'],
									s_singer_mid=dict_value['s_singer_mid'],
									singer_name=dict_value['singer_name'],
									singer_id=dict_value['singer_id'])
		session.add(songsinger_add)
		session.commit()
	elif type == 'singerdetail' and dict_value:
		singerdetail_data = session.query(singerdetail).filter_by(singer_id=dict_value['singer_id']).first()
		if singerdetail_data:
			singerdetail_data.singer_id=dict_value['singer_id']
			singerdetail_data.singer_nationality=dict_value['singer_nationality']
			singerdetail_data.singer_birth=dict_value['singer_birth']
			singerdetail_data.singer_constellation=dict_value['singer_constellation']
			singerdetail_data.singer_homeplace=dict_value['singer_homeplace']
			singerdetail_data.singer_desc=dict_value['singer_desc']
		else:
			singerdetail_add = singerdetail(singer_id=dict_value['singer_id'],
											singer_nationality=dict_value['singer_nationality'],
											singer_birth=dict_value['singer_birth'],
											singer_constellation=dict_value['singer_constellation'],
											singer_homeplace=dict_value['singer_homeplace'],
											singer_desc=dict_value['singer_desc'])
			session.add(singerdetail_add)
		session.commit()
	elif type == 'songclassify' and dict_value:
		songclassify_add = songclassify(classify_type=dict_value['classify_type'],
										type_name=dict_value['type_name'],
										singer_name=dict_value['singer_name'],
										song_name=dict_value['song_name'],
										song_id=dict_value['song_id'],
										type_name_pinyin=dict_value['type_name_pinyin'])
		session.add(songclassify_add)
		session.commit()
	elif type == 'songimperfect' and dict_value:
		songimperfect_add = songimperfect(song_name=dict_value['song_name'],
										singer_id=dict_value['singer_id'],
										singer_name=dict_value['singer_name'],
										album_name=dict_value['album_name'],
										s_platform=dict_value['s_platform'],
										song_miss=dict_value['song_miss'],
										lyc_miss=dict_value['lyc_miss'],
										image_miss=dict_value['image_miss'])
		session.add(songimperfect_add)
		session.commit()
	elif type == 'songfindfail' and dict_value:
		songfindfail_add = songfindfail(singer_id=dict_value['singer_id'],
										singer_name=dict_value['singer_name'],
										singer_mid=dict_value['singer_mid'],
										song_name=dict_value['song_name'],
										fail_reason=dict_value['fail_reason'])
		session.add(songfindfail_add)
		session.commit()
	session.close()


def query_record(condition, offset_num, query_num):
	sql_str_beg = "select singer_id,singer_name,s_singer_mid from singerclassifyqq where singer_id>1180000 "
	sql_str_end = " and singer_id<=1240000 order by singer_id limit %d,%d " % (offset_num, query_num)
	if condition is not None:
		cond_str = " and singer_id=%d " % condition
		sql_str_beg += cond_str

	sql_str = sql_str_beg + sql_str_end

	result = session.execute(sql_str)
	return result


def query_total():
	sql_str = "select count(1) from singerclassifyqq where singer_id>1180000 and singer_id<=1240000 "
	result = session.execute(sql_str).first()[0]
	return result


def query_song_info(s_song_id, s_album_id):
	sql_str = 'select * from song where s_song_id=%d and s_album_id=%d' % (s_song_id, s_album_id)
	result = session.execute(sql_str).first()
	return result


def query_singer_id(s_singer_id):
	sql_str = 'select singer_id from singerclassifyqq where s_singer_id=%s' % s_singer_id
	result = session.execute(sql_str).first()
	return result


def query_songclassify():
	sql_str = 'select classify_type,type_name,type_name_pinyin from songclassify ' \
			' group by classify_type,type_name,type_name_pinyin'
	result = session.execute(sql_str)
	return result


def query_song():
	sql_str = "select song_name,song_artist,song_blum,s_song_id,song_id,song_lable1,song_lable2,song_lable3," \
			"song_lable4,song_lable5 from song where song_time<='2017-09-25' and song_lan='国语' " \
			" and song_url is not null order by song_time desc limit 6 "
	result = session.execute(sql_str)
	return result


def query_singerclassify():
	sql_str = "select singer_photo_url,singer_id from singerclassifyqq "
	result = session.execute(sql_str)
	return result


def update_songclassify_qq_song_alpha():
	sql_str = "update songclassify set song_alpha=getFirstCode(song_name) where song_alpha is NULL"
	session.execute(sql_str)
	session.commit()


def query_song_for_lable(offset_num, query_num):
	sql_str = "select song_name,song_artist,song_blum,s_song_id,song_id,song_lable1,song_lable2,song_lable3," \
			"song_lable4,song_lable5 from song order by song_id limit %d,%d " \
			% (offset_num, query_num)
	result = session.execute(sql_str)
	return result


def query_songclassify_by_song_id(song_id):
	sql_str = "select count(1) from songclassify where song_id=%d" % song_id
	result = session.execute(sql_str).first()
	return result[0]


def query_total_from_song():
	sql_str = "select count(1) from song "
	result = session.execute(sql_str).first()
	return result[0]


def update_singer_classify(singer_id):
	sql_str = " update singerclassifyqq set singer_desc=(select singer_desc from singerdetail where singer_id=%s) " \
				" where singer_id=%s " % (singer_id, singer_id)
	session.execute(sql_str)
	session.commit()


def add_singer_classify(singer_id):
	sql_sql = "select count(1) from singerclassify where singer_id=%d " % singer_id
	query_result = session.execute(sql_sql).first()
	if query_result[0] > 0:
		return

	add_sql = "insert into singerclassify select * from singerclassifyqq where singer_id=%d " % singer_id
	session.execute(add_sql)
	session.commit()
