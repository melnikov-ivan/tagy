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
import optparse

from threading import Thread
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
			if file.startswith('.'):
				continue
			path = os.path.join(subdir, file)
			page = load_page(path)
			pages.append(page)
	return pages
	
CONFIG = '---\n'

import mistune
def load_page(path):
	with open(path, 'r') as f:
		content = f.read()
		i = content.find(CONFIG)
		page = yaml.load(content[:i]) if i > 0 else {}
		start = i+len(CONFIG) if i > 0 else 0
		content = content[start:].decode('utf-8')
		if path.endswith('.html') | path.endswith('.md'):
			content = mistune.markdown(content)
		page[PAGE_CONTENT] = content
		path = path[ : path.index('.')]
		page[PAGE_NAME] = os.path.basename(path)
		if path.endswith('/index'): # cut index page
			path = path[ : path.index('/index')]
		page[PAGE_PATH] = path[len(CONTENT_DIR + '/') : ]
		return Config(page)
	except:
		print 'Failed to read page "%s"' % path


# Generate logic

env = Environment(loader=PackageLoader('tagy', LAYOUT_DIR))

def generate_site(site):
	clear()

	for page in site.pages:
		try:
			generate_page(page, site)
		except:
			print 'Failed to generate page "%s"' % page[PAGE_PATH]

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
	# render content
	content = env.from_string(page.content)
	page.content = content.render({'page': page})
	
	# render layout
	template = env.get_template(get_template(page))
	html = template.render({'page': page, 'site': site})

	# generate page
	path = get_build_path(page)
	f = open(path, 'w')
	f.write(html.encode('utf-8'))
	f.close()

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
	for folder in [CONTENT_DIR, STATIC_DIR, LAYOUT_DIR]:
		for root, dirs, filenames in os.walk(folder):
			for f in filenames:
				filename = os.path.relpath(os.path.join(root, f), folder)
				file_mtime = os.path.getmtime(os.path.join(folder, filename))
				if file_mtime > last or last is None:
					last = file_mtime 
	return last

def serve(port=1313):
	thread = Thread(target=watch)
	thread.daemon = True
	thread.start()

	# start server
	os.system("cd %s; python -m SimpleHTTPServer %d" % (BUILD_DIR, port))

def watch():
	'''Watch file changed in infinite loop'''
	updated = None
	while True:
		last = get_last_update()
		if updated != last:
			updated = last
			try:
				generate()
			except Exception, e:
				print e
		time.sleep(1)


# Jinja filters

def breadcrumbs(path):
	'''Return path chunks'''
	result = []
	if path == '':
		return result
	current = ''
	parts = path.split('/')
	for part in parts:
		if len(current) > 0:
			current = current + '/'
		current = current + part
		result.append(current)
	return result

def where(iterator, param, value=True):
	result = []
	for item in iterator:
		if param in item:
			if isinstance(value, bool): # check item just has a param
				result.append(item)
			elif isinstance(value, str): # for strings check starts with
				if item[param].startswith(value):
					result.append(item)
			elif isinstance(value, int): # for numbers check equality
				if item[param] == value:
					result.append(item)
	return result

from PIL import Image
def get_thumbnail(value, size=(100, 100)):
	file_path = BUILD_DIR + value
	file, ext = os.path.splitext(file_path)
	path = (file + '-%dx%d' + ext) % size
	im = Image.open(file_path)
	im.thumbnail(size, Image.ANTIALIAS)
	im.save(path, "JPEG")
	return path[len(BUILD_DIR) : ]

env.tests['equalto'] = lambda value, other : value == other
env.filters['where'] = where
env.filters['breadcrumbs'] = breadcrumbs
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


# =============================================================================
# options
# =============================================================================

def options():
    """Parse and validate command line arguments."""

    usage = ("Usage: %prog --build [OPTIONS] [path/to/project]\n"
             "       %prog --serve [OPTIONS] [path/to/project]\n"
             "\n"
             "       Project path is optional, '.' is used as default.")

    op = optparse.OptionParser(usage=usage)

    op.add_option("-b" , "--build", action="store_true", default=False,
                  help="build project")
    op.add_option("-s" , "--serve", action="store_true", default=False,
                  help="serve project")

    og = optparse.OptionGroup(op, "Serve options")
    og.add_option("" , "--port", default=1313,
                  metavar="PORT", type="int",
                  help="port for serving (default: 1313)")
    op.add_option_group(og)

    opts, args = op.parse_args()

    if opts.build + opts.serve < 1:
        op.print_help()
        op.exit()

    opts.project = args and args[0] or "."

    return opts

# =============================================================================
# main
# =============================================================================

def main():

    opts = options()

    if opts.build:
        generate()
    if opts.serve:
        serve(opts.port)

if __name__ == '__main__':
    main()
