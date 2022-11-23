import numpy as np
import torch, transformers, clip, requests, umap
from multilingual_clip import pt_multilingual_clip
from xgboost import XGBRegressor
from sklearn.svm import SVR
from PIL import Image


class Models:
    def __init__(self):
        # CLIP Model
        self.model_clip, self.preprocess = clip.load("ViT-B/32")
        self.model_clip.eval()

        # Multi Lang CLIP Model
        model_name = 'M-CLIP/XLM-Roberta-Large-Vit-B-32'
        self.model_multi_lang = pt_multilingual_clip.MultilingualCLIP.from_pretrained(model_name)
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)
        self.model_multi_lang.eval()

        # UMAP Model
        self.umap_haversine = umap.UMAP(output_metric='haversine', random_state=42)

        # XGB Regressor Model
        self.model_xgb = XGBRegressor()

        # SVM Regressor Model
        self.model_svm = SVR()

    ##### CLIP => ImageEncode / TextEncode
    def ImageEncode(self, imageUrl):
        img = self.preprocess(Image.open(requests.get(imageUrl, stream=True).raw)).unsqueeze(0)
        return img
    def TextEncode(self, preset_keyword):
        text_tokens = clip.tokenize(preset_keyword)
        return text_tokens

    ##### Multi Lang CLIP => TextEncode
    def TextEncode(self, imageUrl, preset_keyword, free_keyword):
        img = self.ImageEncode(imageUrl)
        text_tokens = self.TextEncode(preset_keyword)

        with torch.no_grad():
            image_features = self.model_clip.encode_image(img).float()
            text_cat_features = self.model_clip.encode_text(text_tokens).float()
            text_free_features = self.model_multi_lang.forward(free_keyword, self.tokenizer).float()

        image_text_feature = torch.cat([image_features, text_cat_features, text_free_features], dim=1).squeeze(0)
        image_text_feature = image_text_feature.detach().tolist()
        return image_text_feature

    ##### UMAP => Coordinates
    def Coordinates(self, image_text_features):
        sphere_coord = self.umap_haversine.fit_transform(image_text_features)
        x_coord = np.sin(sphere_coord[:, 0]) * np.cos(sphere_coord[:, 1])
        y_coord = np.sin(sphere_coord[:, 0]) * np.sin(sphere_coord[:, 1])
        z_coord = np.cos(sphere_coord[:, 0])
        return x_coord, y_coord, z_coord

    ##### XGB Regressor => Predict
    def XGBPredict(self, xgb_input):
        xgb_pred = self.model_xgb.predict(xgb_input)
        return xgb_pred

    ##### SVM Regressor => Predict
    def SVMPredict(self, svm_input):
        svm_pred = self.model_svm.predict(svm_input)
        return svm_pred