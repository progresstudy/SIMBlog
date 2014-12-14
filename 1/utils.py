#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author yuezhou.li

"""This file include some utils"""

import os
import codecs
import re
import datetime
import base64

import markdown

class Cache(object):
    """Cache class used to cache necessary info"""
    def add(self, key, value):
        raise Exception("No Impl")

    def delete(self, key, value):
        raise Exception("No Impl")
    
    def get(self, key):
        raise Exception("No Impl")

class MemCache(Cache):
    """The memory cache"""
    def __init__(self):
        self.bucket = dict()

    def add(self, key, value):
        self.bucket[key] = value

    def delete(self, key, value):
        if self.bucket.has_key(key):
            self.bucket.pop(key)
            
    def get(self, key):
        return self.bucket.get(key, None)

class Parse(object):
    """Parse articles"""
    def parse(self, article):
        raise Exception("No Impl")

class MDParse(Parse):
    """Markdown parse"""
    def parse(self, article):
        return markdown.markdown(article)


class Storage(object):
    """Manage articles"""
    
    metadatas = {
            "date": "",
            "tags": "default",
            "category": "articles",
            "slug": "",
            "author": "yuezhou.li",
            "summary": "",
            }
    
    def list(self):
        """List all articles"""
        raise Exception("No Impl")

    def get(self, article, cut = -1):
        """Get article content,
        :params article: the path of articles,
        :params cut: get part of content"""
        raise Exception("No Impl")
    
    def is_article(self, article):
        """is article"""
        raise Exception("No Impl")

    def has_last(self):
        raise Exception("No Impl")

class LocalStorage(Storage):
    """The articles at local dir"""

    def __init__(self, path):
        self.path = path
        self.last_time = None
        if not os.path.isdir(self.path):
            raise Exception("The path not exist" % self.path)

    def list(self):
        self.last_time = os.path.getmtime(self.path)
        all_files = os.listdir(self.path)
        rst = []
        all_files = self._sorted_files(all_files)
        for f, ctime in all_files:
            fpath = os.path.join(self.path, f)
            with codecs.open(fpath, "r+", encoding="utf-8") as fs:
                content = fs.read()
                art_meta = self._get_metadatas(content)
                art_meta['filename'] = f
                art_meta['filename_url_encode'] = \
                             base64.urlsafe_b64encode(f)
                if not art_meta['date']:
                    d = datetime.datetime.fromtimestamp(ctime)
                    str_d = d.strftime("%Y-%m-%d %H:%M:%S")
                    art_meta['date'] = str_d
                if not art_meta["slug"]:
                    art_meta['slug'] = f.rpartition(".")[0]
                    art_meta['slug'] = art_meta['slug'].replace("_", " ")
                rst.append(art_meta)
        return rst

    def get(self, article, cut=-1):
        fpath = os.path.join(self.path, article)
        with codecs.open(fpath, "r+", encoding="utf-8") as f:
            mdparse = MDParse()
            content = f.read(cut)
            if cut != -1:
                content += "\n....."
            content = self._clean_metadatas(content)
            return mdparse.parse(content)

    def update_time(self, article):
        mtime = os.path.getmtime(self.path)
        d = datetime.datetime.fromtimestamp(mtime)
        return d.strftime("%Y-%m-%d %H:%M:%S")

    def is_article(self, article):
        return article.endswith(".md")

    def has_last(self):
        d = os.path.getmtime(self.path)
        return d > self.last_time
    
    def _get_metadatas(self, content):
        rst = dict()
        for i in self.metadatas:
            match = re.findall(":%s:\s{0,1}(.*)\n" % i, content)
            if match:
                rst[i] = match[0].strip()
            else:
                rst[i] = self.metadatas[i]
        return rst

    def _clean_metadatas(self, content):
        for i in self.metadatas:
            content, status = re.subn(":%s:.+\n" % i, "", content)
        return content

    def _sorted_files(self, files):
        all_files = []
        for f in files:
            fpath = os.path.join(self.path, f)
            if self.is_article(f):
                all_files.append((f, 
                    os.path.getctime(fpath)))
        def sort_key(item):
            return item[1]
        return sorted(all_files, key=sort_key, reverse=True)


class SAEStorage(LocalStorage):
    def __init__(self, bucket):
        from sae.storage import Bucket
        self.bucket = Bucket(bucket)
        bucket_stat = self.bucket.stat()
        #self.last_mark = bucket_stat.objects + \
        #                       bucket_stat.bytes
        self.last_mark = 0

    def list(self):
        articles = self.bucket.list()
        filter_func = lambda x : self.is_article(x.name)
        articles = filter(filter_func, articles)
        articles = self._sorted_files(articles)
        rst = []
        for article in articles:
            article_name = article.name
            content = self.bucket.get_object_contents(article_name)
            content = content.decode('utf-8')
            art_meta = self._get_metadatas(content)
            art_meta['filename'] = article_name
            if type(article.name) == unicode:
                adjust_name = article_name.encode('utf-8')
            else :
                adjust_name = article_name
            art_meta['filename_url_encode'] = \
                         base64.urlsafe_b64encode(adjust_name)
            if not art_meta['date']:
                art_meta['date'] = article.last_modified
            if not art_meta["slug"]:
                art_meta['slug'] = article_name.rpartition(".")[0]
                art_meta['slug'] = art_meta['slug'].replace("_", " ")
            rst.append(art_meta)
        return rst

    def get(self, article, cut = -1):
        content = self.bucket.get_object_contents(article)
        content = content.decode('utf-8')
        content = unicode(content)
        mdparse = MDParse()
        if cut != -1:
            content = content[:cut]
            content += "\n....."
        content = self._clean_metadatas(content)
        return mdparse.parse(content)

    def save(self, name, content):
        self.bucket.put_object(name, content)

    def delete(self, name):
        self.bucket.delete_object(name)

    def update_time(self, article):
        stat = self.bucket.stat_object(article)
        tmp = float(stat.timestamp)
        d = datetime.datetime.fromtimestamp(tmp)
        return d.strftime("%Y-%m-%d %H:%M:%S")

    def has_last(self):
        bucket_stat = self.bucket.stat()
        curr_mark = bucket_stat.objects + bucket_stat.bytes
        res = self.last_mark == curr_mark
        self.last_mark = curr_mark
        return not res

    def _sorted_files(self, articles):
        def key_func(x):
            stat = self.bucket.stat_object(x.name)
            return float(stat.timestamp)
        return sorted(articles, key=key_func, reverse=True)
