#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Generate static site
'''

import os
import yaml
import time
import shutil
import logging

from collections import defaultdict
from jinja2 import Environment, PackageLoader


# Core config params

CONTENT_DIR = 'content'
LAYOUT_DIR = 'layout'
STATIC_DIR = 'static'
BUILD_DIR = 'public'


# Default item params

SITE_PAGES = 'pages'

PAGE_URL = 'url'
PAGE_NAME = 'name'
PAGE_PATH = 'path'
PAGE_LAYOUT = 'layout'
PAGE_CONTENT = 'content'

log = logging.getLogger('tagy')
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler())

def generate():
	log.info('Generate site')
	site = load_site()
	generate_site(site)

def load_site():
	# load basic configs
	with open('config.yaml', 'r') as f:
		site = Config(yaml.load(f))

	# add pages
	site[SITE_PAGES] = load_content()

	# build indexes
	for page in site.pages:
		# check all indexes
		for indexname in iter(site.indexes):
			index = site.indexes[indexname]
			terms = getattr(page, indexname, None)
			if isinstance(terms, list):
				for term in terms:
					index.setdefault('terms', {}).setdefault(term, []).append(page)

	return site

def load_content(dir=CONTENT_DIR):
	pages = []
	for subdir, dirs, files in os.walk(dir):
		for file in files:
			path = os.path.join(subdir, file)
			pages.append(load_page(path))
	return pages
	
CONFIG = '---\n'

from markdown import markdown
def load_page(path):
	with open(path, 'r') as f:
		content = f.read()
		i = content.find(CONFIG)
		page = yaml.load(content[:i]) if i > 0 else {}
		start = i+len(CONFIG) if i > 0 else 0
		page[PAGE_CONTENT] = markdown(content[start:].decode('utf-8'))
		path = path[ : path.index('.')]
		page[PAGE_NAME] = os.path.basename(path)
		if path.endswith('/index'): # cut index page
			path = path[ : path.index('/index')]
		page[PAGE_PATH] = path[len(CONTENT_DIR + '/') : ]
		return Config(page)


# Generate logic

env = Environment(loader=PackageLoader('tagy', LAYOUT_DIR))

def generate_site(site):
	clear()

	for page in site.pages:
		generate_page(page, site)

	for name in iter(site.indexes):
		generate_index(name, site)

def clear():
	# Clear dir
	folder = BUILD_DIR
	if os.path.exists(folder):
		for name in os.listdir(folder):
		    path = os.path.join(folder, name)
		    try:
		        if os.path.isfile(path):
		            os.unlink(path)
		        else: 
		        	shutil.rmtree(path)
		    except Exception, e:
		        print e
	else:
		os.makedirs(folder)

	# Copy static dir
	for file_name in os.listdir(STATIC_DIR):
	    full_file_name = os.path.join(STATIC_DIR, file_name)
	    if (os.path.isfile(full_file_name)):
	        shutil.copy(full_file_name, BUILD_DIR)
	    else:
	    	shutil.copytree(full_file_name, os.path.join(BUILD_DIR, file_name))


def generate_page(page, site):
	template = env.get_template(get_template(page))
	path = get_build_path(page)
	f = open(path, 'w')
	# try:
	html = template.render({'page': page, 'site': site})
	f.write(html.encode('utf-8'))
	f.close()
	# except Exception, e:
		# print 'Cannot generate page '+page.path, e

def generate_index(name, site):
	index = getattr(site.indexes, name)
	for term in iter(index.terms):
		# TODO: remove layout from yaml
		template = env.get_template(get_template(index))
		
		page = Config()
		page.path = index.url + '/' + term
		f = open(get_build_path(page), 'w')

		html = template.render({'term': term, 'pages': index.terms[term], 'site': site})
		f.write(html.encode('utf-8'))
		f.close()



def get_template(page):
	# TODO: impl inheritance logic
	if PAGE_LAYOUT in page:
		return page[PAGE_LAYOUT]
	return 'index.html'

# Return fancy url for path
def get_build_path(page):
	if PAGE_URL in page:
		return BUILD_DIR + '/' + page.url

	dir = BUILD_DIR + '/' + page.path

	try:
		os.stat(dir)
	except:
		os.makedirs(dir)
	return dir + '/index.html'

def get_last_update():
	'''Get last update time for content directories'''
	# path = '/tmp/test_tracking/'
	files = []
	subdirs = []

	last = None
	for path in [CONTENT_DIR, STATIC_DIR, LAYOUT_DIR]:
		for root, dirs, filenames in os.walk(path):
			# for subdir in dirs:
			# subdirs.append(os.path.relpath(os.path.join(root, subdir), path))

			for f in filenames:
				filename = os.path.relpath(os.path.join(root, f), path)
				file_mtime = os.path.getmtime(os.path.join(path, filename))
				if file_mtime > last or last is None:
					last = file_mtime 
	return last


# Jinja filter
import Image
def get_thumbnail(value, size=(100, 100)):
	file_path = BUILD_DIR + value
	file, ext = os.path.splitext(file_path)
	path = (file + '-%dx%d' + ext) % size
	im = Image.open(file_path)
	im.thumbnail(size, Image.ANTIALIAS)
	im.save(path, "JPEG")
	return path[len(BUILD_DIR) : ]

env.filters['thumb'] = get_thumbnail



# Model for config params
class Config(dict):
    def __getattr__(self, attr):
    	if attr not in self:
    		return None
    	result = self[attr]
    	if isinstance(result, dict):
    		result = Config(result)
        return result
    def __setattr__(self, attr, value):
        self[attr] = value



if __name__=='__main__':
	'''Watch file changed in infinite loop'''
	updated = None
	while True:
		last = get_last_update()
		if updated != last:
			updated = last
			generate()
		time.sleep(1)

