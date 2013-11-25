'''

Created on Nov 21, 2013

@author: alberto

'''

# Import the relevant libraries
import urllib2
import json
import psycopg2
import sys
import time
from bs4 import BeautifulSoup
import requests

# Set the Places API key for your application
AUTH_KEY = 'AIzaSyD4dui7FVSpUwpnrTrMN6NVXoT-C3lYTuI'

# Define the radius (in meters) for the search
RADIUS = 500 #Don't aply when ranking by distance

# Define the type of places
TYPE = 'establishment'

# Define the language
LANGUAGE ='es'

def getPlaces(pagetoken=False, location=False):
	# Compose a URL to query a location 
	if not pagetoken:
		url = ('https://maps.googleapis.com/maps/api/place/search/json?location=%s&rankby=distance&types=%s&laguage=%s&sensor=false&key=%s') % (location, TYPE, LANGUAGE, AUTH_KEY)
		print '%s\n' % (url)
	else:
		url = ('https://maps.googleapis.com/maps/api/place/search/json?location=%s&rankby=distance&types=%s&laguage=%s&pagetoken=%s&sensor=false&key=%s') % (LOCATION, TYPE, LANGUAGE, pagetoken, AUTH_KEY)
		print '%s\n' % (url)
		
	# Send the GET request to the Place details service (using url from above)
	response = urllib2.urlopen(url)
	
	# Get the response and use the JSON library to decode the JSON
	json_raw = response.read()
	json_data = json.loads(json_raw)
	
	f = open('/home/alberto/scraping/logs/insert.csv', 'a')
	
	# Conection to DB
	try:
		conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
	except:
		f.write('%s: %s \n' % ('Connection Failed', time.time()))
		
	# Iterate through the results and insert into the DB
	status = json_data['status']
	if status == 'OK':
	  for place in json_data['results']:
	
	  	if 'rating' in place:
	  		rating = place['rating']
	  	else:
	  		rating = 0.0
	  		
	  	if 'formatted_address' in place:
	  		address = place['formatted_address']
	  	else:
	  		address = place['vicinity']
	  		
		cur = conn.cursor()
			
		try:
			cur.execute('UPDATE place SET id=%s, name=%s, lat=%s, lng=%s, address=%s, rating=%s, reference=%s WHERE id=%s', 
				(place['id'], place['name'], place['geometry']['location']['lat'], place['geometry']['location']['lng'], address, rating, place['reference'], place['id']))
			
			cur.execute('INSERT INTO place (id, name, lat, lng, address, rating, reference ) SELECT %s, %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM place WHERE id=%s)', 
				(place['id'], place['name'], place['geometry']['location']['lat'], place['geometry']['location']['lng'], address, rating, place['reference'], place['id']))
			conn.commit()
			
		except:
			f.write('%s: %s, %s, %s, %s \n' % ('Fail to Upsert', place['name'], place['reference'], url, time.time()))
		
		if 'reference' in place:
			reference = place['reference']
			getDetails(reference)
			
		
		
	#     print '%s: %s, %s\n' % (place['id'], place['geometry']['location']['lat'] , place['reference'])
	elif status == 'ZERO_RESULTS':
		# No results
		f.write('%s: %s \n' % ('ZERO_RESULTS', url))
		
	elif status == 'OVER_QUERY_LIMIT':
		# change api_key or stop
		f.write('%s: %s \n' % ('OVER_QUERY_LIMIT', url))
		
	elif status == 'REQUEST_DENIED':
		# deny conection, usually sensor information
		f.write('%s: %s \n' % ('REQUEST_DENIED', url))
		
	elif status == 'INVALID_REQUEST':
		# deny conection, usually sensor information or not enought time to process pagetoken
		f.write('%s: %s \n' % ('INVALID_REQUEST', url))	
		
	else:
		f.write('%s: %s \n' % ('We Fuck up something!', url))
		
	f.close()	
	
	if conn:
		conn.close()
	
	if 'next_page_token' in json_data:
		pagetoken = json_data['next_page_token']
		getPlaces(pagetoken)
			
