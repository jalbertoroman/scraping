'''

Created on Nov 21, 2013

@author: alberto

'''

# Import the relevant libraries
import sys
import psycopg2
import urllib2
import requests
import json
import codecs

import time
from datetime import datetime
from dateutil import tz
from datetime import timedelta
from bs4 import BeautifulSoup



# Set the Places API key for your application
KEY_ARRAY = ['AIzaSyD4dui7FVSpUwpnrTrMN6NVXoT-C3lYTuI','AIzaSyCXOCzjUG83ysKqf4oEtgVlHoxWsC7iIVo', 'AIzaSyBXunz47Yja0aLmUGAu3vk0xqZG9WmQ3y4']
# More keys:  
# AIzaSyDLtz4_hWO-iGpy5RT8SxZi-YcZTZYTVXY
# AIzaSyBAsRqfCX7h7YXyUSdw61Z3LTHc-KT1EZY
# AIzaSyAiFpFd85eMtfbvmVNEYuNds5TEF9FjIPI
# AIzaSyCS2F_UYmpRzCRhHv4aT7pBdaWRqvA42U8
# AIzaSyCDVMO3-PEsnU22lgvjp0ltnqMwW4R8TE4
# AIzaSyAi-0KQ7UfzdbVefQ-v5CVbfyCif25Pq-U
# AIzaSyCt2nJvUU0YDNK24Bg9rNFH0HxW7C2I0bo
# AIzaSyDdxVDEz0tAVh6199Rz-fjZnp4h2Sf-rIo
# AIzaSyDva2nYRJnjiQ-BW-I67_5m7GxA_19gA7Y
# AIzaSyBFD-5MKrHvcu2vtCI630fhGWpzBPEZqdk
# AIzaSyDSnWK7NpyWvXoOsF22VZEXWPihK2Jp4Mg
# AIzaSyCvfId0lM9v_F2igUi4AIRbFJHr8IlMFAY
# AIzaSyAwwAQHYJ29SkL3Ipi9JO-15mR5OXNIUl0
# AIzaSyAZVLuVEQ8VfkBfHgpME9RGkvwyzJYXfGo
# AIzaSyCtc-W3m2xFf_j9Qi4Axvfqe2lonkR2Uy8

#Define number of point per request
LIMIT = 1

# Define api_key array index
KEY_ARRAY_INDEX = 0
AUTH_KEY = KEY_ARRAY[KEY_ARRAY_INDEX]

# Define the radius (in meters) for the api search (Don't aply when ranking by distance)
RADIUS = 500

# Define the type of places separated by |
TYPE = 'establishment'

# Define the language
LANGUAGE ='en'

# Define the search: distance or prominence
SEARCH ='distance'

def getPlaces(pagetoken=False, location=False):
	
	# Get time
	gPstart = datetime.now()
				
	# Compose a URL to query a location 
	if not pagetoken:
		if SEARCH == 'distance':
			# Search with "rank by distance"
			url = ('https://maps.googleapis.com/maps/api/place/search/json?location=%s&rankby=distance&types=%s&laguage=%s&sensor=false&key=%s') % (location, TYPE, LANGUAGE, AUTH_KEY)
# 			print '%s\n' % (url)
		else:
			# Search with "prominece with radius"
			url = ('https://maps.googleapis.com/maps/api/place/search/json?location=%s&radius=%s&types=%s&laguage=%s&sensor=false&key=%s') % (location, RADIUS, TYPE, LANGUAGE, AUTH_KEY)
# 			print '%s\n' % (url)
	else:
		if SEARCH == 'distance':
			# Search with "rank by distance"
			url = ('https://maps.googleapis.com/maps/api/place/search/json?location=%s&rankby=distance&types=%s&laguage=%s&pagetoken=%s&sensor=false&key=%s') % (location, TYPE, LANGUAGE, pagetoken, AUTH_KEY)
# 			print '%s\n' % (url)
		else:
			# Search with "prominece with radius"
			url = ('https://maps.googleapis.com/maps/api/place/search/json?location=%s&radius=%s&types=%s&laguage=%s&pagetoken=%s&sensor=false&key=%s') % (location, RADIUS, TYPE, LANGUAGE, pagetoken, AUTH_KEY)
