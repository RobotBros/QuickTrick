#!/usr/bin/env python
import os
import re
import time
import json


AUTHOR = 'RobotBros'
REPO_PROTOCOL = "https"
REPO_SERVER = 'github.com'
REPO_NAME = 'RobotBros/QuickTrick'

ISO_639_1_CODES = ['en-US', 'en-GB', 'en-CA', 'en-AU', 'zh-CN', 'zh-TW', 'zh-HK']

TRICK_PREFIX = ['cheetsheet', 'shortcut']


class MyEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class TrickModel(object):
    '''
    Trick
    '''
    def __init__(self, tid, title, author, created, url, languages=['en-US']):
        self.id = tid
        self.title = title
        self.author = author
        self.created = created
        self.languages = languages
        self.url = url


class CatalogModel(object):
    '''
    Catalog
    '''
    def __init__(self):
        self.created = 0
        self.catalog = []

    def addTrick(self, trick):
        assert isinstance(trick, TrickModel), "trick must be TrickModel object."
        self.catalog.append(trick)

    def removeTrick(self, trick=None, index=None):
        assert trick is None or isinstance(trick, TrickModel), "trick must be None or TrickModel object."
        assert index is None or isinstance(index, int), "index must be None or int."
        self.catalog.pop(index)

    def curdir(self):
        return os.path.realpath(os.path.curdir)

    def url_normalize(self, path):
        return '{}://{}/{}/{}'.format(REPO_PROTOCOL, REPO_SERVER, REPO_NAME, path)

    def build_catalog(self):
        cwd = self.curdir()
        print('Start to build catalog (dir: {})...'.format(cwd))
        for d in os.walk(cwd):
            not_found = True
            for prefix in TRICK_PREFIX:
                if re.search(prefix, d[0]):
                    not_found = False
            if not_found:
                continue

            print('Analysing {}...'.format(d[0]))
            # Get title
            title = ''
            path = ''
            for prefix in TRICK_PREFIX:
                m = re.match(r'(.*)/{}_(.*)'.format(prefix), d[0])
                if m:
                    title = m.groups()[1]
                    path = prefix + '_' + title

            tid = '{}-1'.format(title)
            created = int(os.stat(d[0]).st_mtime)
            url = path
            # Get supported language
            languages = []
            for f in d[2]:
                m = re.match('{}.([\w\-]+).json'.format(title), f)
                if m:
                    language = m.groups()[0]
                    if language in ISO_639_1_CODES:
                        languages.append(language)
                    else:
                        print('Warning: not supported language: {} for trick: {}'.format(language, f))

            trick = TrickModel(tid, title, AUTHOR, created, url, languages)
            self.addTrick(trick)

        self.created = int(time.time())

    def save_to_json(self, filename):
        with open(filename, 'wb') as f:
            j = MyEncoder().encode(self.__dict__)
            f.write(j)
        print('JSON file saved to {}.'.format(filename))

if __name__ == '__main__':
    catalog = CatalogModel()
    catalog.build_catalog()
    catalog.save_to_json('catalog.json')