def getDetails(reference):
	# Compose a URL to query place details
	url = ('https://maps.googleapis.com/maps/api/place/details/json?reference=%s&laguage=%s&sensor=false&key=%s') % (reference, LANGUAGE, AUTH_KEY)
	print '%s\n' % (url)
				
	# Send the GET request to the Place details service (using url from above)
	response = urllib2.urlopen(url)
	
	# Get the response and use the JSON library to decode the JSON
	json_raw = response.read()
	json_data = json.loads(json_raw)
	
	f = open('/home/alberto/scraping/logs/insert.csv', 'a')
	
	# Conection to DB
	try:
		conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
	except:
		f.write('%s: %s \n' % ('Connection Failed', time.time()))
		
	# Iterate through the results and insert into the DB
	status = json_data['status']
	if status == 'OK':
		place = json_data['result']
	
	  	if 'rating' in place:
	  		rating = place['rating']
	  	else:
	  		rating = 0.0
	  		
	  	if 'formatted_address' in place:
	  		address = place['formatted_address']
	  	else:
	  		address = place['vicinity']
	  		
	  	if 'website' in place:
	  		website = place['website']
	  	else:
	  		website = ''
	  		
	  	if 'url' in place:
	  		url_g = place['url']
	  		types_gplus = getTypes(url_g)
	  		# insertTypes (types_gplus)
	  	else:
	  		url_g = ''
	  	
	  	if 'international_phone_number' in place:
	  		phone = place['international_phone_number']
	  	else:
	  		phone = ''
	  		
		cur = conn.cursor()
			
		try:
			cur.execute('UPDATE place SET address=%s, rating=%s, reference=%s, website=%s, url_g=%s, phone=%s WHERE id=%s', 
				(address, rating, place['reference'], website, url_g , phone, place['id']))
			
			cur.execute('INSERT INTO place ( address, rating, reference, website, url_g, phone ) SELECT %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM place WHERE id=%s)', 
				(address, rating, place['reference'], website, url_g , phone, place['id']))
			conn.commit()
			
		except:
			f.write('%s: %s, %s, %s, %s \n' % ('Fail to Upsert', place['name'], place['reference'], url, time.time()))
		
		# Insert Types 
		types = []
	  	for type in place['types']:
	  		types.append(type)
# 	  	insertTypes(types)
	
	#     print '%s: %s, %s\n' % (place['id'], place['geometry']['location']['lat'] , place['reference'])
	elif status == 'ZERO_RESULTS':
		# No results, close place
		# TODO delete place
		f.write('%s: %s \n' % ('ZERO_RESULTS', url))
		
	elif status == 'OVER_QUERY_LIMIT':
		# change api_key or stop
		f.write('%s: %s \n' % ('OVER_QUERY_LIMIT', url))
		
	elif status == 'REQUEST_DENIED':
		# deny conection, usually sensor information
		f.write('%s: %s \n' % ('REQUEST_DENIED', url))
		
	elif status == 'INVALID_REQUEST':
		# mising reference
		f.write('%s: %s \n' % ('INVALID_REQUEST', url))	
		
	else:
		f.write('%s: %s \n' % ('We Fuck up something!', url))
		
	f.close()

	if conn:
		conn.close()
		
def getTypes(url_g):

	r = requests.get(url_g)
	
	data = r.text
	
	soup = BeautifulSoup(data)
	
	types = []
	
	for tag in soup.find_all('span', class_='d-s JPa Jhb'):
		types.append(tag.get('data-payload'))

# 	types = set(types)
	
	return types
	
# def insertTypes(types):
# 	for type in place['types']:
# 		INSERT INTO type (  ) 
# 		cur.execute('UPDATE place SET address=%s, rating=%s, reference=%s, website=%s, url_g=%s, phone=%s WHERE id=%s', 
# 			(address, rating, place['reference'], website, url_g , phone, place['id']))
# 		cur.execute('INSERT INTO place ( address, rating, reference, website, url_g, phone ) SELECT %s, %s, %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM place WHERE id=%s)', 
# 		(address, rating, place['reference'], website, url_g , phone, place['id']))
# 		conn.commit()
# 		print '%s \n' % (type)
# 

# Define the location coordinates
lat = 43.31353 
lng = -1.973274

polygon_type = "CC"

location = '%s,%s' % (lat, lng)

conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
cur = conn.cursor()

cur.execute("Select id, name from  polygon where type=%s", [polygon_type])

for item in cur.fetchall():
	
	
		
	# cur.execute("select id from polygon where ST_Contains((Select polygon where id=%s), ST_GeomFromText('POINT(%s %s)', 4326))", (area, lng, lat))
	
	cur.execute("Select polygon from polygon where id=%s", [item[0]])
	polygon = cur.fetchall()
	
	#Make grid each 500 meters
	cur.execute("SELECT makegrid(%s, 1000, 4326) from polygon", polygon)
	geo = cur.fetchall()
	
	cur.execute("Insert into  grids (name, geom, type) values (%s, %s, %s)", (item[1], geo[0], polygon_type))
	conn.commit()
	
	
	# cur.execute("Insert into  grids (name, polygon, type) values ('SS', %s, 'G')", (geo))
	# conn.commit()

# if points:
# 	#inside
# 	# getPlaces(location)
# 	#next point
# # 	print points
# 	f1 = open('/home/alberto/scraping/logs/points.txt', 'a')
# 	f1.write('%s\n' % (points))
# 	f1.close()
# else:
# 	# outside
# 	#next point
# 	print points
# 	




# Select 1 from polygon where ST_Intersects(ST_GeomFromText('POINT(-1.973274 43.31353)', 4326), polygon);
# select name from polygon where ST_Contains((Select polygon where id=92), ST_GeomFromText('POINT(-1.973274 43.31353)', 4326));


# getPlaces(location)