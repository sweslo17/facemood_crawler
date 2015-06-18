#coding=utf-8
import requests
import json
import time
import mysql.connector
import datetime
import config
import HTMLParser
import sys
import hashlib
from bs4 import BeautifulSoup
import re

cnx = mysql.connector.connect(host=config.db_host,user=config.db_user,passwd=config.db_password,database=config.db_database)
cur = cnx.cursor()
def write_types(types):
	sql = "REPLACE INTO types (id,name) VALUES (%s,%s)"
	for type in types:
		cur.execute(sql,type)

def write_words(type_id,word_list):
	sql = "REPLACE INTO words (word_md5,word,type_id,likes) VALUES (%s,%s,%s,%s)"
	for word in word_list:
		m = hashlib.md5()
		m.update(word[0])
		word_md5 = m.hexdigest()
		cur.execute(sql,(word_md5,word[0],type_id,word[1]))
	cnx.commit()

def get_types(url):
	soup = BeautifulSoup(requests.get(url).content)
	types = []
	for type_tag in soup.find(class_="tagMenu").find_all("a"):
		name = type_tag.get_text().strip()
		id = type_tag['href'].split('=')[-1]
		types.append((id,name))
	return types

def parse_words_page(url):
	word_list = []
	p = re.compile(ur'str=(.+)">', re.UNICODE)
	soup = BeautifulSoup(requests.get(url).content)
	h = HTMLParser.HTMLParser()
	for word_tag in soup.find_all(class_="facemoodItem"):
		word = re.search(p, str(word_tag.find("param",attrs={'name':"flashvars"}))).group(1).strip()
		word = h.unescape(word.decode('utf-8')).encode('utf-8')
		likes = int(word_tag.find(class_='faceLikeCount').get_text())
		word_list.append((word,likes))
	return word_list

def get_word_list(type_id):
	word_list = []
	for page in range(1,100):
		temp_list = []
		print 'http://facemood.grtimed.com/index.php?view=facemood&tid='+type_id+'&page='+str(page)
		temp_list = parse_words_page('http://facemood.grtimed.com/index.php?view=facemood&tid='+type_id+'&page='+str(page))
		if len(temp_list) != 0:
			word_list += temp_list
		else:
			break
	return word_list

def crawl():
	types = get_types('http://facemood.grtimed.com/index.php')
	write_types(types)
	for type in types:
		type_id = type[0]
		word_list = get_word_list(type_id)
		write_words(type_id,word_list)

if __name__ == '__main__':
	crawl()
