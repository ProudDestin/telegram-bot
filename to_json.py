import string
import json
from utils.config import root_path
import os

ar = []

with open(os.path.join(root_path, 'cenz.txt'), encoding='utf-8') as r:
    for i in r:
        n = i.lower().split('\n')[0]
        if n != '':
            ar.append(n)

with open('cenz.json', 'w', encoding='utf-8') as e:
    json.dump(ar, e)