# 			print '%s\n' % (url)

		# 		print '%s\n' % (url)
		
	# Send the GET request to the Place details service (using url from above)	
	request = urllib2.Request(url)
	request.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')

	response = urllib2.urlopen(request)
	
	# Get the response and use the JSON library to decode the JSON
	json_raw = response.read()
	json_data = json.loads(json_raw)
	response.close()
	
	f = codecs.open('/home/alberto/scraping/places/logs/places_error_log.csv', 'a', 'utf-8')
	
	# Conection to DB
	try:
		conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
	except:
		f.write('%s: %s \n' % ('Connection Failed', time.time()))
	
	cur = conn.cursor()
		
	# Iterate through the results and insert into the DB
	status = json_data['status']
	if status == 'OK':
	  	  
	  for place in json_data['results']:
	  	
	  	idp = place['id'].encode("utf-8")
	  	reference = place['reference'].encode("utf-8")
	  	
	  	cur.execute('SELECT 1 FROM place WHERE id=%s', [idp])
	  	conn.commit()	
	  	
		if 'reference' in place and cur.rowcount == 0:
			status_details = getDetails(reference)	
			
			if status_details == 'OVER_QUERY_LIMIT':
				return status_details		
		
	#     print '%s: %s, %s\n' % (idp, lat , reference)
	elif status == 'ZERO_RESULTS':
		# No results
		f.write('%s: %s \n' % ('ZERO_RESULTS', url))
		
	elif status == 'OVER_QUERY_LIMIT':
		# change api_key or stop
		return status
		f.write('%s: %s \n' % ('OVER_QUERY_LIMIT', url))
		
	elif status == 'REQUEST_DENIED':
		# deny conection, usually sensor information
		f.write('%s: %s \n' % ('REQUEST_DENIED', url))
		
	elif status == 'INVALID_REQUEST':
		# deny conection, usually sensor information or not enought time to process pagetoke
 		f.write('%s: %s \n' % ('INVALID_REQUEST Places', url))
			
	else:
		f.write('%s: %s \n' % ('We Fuck up something!', url))

	f.close()	
	
	if conn:
		conn.close()
	
	if 'next_page_token' in json_data:
		next_page_token = json_data['next_page_token']
		gPnow = datetime.now()
		gPresto = int(gPnow.strftime('%s')) - int(gPstart.strftime('%s')) # seconds more
# 		print gPresto
		if gPresto < 2:
			time.sleep( 2 )
		getPlaces(next_page_token,location)
	
			
def getDetails(reference):
	# Compose a URL to query place details
	url = ('https://maps.googleapis.com/maps/api/place/details/json?reference=%s&laguage=%s&sensor=false&key=%s') % (reference, LANGUAGE, AUTH_KEY)
# 	print '%s\n' % (url)
				
	# Send the GET request to the Place details service (using url from above)
	request = urllib2.Request(url)
	request.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')

	response = urllib2.urlopen(request)
	
	# Get the response and use the JSON library to decode the JSON
	json_raw = response.read()	
	json_data = json.loads(json_raw)
	response.close()
	
	f = codecs.open('/home/alberto/scraping/places/logs/places_error_log.csv', 'a', 'utf-8')
	
	# Conection to DB
	try:
		conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
	except:
		f.write('%s: %s \n' % ('Connection Failed', time.time()))
	
	cur = conn.cursor()
		
	# Iterate through the results and insert into the DB
	status = json_data['status']
	if status == 'OK':
		place = json_data['result']
		
		idp = place['id'].encode("utf-8")
		name = place['name'].encode("utf-8")
		reference = place['reference'].encode("utf-8")
		lat = place['geometry']['location']['lat']
		lng = place['geometry']['location']['lng']
		
	  	if 'rating' in place:
	  		rating = place['rating']
	  	else:
	  		rating = 0.0
	  		
	  	if 'formatted_address' in place:
	  		address = place['formatted_address'].encode("utf-8")
	  	elif 'vicinity' in place:
	  		address = place['vicinity'].encode("utf-8")
	  	else:
	  		address = ''
	  		
	  	if 'website' in place:
	  		website = place['website']
	  	else:
	  		website = ''
	  		
	  	if 'international_phone_number' in place:
	  		phone = place['international_phone_number']
	  	else:
	  		phone = ''
	  		  	
	  	if 'url' in place:
	  		url_g = place['url']
	  	else:
	  		url_g = ''
	  		
		try:
			cur.execute('UPDATE place SET id=%s, name=%s, lat=%s, lng=%s, address=%s, rating=%s, reference=%s, website=%s, url_g=%s, phone=%s WHERE id=%s', 
				(idp, name, lat, lng, address, rating, reference, website, url_g , phone, idp))
			
			cur.execute('INSERT INTO place ( id, name, lat, lng, address, rating, reference, website, url_g, phone ) SELECT %s, %s, %s, %s, %s, %s, %s, %s ,%s ,%s WHERE NOT EXISTS (SELECT 1 FROM place WHERE id=%s)', 
				(idp, name, lat, lng, address, rating, reference, website, url_g , phone, idp))
			conn.commit()
			
		except:
			f.write('%s: %s, %s, %s, %s \n' % ('Fail to Upsert', name, reference, url, time.time()))
		
		#Delete relation place - type 
	  	cur.execute('DELETE from place_type where place_id=%s', [idp])
	  	conn.commit()	
	  	
	  	# Insert Google plus types
		if url_g.find('plus.google.com') != -1:
	  		getTypes(url_g, idp)
	  	else: 
	  		print url_g
	  	
	  	# Insert API Types
	  	for type in place['types']:
	  		insertType(type, 'API', idp)	

	
	#     print '%s: %s, %s\n' % (idp, lat , reference)
	elif status == 'ZERO_RESULTS':
		# No results, close place
		# TODO delete place
		f.write('%s: %s \n' % ('ZERO_RESULTS', url))
		
	elif status == 'OVER_QUERY_LIMIT':
		# change api_key or stop
		return status
		f.write('%s: %s \n' % ('OVER_QUERY_LIMIT', url))
		
	elif status == 'REQUEST_DENIED':
		# deny conection, usually sensor information
		f.write('%s: %s \n' % ('REQUEST_DENIED', url))
		
	elif status == 'INVALID_REQUEST':
		# mising reference
		f.write('%s: %s \n' % ('INVALID_REQUEST Details', url))	
		
	else:
		f.write('%s: %s \n' % ('We Fuck up something!', url))
		
	f.close()

	if conn:
		conn.close()
		
