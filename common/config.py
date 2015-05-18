# encoding=utf-8
'''
读取配置文件信息。
    - __init__(path, section)
        path: 配置文件路径
        section: 配置文件段落名
    - reset(path)
        path: 配置文件路径
    - fread(key)
        config: 配置文件中的某个key
    - fwrite(key, value)
        key: 新的key值
        value: 新的value值
'''

from ConfigParser import ConfigParser


class ConfigHandler(object):
    """which used to read configure file"""
    def __init__(self, path, section):
        self.conf = ConfigParser()
        self.conf.read(path)
        self.section = section
        self.cfgpath = path

    def reset(self, path, section):
        self.conf.read(path)
        self.cfgpath = path
        self.section = section

    def fread(self, config):
        if self.conf.has_option(self.section, config):
            return self.conf.get(self.section, config)
        else:
            return None

    def fwrite(self, config, value):
        if self.conf.has_option(self.section, config):
            self.conf.set(self.section, config, value)
            self.conf.write(open(self.cfgpath, 'w'))
