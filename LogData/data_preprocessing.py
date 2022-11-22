import psycopg2, psycopg2.extras
from datetime import datetime


class Databases():
    def __init__(self):
        self.db = psycopg2.connect(
            host='*****',
            dbname='*****',
            user='*****',
            password='*****',
            port=*****
        )
        self.cursor = self.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def __del__(self):
        self.db.close()
        self.cursor.close()

    def execute(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.cursor.commit()


class SELECT(Databases):
    def SkyIslandCount(self):
        sql = '''
        SELECT COUNT(id) AS skyisland_cnt FROM skyisland.tbl_sky_island
        '''
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e:
            result = (" read DB err", e)
        return result

    def Keyword(self):
        sql = '''
        SELECT sky.id AS skyisland_id,
                CASE WHEN avttag.number=0 THEN avttag."content" ELSE 'X' END AS category1,
                CASE WHEN avttag.number=1 THEN avttag."content" ELSE 'X' END AS category2,
                CASE WHEN avttag.number>1 THEN avttag."content" ELSE 'X' END AS free_keyword
        FROM skyisland.tbl_sky_island AS sky
        INNER JOIN avatar.tbl_avatar_tag AS avttag
        ON sky.avatar_id = avttag.avatar_id
        ORDER BY sky.id, category1, category2, free_keyword
        '''
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e:
            result = (" read DB err", e)
        return result

    def UserConnectLog(self):
        sql = '''
        SELECT DISTINCT to_char("login_date", 'YYYY-MM-DD') AS login_date, user_id
        FROM users.tbl_login_log
        ORDER BY login_date, user_id
        '''
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e:
            result = (" read DB err", e)
        return result

    def ItemCount(self):
        sql = '''
        SELECT COUNT(id) AS generateitem_cnt
        FROM item.tbl_clothes
        '''
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e:
            result = (" read DB err", e)
        return result

select = SELECT()

#################### 하늘섬 총 갯수 ####################
skyisland_all_cnt = select.SkyIslandCount()[0]['skyisland_cnt']
# print(skyisland_all_cnt)

#################### 취향 프로필 통계 data ####################
##### 섬id: [카테고리1, 카테고리2, 자유키워드1, 자유키워드2] #####
keyword_select = select.Keyword()
profile_data = {}

for ks in keyword_select:
    key_tmp = ks['skyisland_id']
    cate1, cate2, fword = ks['category1'], ks['category2'], ks['free_keyword']

    if key_tmp not in profile_data.keys():
        # key(=skyisland_id) => not string, but int
        profile_data[key_tmp] = []

    # value 순서 => category1, category2, freekeyword(free_keyword1, free_keyword2)
    if cate1 != 'X':
        profile_data[key_tmp].append(cate1)
    elif cate2 != 'X':
        profile_data[key_tmp].append(cate2)
    else:
        profile_data[key_tmp].append(fword)

# print(profile_data)

#################### 유저 리텐션 ####################
##### user_id 기준 일별 접속 여부 #####
connect_log = select.UserConnectLog()
login_data = {}

for cl in connect_log:
    key_temp = cl['user_id']
    user_id = cl['login_date']

    if key_temp not in login_data.keys():
        # key(=user_id) => not string, but int
        login_data[key_temp] = []

    # value(=login_date) => not datetime, but string
    login_data[key_temp].append(user_id)

# 3일 중에 2번 이상 접속한 user 뽑기
min_date = connect_log[0]['login_date']
max_date = connect_log[-1]['login_date']
datetime_format = "%Y-%m-%d"
min_datetime = datetime.strptime(min_date, datetime_format)
max_datetime = datetime.strptime(max_date, datetime_format)

# 일단, 3일 중에 2번 이상 접속한 확률을 기준으로 테스트 단계에서 유저를 뽑아낼 것임
percentage = round(2/3, 3) # 66.7% 기준
all_period = max_datetime - min_datetime
retention_user = []
for ld in login_data.items():
    user_tmp = ld[0]
    list_tmp = ld[1]
    min_tmp = datetime.strptime(list_tmp[0], datetime_format)
    max_tmp = datetime.strptime(list_tmp[-1], datetime_format)
    now_percentage = round((max_tmp-min_tmp)/all_period, 3)
    if now_percentage >= percentage:
        retention_user.append(user_tmp)

# print(retention_user)

#################### 아이템 로그 ####################
##### 생성 아이템 수 #####
generate_item_cnt = select.ItemCount()[0]['generateitem_cnt']
# print(generate_item_cnt)
