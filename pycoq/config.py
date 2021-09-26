'''
functions to work with config file

'''

# needs refactoring work with using dataclass for the config file and validation
# see https://tech.preferred.jp/en/blog/working-with-configuration-in-python/




from typing import Dict
from collections import defaultdict
import json
import os


DEFAULT_CONFIG = defaultdict(None,
{
    "opam_root" : os.path.join(os.getenv('HOME'),
                               '.local/share/pycoq/.opam'),
    "log_level" : 4,
    "log_filename" : os.path.join(os.getenv('HOME'),
                                  '.local/share/pycoq/pycoq.log')
}
)

PYCOQ_CONFIG_FILE = os.path.join(os.getenv('HOME'), '.pycoq')

def load_config() -> Dict:
    cfg = DEFAULT_CONFIG.copy()
    if os.path.isfile(PYCOQ_CONFIG_FILE):
        with open(PYCOQ_CONFIG_FILE) as config_file:
            cfg_from_file = json.load(config_file)
            cfg.update(cfg_from_file)
    save_config(cfg)
    return cfg


def save_config(cfg):
    '''saves config object to config file'''
    with open(PYCOQ_CONFIG_FILE, 'w') as config_file:
        json.dump(cfg, config_file)


def set_var(var: str, value):
    '''sets config var to value and saves config'''
    
    cfg = load_config()
    cfg[var] = value
    save_config(cfg)
    
def get_var(var: str):
    '''gets config var or default'''
    cfg = load_config()
    return cfg.get(var)

def set_opam_root(s: str):
    ''' sets opam root '''
    set_var("opam_root", s)

def opam_root() -> str:
    ''' loads opam root from config '''
    root = get_var("opam_root")
    if not os.path.isdir(root):
        os.makedirs(root, exist_ok=True)
    return os.path.expandvars(os.path.expanduser(root))

def set_log_level(level: int):
    ''' sets log level
    5: debug
    4: info
    3: warning
    2: error
    1: critical
    '''
    set_var("log_level", level)

def log_level():
    return get_var("log_level")

def set_log_filename(s: str):
    set_var("log_filename", s)

def log_filename():
    return os.path.expandvars(os.path.expanduser(
        get_var("log_filename")))

def strace_logdir():
    return get_var("strace_logdir")


