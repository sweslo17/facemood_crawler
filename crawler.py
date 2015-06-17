import requests
import json
import time
import mysql.connector
import datetime
import config
import sys
from bs4 import BeautifulSoup
import re

cnx = mysql.connector.connect(host=config.db_host,user=config.db_user,passwd=config.db_password,database=config.db_database)
cur = cnx.cursor()
def write_types(types):
	sql = "REPLACE INTO types (id,name) VALUES (%s,%s)"
	for type in types:
		cur.execute(sql,type)

def get_types(url):
	soup = BeautifulSoup(requests.get(url).content)
	types = []
	for type_tag in soup.find(class_="tagMenu").find_all("a"):
		#print type_tag
		name = type_tag.get_text().strip()
		id = type_tag['href'].split('=')[-1]
		types.append((id,name))
	return types

def parse_type_page(url):
	word_list = []
	p = re.compile(ur'str=(.+)">', re.UNICODE)
	soup = BeautifulSoup(requests.get(url).content)
	for word_tag in soup.find_all(class_="facemoodItem"):
		word = re.search(p, str(word_tag.find("param",attrs={'name':"flashvars"}))).group(1).strip()
		likes = int(word_tag.find(class_='faceLikeCount').get_text())
		word_list.append((word,likes))
		print (word,likes)
	return word_list


def crawl():
	types = get_types('http://facemood.grtimed.com/index.php')
	write_types(types)
	for type in types:
		type_id = type[0]
		word_list = []
		for page in range(1,2):
			temp_list = []
			temp_list = parse_type_page('http://facemood.grtimed.com/index.php?view=facemood&tid='+type_id+'&page='+str(page))
			if len(temp_list) != 0:
				word_list += temp_list
			else:
				break

if __name__ == '__main__':
	crawl()
	#parse_type_page('http://facemood.grtimed.com/index.php?view=facemood&tid=4&page=1')