def getTypes(url_g, place_id):
	
	try:		
		r = requests.get(url_g)
		
		data = r.text
	
		soup = BeautifulSoup(data)
		
		# Skip first element
		for tag in soup.find_all('span', class_='d-s JPa Jhb')[1:]:
			str = tag.get('data-payload')
			str = str.lower()
			str = str.replace(" ", "_")
			
			if str.find('...') == -1 and str.strip():
				insertType(str,'GP', place_id)
# 			else:
#				print str.encode("utf-8")
	
	except requests.exceptions.RequestException as e:
		# Add a type for the missing Google Plus Types so we can keep track of the place and update it		

		r = requests.get(url_g)
		data = r.text
		
		insertType('MGPT','GP', place_id)
		f = codecs.open('/home/alberto/scraping/places/logs/places_error_log.csv', 'a', 'utf-8')
		f.write('%s: %s \n %s \n' % (place_id, url_g, e))
		f.close()
    
	
	
def insertType(type, origin, place_id):
	
	# Conection to DB
	try:
		conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
	except:
		f.write('%s: %s \n' % ('Connection Failed', time.time()))
	
	cur = conn.cursor()
	
	cur.execute('INSERT INTO type (name_en, origin) SELECT %s, %s WHERE NOT EXISTS (SELECT 1 FROM type WHERE name_en=%s)', (type, origin, type))
	conn.commit()
	
	cur.execute('SELECT id FROM type where name_en=%s ', [type])
	type_id = cur.fetchall()	
	conn.commit()
	
	try:
		cur.execute('INSERT INTO place_type (place_id, type_id) SELECT %s, %s WHERE NOT EXISTS (SELECT 1 FROM place_type WHERE (place_id=%s AND type_id=%s))', (place_id, type_id[0], place_id, type_id[0]))
	except psycopg2.IntegrityError:
		conn.rollback()
	else:
		conn.commit()
	
	if conn:
		conn.close()


# -----------------------------------------------------------------------------------------------------------------------------------------------------


done = False

# Conection to DB
try:
	conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
except:
	f.write('%s: %s \n' % ('Connection Failed', time.time()))
	
cur = conn.cursor()

while not done:
	# cur.execute('SELECT lat, lng FROM point where scraped = FALSE and (polygon_id=92 or polygon_id=80 or polygon_id=100 or polygon_id=120)')
	cur.execute('BEGIN')
	cur.execute('SELECT ST_X(geom) as x, ST_Y(geom) as y FROM point where idx = FALSE LIMIT %s', [LIMIT])
	points = cur.fetchall()
	if cur.rowcount < 1:
		done = True
		cur.execute('COMMIT')
		conn.commit()
		conn.close()
		print ('Done: %s' % time.time())
		break
	cur.execute('UPDATE point SET idx = TRUE WHERE ST_ASTEXT(geom) in (SELECT ST_ASTEXT(geom) FROM point where idx = FALSE LIMIT %s)', [LIMIT])
	cur.execute('COMMIT')
	conn.commit()	

	for point in points:
		lat = point[1]
		lng = point[0]
		location = '%s,%s' % (lat, lng)
		print location
	 	res = getPlaces(False, location)
		if res == 'OVER_QUERY_LIMIT':
			#Change api_key or stop
			if KEY_ARRAY_INDEX == len(KEY_ARRAY) - 1:
				today = datetime.now(timezone('America/Los_Angeles'))
				start = datetime(today.year, today.month, today.day, tzinfo=tz.tzutc())
				end = start + timedelta(1)
				resto = int(end.strftime('%s')) - int(today.strftime('%s')) + 60 # seconds more
				time.sleep(resto)
				print 'OVER_QUERY_LIMIT'
			else:
				KEY_ARRAY_INDEX = KEY_ARRAY_INDEX + 1
				AUTH_KEY = KEY_ARRAY[KEY_ARRAY_INDEX]
				getPlaces(False, location)
		else:
			cur.execute('UPDATE point SET scraped = TRUE where lat=%s and lng=%s', (lat, lng))
			conn.commit() 		
			
if conn:
	conn.close()