import cPickle
import zlib
import re
import time
import os

from _os import remove_file, rename_file, create_folder, hide_file
from versions import VERSION, upgrade_version
from constants import DEFAULT_NAME, CONFIG


def format_folder_path(path):
    parts = path.replace('\\', '/').split('/')
    if '.' in parts[-1]:
        del parts[-1]
    return '/'.join(i for i in parts if i)


def load_program(program_name=None):
    if program_name is None:
        program_name = DEFAULT_NAME
    elif isinstance(program_name, (list, tuple)):
        program_name = program_name[0]
    name_format = re.sub('[^A-Za-z0-9]+', '', program_name).lower()
    path = CONFIG.data['Paths']['Data']
    try:
        with open('{}/{}.data'.format(path, name_format), 'rb') as f:
            loaded_data = cPickle.loads(zlib.decompress(f.read()))
    except (IOError, zlib.error):
        try:
            with open('{}/{}.data.old'.format(path, name_format), 'rb') as f:
                loaded_data = cPickle.loads(zlib.decompress(f.read()))
        except (IOError, zlib.error):
            return {'Tracks': {},
                    'Clicks': {},
                    'Speed': {},
                    'Keys': {'Pressed': {}, 'Held': {}},
                    'Combined': {},
                    'Time': {'Created': time.time(),
                             'Modified': time.time()},
                    'Version': VERSION,
                    'Ticks': {'Current': 0, 'Total': 0, 'Recorded': 0},
                    'TimesLoaded': 0}
    else:
        loaded_data['TimesLoaded'] += 1
        return upgrade_version(loaded_data)
    

def save_program(program_name, data):
    if program_name is None:
        program_name = [DEFAULT_NAME]
    name_format = re.sub('[^A-Za-z0-9]+', '', program_name[0]).lower()
    data['Time']['Modified'] = time.time()
    data['Version'] = VERSION
    compressed_data = zlib.compress(cPickle.dumps(data))

    path = CONFIG.data['Paths']['Data']
    old_name = '{}/{}.data.old'.format(path, name_format)
    new_name = '{}/{}.data'.format(path, name_format)
    temp_name = '{}/{}.data.{}'.format(path, name_format, int(time.time()))

    create_folder(path)
    with open(temp_name, 'wb') as f:
        f.write(compressed_data)
    remove_file(old_name)
    rename_file(new_name, old_name)
    hide_file(old_name)
    if rename_file(temp_name, new_name):
        return True
    else:
        remove_file(temp_name)
        return False
