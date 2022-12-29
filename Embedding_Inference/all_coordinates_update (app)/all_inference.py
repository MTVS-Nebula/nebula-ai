import numpy as np
import clip, torch, requests, psycopg2, psycopg2.extras, transformers, umap
from multilingual_clip import pt_multilingual_clip
from PIL import Image


model, preprocess = clip.load("ViT-B/32")

model_name = 'M-CLIP/XLM-Roberta-Large-Vit-B-32'
model_multi_lang = pt_multilingual_clip.MultilingualCLIP.from_pretrained(model_name)
tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)

# umap
umap_haversine = umap.UMAP(output_metric='haversine', random_state=42)

model.eval()
model_multi_lang.eval()


# alpha에서는 우선 하드코딩 형태로 적용, 추후 불러오기
dict_cat1 = {
    "엔터테인먼트/예술": "entertainment art", "라이프스타일/취미": "lifestyle hobby", "여행/맛집": "travel restaurant", "스포츠": "sports",
    "지식/동향": "information trends", "sports":"sports"
}
dict_cat2 = {
    "영화/드라마": "movie and drama", "만화/애니메이션": "comics and animation", "TV방송": "TV programs", "인터넷방송": "online broadcast",
    "음악": "music", "연예인": "celebrity", "밈/움짤": "memes and gif", "게임": "game",
    "공연/전시/축제": "performance and exhibition and festival", "문학/책": "literature and books", "창작": "creation creator",
    "결혼/육아": "weddings childrearing and childcare", "애완동물": "pet petting", "soccer":"soccer",
    "건강/피트니스": "health and fitness training", "캠핑/등산": "outdoor camping and moutain climbing",
    "맛집": "famous must-go restaurants", "카페/디저트": "caffes and desserts", "일반": "general categories",
    "축구": "soccer", "야구": "baseball", "농구": "basketball", "배구": "volleyball", "골프": "golf",
    "IT/컴퓨터": "IT computers", "사회/정치": "social and politics", "건강/의학": "health clinic and hospital",
    "비즈니스/경제": "business and economics", "어학/외국어": "language learning", "교육/학문": "education and academic discipline",
    "경영/직장": "management and career", '요리/레시피': 'cooking/recipes', '국내여행': 'domestic travel', '해외여행': 'overseas travel'
}


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


class CRUD(Databases):

    def readDB_all_tags(self):
        sql = """
            SELECT (sky.id, avttag.content) 
            FROM skyisland.tbl_sky_island AS sky
                INNER JOIN avatar.tbl_avatar_tag AS avttag
                ON sky.avatar_id = avttag.avatar_id
        """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    def readDB_all_image_urls(self):
        sql = """
            SELECT (sky.id, atc.saved_path) 
            FROM skyisland.tbl_sky_island AS sky
                INNER JOIN avatar.tbl_avatar AS avt
                    ON sky.avatar_id = avt.id
                INNER JOIN file.tbl_atc AS atc
                    ON avt.image_id = atc.id
        """
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    def updateDB(self, schema, table, colum_update, value_update, colum_condition, value_condition):
        sql = f" UPDATE {schema}.{table} SET {colum_update}='{value_update}' WHERE {colum_condition}='{value_condition}' "
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(" update DB err", e)

    def updateDB_skyIslandCoord(self, schema, table, skyIslandId, k1, k2, pc1, pc2, pc3):
        sql1 = f" UPDATE {schema}.{table} SET "
        sql2 = f"id={skyIslandId}, keyword1='{k1}', keyword2='{k2}', pc1={pc1}, pc2={pc2}, pc3={pc3} "
        sql3 = f"WHERE id = {skyIslandId}"
        sql = sql1 + sql2 + sql3
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print(" update DB err", e)


crud = CRUD()

result_tag = crud.readDB_all_tags()
result_img = crud.readDB_all_image_urls()

req = {}
for row in result_tag:
    skyid = int(row['row'].split(',')[0][1:])
    tag = row['row'].split(',')[1][:-1]
    if skyid in req.keys():
        req[skyid]['tag'].append(tag)
    else:
        req[skyid] = {'tag': [], 'image_url': ''}
        req[skyid] = {'tag': []}
        req[skyid]['tag'].append(tag)

for row in result_img:
    skyid = int(row['row'].split(',')[0][1:])
    url = row['row'].split(',')[1][:-1]
    if skyid in req.keys():
        req[skyid]['image_url'] = url

reqIds = []
image_text_features = []
keywords1, keywords2 = [], []

for k, v in req.items():
    skyIslandId = k
    tag1, tag2, tag3, tag4 = v['tag']
    imageUrl = v['image_url']
    img = preprocess(Image.open(requests.get(imageUrl, stream=True).raw)).unsqueeze(0)

    tag1_en = dict_cat1[tag1]
    tag2_en = dict_cat2[tag2]
    preset_keyword = tag1_en + ' ' + tag2_en
    text_tokens = clip.tokenize(preset_keyword)
    # free_keyword = tag1 + ' ' + tag2 + ' ' + tag3 + ' ' + tag4
    free_keyword = tag3 + ' ' + tag4

    with torch.no_grad():
        image_features = model.encode_image(img).float()
        text_cat_features = model.encode_text(text_tokens).float()
        text_free_features = model_multi_lang.forward(free_keyword, tokenizer).float()

    image_text_feature = torch.cat([image_features, text_cat_features, text_free_features], dim=1).squeeze(0)  # image 512 + text_cat 512 + text_free 512 = 1536
    image_text_feature = image_text_feature.detach().tolist()
    image_text_features.append(image_text_feature)
    del image_text_feature, text_cat_features, text_free_features, image_features

    reqIds.append(int(skyIslandId))
    keywords1.append(tag1)
    keywords2.append(tag2)

# UMAP
sphere_coord = umap_haversine.fit_transform(image_text_features)
del image_text_features

x_coord = np.sin(sphere_coord[:, 0]) * np.cos(sphere_coord[:, 1]) * 2.0
y_coord = np.sin(sphere_coord[:, 0]) * np.sin(sphere_coord[:, 1]) * 2.0
z_coord = np.cos(sphere_coord[:, 0]) * 2.0


for p1, p2, p3, i, k1, k2 in zip(x_coord, y_coord, z_coord, reqIds, keywords1, keywords2):
        crud.updateDB_skyIslandCoord('skyisland', 'tbl_sky_island_coordinate', int(i), k1, k2, p1, p2, p3)
