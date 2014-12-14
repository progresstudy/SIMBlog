#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author yuezhou.li

"""This file is used for conf 
the base info of you blog"""


SITENAME = "SIM Blog - storage of my memory"
AUTHOR = "Demo"
TAGLINE = """A simple blog """ 
# a doc show you who you are
ABOUT_ME = "about_me"
EMAIL = "demo@demo.com"
# a doc show what you are doing or what 
# you did
PROJECTS = "projects"

# display custom pages
DISPLAY_PAGES_ON_MENU = True

# use google analyitcs as default
GOOGLE_ANALYTICS = False

# the num of articles in on page
ARTICLES_IN_PAGE = 5

# the summary num of words
SUMMARY_NUM = 300

# use paginator
DEFAULT_PAGINATION = True

# SITEURL
SITEURL = ""

# github push request secret
PULL_SECRET = "5ab9cdb82972a5e25201170e8d4f09f1f7271b68"

# the 3th Comments system
DISQUS_SITENAME = True

def global_env():
    return globals()
