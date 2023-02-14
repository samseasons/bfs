import os
import json
from glob import glob
from shutil import rmtree
from .util import encode, tape

class bands:
    def __init__(self, name=None, data={}, file='a.json', ties=4, root=',', path='/srv/bands/'):
        if not isinstance(name, str):
            raise ValueError('invalid name')
        if not isinstance(data, dict):
            raise ValueError('invalid data')
        if file[-5:] != '.json':
            raise ValueError('invalid file')
        if not isinstance(root, str):
            raise ValueError('invalid root')
        if not isinstance(ties, int):
            raise ValueError('invalid ties')
        if not isinstance(path, str):
            raise ValueError('invalid path')
        self.size = len(path)
        self.name = name.replace('/', '')
        self.path = path.rstrip('/') + '/'
        self.home = self.path + self.name + '/'
        self.root = self.home + root.rstrip('/') + '/'
        self.file = encode(file)
        self.ties = ties
        self.create_space(data)
        
    def alter_space(self, data):
        data_path = encode(path) + self.file
        if os.path.exists(data_path):
            with open(data_path, 'r') as json_file:
                old_data = json.load(file)
            data = {**old_data, **data}
        with open(data_path, 'w') as json_file:
            json.dump(data, json_file)

    def create_space(self, data):
        path = encode(self.home)
        if not os.path.exists(path):
            os.makedirs(path)
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        if len(data):
            self.alter_space(data)

    def erase_space(self):
        path = encode(self.home)
        if os.path.exists(path):
            rmtree(path)
            
    def clean(self, subpath):
        return subpath.replace('/', '')[:256]
    
    def clean_file(self, file):
        file = file.replace('/', '')
        return file[:file.rfind('.')][:256] + file[file.rfind('.'):]
    
    def alter_data(self, root, path, data):
        os.makedirs(path, exist_ok=True)
        subpath = root[self.size:]
        for key, value in data.items():
            item = encode(self.root + key + '/' + tape(value, self.ties) + subpath)
            os.makedirs(item, exist_ok=True)
            key = encode(root + key)
            os.makedirs(key, exist_ok=True)
        data_path = encode(root) +  self.file
        print('dpd', data_path, data)
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r') as json_file:
                    old_data = json.load(json_file)
                data = {**old_data, **data}
            except Exception as error:
                print('Error:', error)
        with open(data_path, 'w') as json_file:
            json.dump(data, json_file)

    def create_data(self, root, path, data={}):
        os.makedirs(path, exist_ok=True)
        self.alter_data(root, path, data)
    
    def erase_data(self, path, keys=[]):
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                if name == self.file:
                    data = {}
                    try:
                        with open(root + b'/' + name, 'r') as json_file:
                            data = json.load(json_file)
                    except Exception as error:
                        print('Error:', error)
                    if len(data):
                        subpath = root[self.size:]
                        for key, value in data.items():
                            if len(keys) == 0 or key in keys:
                                item = encode(self.root + key + '/' + tape(value, self.ties))
                                item = os.path.dirname(os.path.dirname(item))
                                if os.path.exists(item) and len(os.listdir(item)) == 0:
                                    rmtree(item)
                                    item = os.path.dirname(item)
                                    while len(item) > len(self.root) and len(os.listdir(item)) == 0:
                                        rmtree(item)
                                        item = os.path.dirname(item)
        path = os.path.dirname(os.path.dirname(path))
        if os.path.exists(path) and len(os.listdir(path)) < 2:
            rmtree(path)
            path = os.path.dirname(path)
            while len(path) > len(self.home) and len(os.listdir(path)) == 0:
                rmtree(path)
                path = os.path.dirname(path)
            
    def get_data(self, path=None, subpath=None):
        if os.path.exists(path):
            with open(path, 'r') as json_file:
                data = json.load(json_file)
            return {path: data}
        return {}
        
    def alter_band(self, band, data={}, path=None):
        band = self.clean(band)
        root = self.home + tape(band, self.ties)
        path = path or encode(root)
        self.erase_data(path, keys=list(data))
        self.create_data(root, path, data)

    def create_band(self, band, data={}):
        band = self.clean(band)
        path = encode(self.home + tape(band, self.ties))
        os.makedirs(path, exist_ok=True)
        if len(data):
            self.alter_band(band, data)
        
    def erase_band(self, band):
        band = self.clean(band)
        path = self.home + tape(band, self.ties)
        self.erase_data(encode(path))
        
    def find_band(self, band):
        if band:
            band = self.clean(band)
            return tape(band + max(self.ties - len(band) + 1, 1) * '*', self.ties)
        return tape((self.ties + 1) * '*', self.ties)
        
    def get_bands(self, band):
        band = self.find_band(band)
        file = encode(self.home + band) + self.file
        data = {}
        for path in glob(file):
            data.update(self.get_data(path))
        return data
    
    def alter_key(self, band, key, data={}, path=None):
        band = self.clean(band)
        key = self.clean(key)
        root = self.home + tape(band, self.ties) + key + '/'
        path = path or encode(root)
        self.create_data(root, path, data)

    def create_key(self, band, key, data={}):
        band = self.clean(band)
        key = self.clean(key)
        path = encode(self.home + tape(band, self.ties) + key + '/')
        os.makedirs(path, exist_ok=True)
        if len(data):
            self.alter_key(band, key, data, path)
        
    def erase_key(self, band, key):
        band = self.clean(band)
        key = self.clean(key)
        path = encode(self.home + tape(band, self.ties) + key)
        self.erase_data(path)

    def find_key(self, key):
        if key:
            return self.clean(key).rstrip('/') + '*/'
        return '*/'
        
    def get_keys(self, band, key=None):
        band = self.find_band(band)
        key = self.find_key(key)
        file = encode(self.home + band + key) + self.file
        data = {}
        for path in glob(file):
            data.update(self.get_data(path))
        return data

    def alter_item(self, band, key, item, data={}, path=None):
        band = self.clean(band)
        key = self.clean(key)
        item = self.clean(item)
        root = self.home + tape(band, self.ties) + key + '/' + item + '/'
        path = path or encode(root)
        self.create_data(root, path, data)

    def create_item(self, band, key, item, data={}):
        band = self.clean(band)
        key = self.clean(key)
        item = self.clean(item)
        path = encode(self.home + tape(band, self.ties) + key + '/' + item)
        os.makedirs(path, exist_ok=True)
        if len(data):
            self.alter_item(band, key, item, data, path)

    def erase_item(self, band, key, item):
        band = self.clean(band)
        key = self.clean(key)
        item = self.clean(item)
        path = encode(self.home + tape(band, self.ties) + key + '/' + item)
        self.erase_data(path)
        
    def find_item(self, item):
        if item:
            return self.clean(item).rstrip('/') + '*/'
        return '*/'

    def get_items(self, band=None, key=None, item=None):
        band = self.find_band(band)
        key = self.find_key(key)
        item = self.find_item(item)
        file = encode(self.home + band + key + item) + self.file
        data = {}
        for path in glob(file):
            data.update(self.get_data(path))
        return data

    def get_file(self, band, key, item, file):
        band = self.clean(band)
        key = self.clean(key)
        item = self.clean(item)
        file = self.clean_file(file)
        return encode(self.home + tape(band, self.ties) + key + '/' + item + '/' + file)

    def find_file(band, key, item, file):
        band = self.find_band(band)
        key = self.find_key(key)
        item = self.find_item(item)
        return encode(self.home + tape(band, self.ties) + key + item + '*')

    def get_files(self, band=None, key=None, item=None):
        file = find_file(band, key, item, file)
        return glob(file)
    
    def alter_file(self, band, key, item, file, data):
        file = get_file(band, key, item, file)
        if os.path.exists(file):
            os.remove(file)
        with open(file, 'wb') as f:
            f.write(data)
            
    def create_file(self, band, key, item, file, data={}):
        file = get_file(band, key, item, file)
        with open(file, 'wb') as f:
            f.write(data)
    
    def erase_file(self, band, key, item, file):
        file = find_file(band, key, item, file)
        for path in glob(file):
            os.remove(path)