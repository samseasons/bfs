import json
import base64
import hashlib

def load_config(path):
    try:
        with open(path, 'r') as json_file:
            return json.load(json_file)
    except:
        print('config not found')
    return {}

config_path = 'bfs/config.json'
config = load_config(config_path)
    
def update_config(self, new_config):
    config.update(new_config)
    with open(config_path, "w") as json_file:
        json.dump(json_file, config)
        
def decode(string, algo='utf-8'):
    if algo == 'b64':
        if isinstance(string, bytes):
            string = string.decode()
        return base64.b64decode(string+'==', altchars=b'-_')
    return string.decode(algo)
    
def encode(string, algo='utf-8'):
    if algo == 'b64':
        return base64.b64encode(string, altchars=b'-_').decode().replace('=', '')
    return string.encode(algo)

def tape(string, ties=4):
    string = string.replace('/', '')
    ties = min(ties, len(string) - 1) + 1
    return '/'.join(string[i] for i in range(ties)) + string[ties:] + '/'

def sha256(bytes_list):
    if isinstance(bytes_list, list) and len(bytes_list):
        m = hashlib.sha256()
        for string in bytes_list:
            if isinstance(string, bytes):
                m.update(string)
        return m.digest()
    return b''