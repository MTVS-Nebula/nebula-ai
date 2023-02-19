import clip, torch, requests, transformers, umap
from PIL import Image
from PostgreSQL.db_CRUD import CRUD


def fit(allDefaultId, dict_cat1, dict_cat2, model, preprocess, model_multi_lang, tokenizer):
    umap_haversine = umap.UMAP(output_metric='haversine', random_state=42)

    temp = CRUD()

    result_tag = temp.readDB_all_tag()
    result_img = temp.readDB_all_image_url()

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
        if k in allDefaultId:
            continue
        skyIslandId = k
        tag1, tag2, tag3, tag4 = v['tag']
        imageUrl = v['image_url']
        img = preprocess(Image.open(requests.get(imageUrl, stream=True).raw)).unsqueeze(0)

        tag1_en = dict_cat1[tag1]
        tag2_en = dict_cat2[tag2]
        preset_keyword = tag1_en + ' ' + tag2_en
        text_tokens = clip.tokenize(preset_keyword)
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
    umap_haversine.fit(image_text_features)

    return umap_haversine