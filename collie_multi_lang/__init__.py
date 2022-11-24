import torch
import clip
from PIL import Image
from multilingual_clip import pt_multilingual_clip
import transformers
import open_clip

# load text embedding model
model_name = 'M-CLIP/XLM-Roberta-Large-Vit-B-32'
model_txt = pt_multilingual_clip.MultilingualCLIP.from_pretrained(model_name)
tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)

# load image embedding model
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device " + device)
model_img, preprocess = clip.load("ViT-B/32", device=device)
model_img.eval()

def encode_images(files):
    with torch.no_grad():
        s = torch.stack([preprocess(Image.open(file)).to(device) for file in files])
        res = model_img.encode_image(s).to(device)
        res /= res.norm(dim=-1, keepdim=True)
        return res

def encode_texts(texts):
    with torch.no_grad():
        # res = model.encode_text(clip.tokenize(texts).to(device))
        res = model_txt.forward(texts, tokenizer)
        res /= res.norm(dim=-1, keepdim=True)
        return res

def normalize(emb):
    emb /= emb.norm(dim=-1, keepdim=True)
    return emb

# Returns the result sorted (pairs with (score,N))
def find_best(queryTensor, dataTensor, dataMeta = None):
    # print('initial query tensor shape', queryTensor.shape)
    if dataMeta is None:
        dataMeta = range(len(dataTensor))
    if len(queryTensor.size()) == 1:
        queryTensor = queryTensor.unsqueeze(0)
    if dataTensor.dtype == torch.float16:
        queryTensor = queryTensor.half().to(device)
        
    # print('query tensor shape', queryTensor.shape)
    # print('data tensor shape', dataTensor.shape)
    
    similarity = (100.0 * queryTensor @ dataTensor.T).softmax(dim=-1)
    return sorted(zip(similarity[0], dataMeta), reverse=True, key=lambda x: x[0])

def find_similarity(queryTensor, dataTensor):
    if len(queryTensor.size()) == 1:
        queryTensor = queryTensor.unsqueeze(0)
    similarity = (100.0 * queryTensor @ dataTensor.T).softmax(dim=-1)
    return similarity[0].tolist()

def dot_product(queryTensor, dataTensor):
    if len(queryTensor.size()) == 1:
        queryTensor = queryTensor.unsqueeze(0)
    similarity = (100.0 * queryTensor @ dataTensor.T)
    return similarity[0].tolist()

def read_text_file(path):
    with open(path, 'r') as file:
        data = [line.strip() for line in file.readlines()]
    return data

def mrr(result, k):
    if result is None:
        return None
    rank = 0
    for j in range(len(result)):
        if result[j][1] == k:
            rank = j+1
    return 1 / rank