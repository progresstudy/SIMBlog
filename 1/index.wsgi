#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author yuezhou.li

"""This is the controller of web"""

import base64
import urllib
import json
import time
import datetime

import sae
import web
from web.contrib.template import render_jinja

import setting
import utils
import entity

urls = (
      '/', 'Index',
      '/index(\d*)\.html', 'Index',
      '/archives.html', 'Archives',
      '/pages/([\w\d\_=]+)', 'Page',
      '/article/([\w\d_=]*)', 'Article',
      '/category/([\w\d\_=]+)', 'Category',
      '/tag/([\w\d\_=\-]+)', 'Tag',
      '/feeds', 'Feeds',
)

### Templates
render = render_jinja('templates',
             encoding = 'utf-8')
### Utils
memcache = utils.MemCache()
#storage = utils.LocalStorage("articles")
storage = utils.SAEStorage("articles")

### init articles to mem
memcache.add("article", storage.list())

### cache pages info
pages = []


def _generate_params():
    global pages
    params = dict()
    params.update(setting.global_env())
    if not pages:
        about_me = entity.Page()
        about_me.title = "About"
        about_me.url = "pages/%s" % \
                base64.urlsafe_b64encode(params['ABOUT_ME'])
        projects = entity.Page()
        projects.title = "Projects"
        projects.url = "pages/%s" % \
                 base64.urlsafe_b64encode(params['PROJECTS'])
        pages = [about_me, projects]
    params['pages'] = pages
    return params


class Index:
    def GET(self, pageno = 1):
        use_cache = True
        if storage.has_last():
            memcache.add("article", storage.list())
            use_cache = False
        arts = memcache.get('article')
        if not arts:
            return str(storage.has_last())
        pagetotal = (len(arts) / setting.ARTICLES_IN_PAGE) + 1
        if not pageno:
            pageno = 1
        elif type(pageno) == unicode:
            pageno = int(pageno)
        arts = arts[(pageno-1) * setting.ARTICLES_IN_PAGE:
                pageno * setting.ARTICLES_IN_PAGE]
        art_ents = []
        print "xxxxxxx"
        print use_cache
        for art in arts:
            art_ent = entity.Article()
            art_ent.title = art['slug']
            art_ent.url = "article/%s" % art['filename_url_encode']
            art_ent.summary = memcache.get(art_ent.title)
            if not use_cache or not art_ent.summary:
                art_ent.summary = storage.get(art['filename'],
                          cut=setting.SUMMARY_NUM)
                memcache.add(art_ent.title, art_ent.summary)
            art_ents.append(art_ent)
        articles_page = entity.ArticlesPage(art_ents, pageno, pagetotal)
        params = _generate_params()
        params.update({
              "articles_page" : articles_page,
              'page_name' : 'index'})
        return render.index(**params)

class Category:
    def GET(self, category):
        cat = base64.urlsafe_b64decode(str(category))
        cat = cat.decode('utf-8')
        cat_ent = entity.Category()
        cat_ent.url = "category/%s" % category
        cat_ent.name = cat
        arts = memcache.get('article')
        if not arts:
            return "articles no found"
        art_ents = []
        for art in arts:
            if art['category'] != cat:
                continue
            art_ent = entity.Article()
            art_ent.title = art['slug']
            art_ent.url = "article/%s" % art['filename_url_encode']
            art_ent.summary = storage.get(art['filename'],
                          cut=setting.SUMMARY_NUM)
            art_ents.append(art_ent)
        articles_page = entity.ArticlesPage(art_ents, -1, -1)
        params = _generate_params()
        params.update({
              "articles_page" : articles_page,
              'category' : cat_ent})
        return render.category(**params)

class Tag:
    def GET(self, tagname):
        tag = base64.urlsafe_b64decode(str(tagname))
        tag = tag.decode('utf-8')
        tag_ent = entity.Tag()
        tag_ent.url = "tag/%s" % tagname
        tag_ent.name = tag
        arts = memcache.get('article')
        if not arts:
            return "articles no found"
        art_ents = []
        for art in arts:
            if tag not in art['tags']:
                continue
            art_ent = entity.Article()
            art_ent.title = art['slug']
            art_ent.url = "article/%s" % art['filename_url_encode']
            art_ent.summary = storage.get(art['filename'],
                          cut=setting.SUMMARY_NUM)
            art_ents.append(art_ent)
        articles_page = entity.ArticlesPage(art_ents, -1, -1)
        params = _generate_params()
        params.update({
              "articles_page" : articles_page,
              'tag' : tag_ent})
        return render.tag(**params)

class Archives:
    pass
    def GET(self):
        arts = memcache.get('article')
        art_ents = []
        for art in arts:
            art_ent = entity.Article()
            art_ent.title = art['slug']
            d = art['date']
            dd = datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S.%f")
            art_ent.locale_date = dd.strftime("%Y-%m-%d %H:%M:%S")
            art_ent.url = "article/%s" % art['filename_url_encode']
            art_ents.append(art_ent)
        params = _generate_params()
        params.update({
              "dates" : art_ents,
              })
        return render.archives(**params)


class Article:
    def GET(self, filename):
        fname = base64.urlsafe_b64decode(str(filename))
        arts = memcache.get('article')
        for art in arts:
            if filename == art['filename_url_encode']:
                content = storage.get(fname)
                art_ent = entity.Article()
                art_ent.title = art['slug']
                art_ent.locale_date = art['date']
                art_ent.content = content
                art_ent.url = "article/%s" % art['filename_url_encode']
                category = entity.Category()
                category.name = art['category']
                if type(art['category']) == unicode:
                    tmp = art['category'].encode('utf-8')
                else:
                    tmp = art['category']
                category.url = "category/%s" % \
                            base64.urlsafe_b64encode(tmp)
                art_ent.category = category
                tags = art['tags']
                tags = tags.split(",")
                for tag in tags:
                    tag_ent = entity.Tag()
                    tag_ent.name = tag
                    if type(tag) == unicode:
                        tag = tag.encode('utf-8')
                    tag_ent.url = "tag/%s" % base64.urlsafe_b64encode(tag)
                    art_ent.tags.add(tag_ent)
                params = _generate_params()
                params.update({"article" : art_ent})
                return render.article(**params)
        else:
            return "no found"

    def POST(self, secret):
        if secret != setting.PULL_SECRET:
            print "get wrong secret %s" % secret
            return {"msg": "no authorized"}
        req = web.data()
        req = json.loads(req)
        com = req['head_commit']
        ref = req['ref']
        branch = ref.split("/")[-1]
        url = req['repository']['url']
        for i in com['added'] + com['modified']:
            sign = time.time()
            print "request: %s/raw/%s/%s?sign=%s" % (url, branch, i, sign)
            content = urllib.urlopen("%s/raw/%s/%s?sign=%s" % 
                         (url, branch, i, sign)).read()
            storage.save(i, content)
        for i in com['removed']:
            storage.delete(i)
        return {"msg": "success"}

class Page:
    def GET(self, pagename):
        pname = base64.urlsafe_b64decode(str(pagename))
        content = storage.get(pname)
        modefy_time = storage.update_time(pname)
        page = entity.Page()
        for p in pages:
            if pagename in p.url:
                page.url = p.url
                page.title = p.title
                break
        page.content = content
        page.locale_date = modefy_time
        params = _generate_params()
        params.update({'page':page})
        return render.page(**params)

class Feeds:
    pass

app = web.application(urls, globals())

if __name__ == '__main__':
    app.run()
application = sae.create_wsgi_app(app.wsgifunc())
