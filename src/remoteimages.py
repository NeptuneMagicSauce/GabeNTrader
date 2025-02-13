import os

from utils import *
from network import *

class Images:
    k_dir = 'images'
    k_path = k_dir + '/images.pkl'

    data = {} # dict<url, data>

    def initialize():
        if not os.path.isdir(Images.k_dir):
            os.mkdir(Images.k_dir)

        try:
            Images.data = pickle_load(Images.k_path)
        except:
            pass

    def get(url, use_cache=True):
        assert(threading.current_thread().name == 'Init')

        words = url.split('/')
        name = words[-1] if len(words) else url

        if use_cache and name in Images.data:
            return Images.data[name]

        print('Fetch image', name)

        if b := Instances.fetcher.get_binary(url):
            # open(Images.k_dir + '/' + name, 'wb').write(b)
            if use_cache:
                Images.data[name] = b
                pickle_save(Images.data, Images.k_path, compress=False)
            return b
        return None
