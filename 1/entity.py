#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author yuezhou.li

"""Entity class , entity to render templetes"""

class Article:
    def __init__(self):
        self.tags = set()
    url = ""
    title = ""
    summary = ""
    content = ""
    tags = set()
    locale_date = ""
    category = ""

class Tag:
    url = ""
    name = ""
    def __repr__(self):
        return self.name

class Category:
    url = ""
    name = ""
    def __repr__(self):
        return self.name

class ArticlesPage:

    def __init__(self, articles, pageno, pagetotal):
        self.articles = articles
        self.pageno = pageno
        self.pagetotal = pagetotal
    
    @property
    def object_list(self):
        return self.articles

    def next_page_number(self):
        return self.pageno + 1

    def previous_page_number(self):
        return self.pageno - 1

    def has_previous(self):
        if self.pageno == -1:
            return False
        if self.pageno <= 1:
            return False
        return True

    def has_next(self):
        if self.pageno == -1:
            return False
        if self.pageno+1 <= self.pagetotal:
            return True
        return False

class Page:
    title = ""
    url = ""
    content = ""
    locale_date = ""
