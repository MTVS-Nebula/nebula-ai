import os
import pickle
from datetime import datetime

import torch
from sklearn.linear_model import Ridge, LogisticRegression
from xgboost import XGBRegressor
from sklearn.svm import SVR
from torch import Tensor

from multilingual_clip import pt_multilingual_clip
import transformers
import open_clip

import collie_multi_lang


class Model:

    def __init__(self):
        self.X = torch.empty(0, 512)
        self.Y = torch.empty(0, 512)
        self.model = None

    def save(self, filename):
        pickle.dump(self.model, open(filename + ".model", 'wb'))

    def load(self, filename):
        self.model = pickle.load(open(filename + ".model", 'rb'))

    def model_predict(self, x):
        if len(x.size()) == 1:
            x = x.unsqueeze(0)
        return self.model.predict(x)[0]

    # Returns the result sorted (pairs with (score,N))
    def find_best(self, text, imgEmbeds):
        # print('model.find_best init')
        with torch.no_grad():
            textEmbed = collie_multi_lang.encode_texts([text]).flatten()
            if self.model is not None:
                textEmbedCPU = textEmbed.cpu()
                # print('', textEmbedCPU.shape)
                res = Tensor(self.model_predict(textEmbedCPU))
                textEmbedAdj = textEmbedCPU.add(res)
                # print('textEmbedAdj calculated')
                return collie_multi_lang.find_best(textEmbedAdj, imgEmbeds)
            else:
                return collie_multi_lang.find_best(textEmbed, imgEmbeds)


pickledNouns = pickle.load(open(os.path.join(os.path.dirname(__file__), 'nouns1000.pickle'), 'rb'))


class CollieFullModel_XGBR(Model):

    def __init__(self, name="CoLLIE_XGBR_MultLang", defaultAlpha=0.001):
        self.alpha = defaultAlpha
        self.name = name
        self.Xm = torch.empty(0, 512)
        self.Ym = torch.empty(0)
        self.modelM = None
        self.Xm = pickledNouns
        self.Ym = torch.zeros(len(pickledNouns))
        self.savedir = './Models/'
        self.pickle_name = ''
        self.pickle_desc = 'BTS, NewJeans'
        self.pickle_dt = datetime.now()
        self.pickle_version = 'v1'
        self.pickle_summary = { 'name': [], 'desc': [], 'datetime': [], 'version': [] }
        super().__init__()

    def save(self):
        fname = f'{self.version}_{str(self.dt.year)}_{str(self.dt.month)}_{str(self.dt.day)}_{str(self.dt.hour)}_{str(self.dt.minute)}'
        path = os.path.join(self.savedir, fname)

        pickle.dump(self.model, open(path + ".xgbr.model", 'wb'))
        pickle.dump(self.modelM, open(path + ".svr.model", 'wb'))

    def load(self, filename):
        self.model = pickle.load(open(filename + ".xgbr.model", 'rb'))
        self.modelM = pickle.load(open(filename + ".svr.model", 'rb'))

    def model_predict(self, x):
        if len(x.size()) == 1:
            x = x.unsqueeze(0)
        return self.model.predict(x)[0] * self.modelM.predict(x)[0]

    def teach(self, text, imgEmbeds, k):
        with torch.no_grad():
            imgEmbed = imgEmbeds[k].flatten()
            textEmbed = collie_multi_lang.encode_texts([text]).flatten()
            diff = imgEmbed.sub(textEmbed)
            textEmbeds = textEmbed.unsqueeze(0).cpu()
            self.X = torch.cat((self.X, textEmbeds))
            self.Y = torch.cat((self.Y, diff.unsqueeze(0).cpu()))
            self.Xm = torch.cat((self.Xm, textEmbeds))
            self.Ym = torch.cat((self.Ym, torch.ones(1)))

    def train(self):
        self.model = XGBRegressor(reg_lambda = self.alpha).fit(self.X, self.Y)
        self.modelM = SVR().fit(self.Xm, self.Ym)
