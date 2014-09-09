'''

Created on Nov 21, 2013

@author: alberto

'''

# Import the relevant libraries
import sys,os,logging,csv
import psycopg2
import urllib2
import requests
import json
import codecs


import time
from pytz import timezone
from datetime import datetime
from dateutil import tz
from datetime import timedelta
from lxml import html



# Set the Places API key for your application
KEY_ARRAY = ['AIzaSyD4dui7FVSpUwpnrTrMN6NVXoT-C3lYTuI','AIzaSyCXOCzjUG83ysKqf4oEtgVlHoxWsC7iIVo', 'AIzaSyBXunz47Yja0aLmUGAu3vk0xqZG9WmQ3y4',
             'AIzaSyDJhi_xxxGi40Nnzyr6Ecy6F_PeWVGumMs','AIzaSyBAsRqfCX7h7YXyUSdw61Z3LTHc-KT1EZY', 
             'AIzaSyCDVMO3-PEsnU22lgvjp0ltnqMwW4R8TE4', 'AIzaSyAi-0KQ7UfzdbVefQ-v5CVbfyCif25Pq-U',
             'AIzaSyCt2nJvUU0YDNK24Bg9rNFH0HxW7C2I0bo', 'AIzaSyDdxVDEz0tAVh6199Rz-fjZnp4h2Sf-rIo', 'AIzaSyDva2nYRJnjiQ-BW-I67_5m7GxA_19gA7Y',
             'AIzaSyBFD-5MKrHvcu2vtCI630fhGWpzBPEZqdk', 'AIzaSyCvfId0lM9v_F2igUi4AIRbFJHr8IlMFAY',
             'AIzaSyAwwAQHYJ29SkL3Ipi9JO-15mR5OXNIUl0', 'AIzaSyAZVLuVEQ8VfkBfHgpME9RGkvwyzJYXfGo', 'AIzaSyCtc-W3m2xFf_j9Qi4Axvfqe2lonkR2Uy8']
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
LIMIT = 500

# Define api_key array index
KEY_ARRAY_INDEX = 0
AUTH_KEY = KEY_ARRAY[KEY_ARRAY_INDEX]

# Define the radius (in meters) for the api search (Don't apply when ranking by distance)
RADIUS = 10000

# Define the type of places separated by |
TYPE = 'establishment'

# Define the language
LANGUAGE ='en'

# Define the search: distance, prominence or radarsearch
SEARCH ='radar'

'''
DB LOG OPEN
'''
def open_log(logger_name, filename, level):
    try:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        fh = logging.FileHandler(filename)
        fh.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger
    except:
        raise Exception("Error opening log file!")

def log(string, log_dict, logger, level):
    #print "[ %s ]%s" % (datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f"), string)
    log_dict[logger][level](string)
            
def get_chain_places(chain_name, pagetoken=False, location=False, polygon_id=-1):
    
    # Get time
    gPstart = datetime.now()
                
    # Compose a URL to query a location 
    if not pagetoken:
        if SEARCH == 'distance':
            # Search with "rank by distance"
            params = {'location' : location, 'rankby' : 'distance', 'types': TYPE, 'language' : LANGUAGE, 'sensor' : 'false', 'name' : chain_name, 'key' : AUTH_KEY}
            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
#             print '%s\n' % (url)
        elif SEARCH == 'prominence':
            # Search with "prominece with radius"
            params = {'location' : location, 'radius' : RADIUS, 'types': TYPE, 'language' : LANGUAGE, 'sensor' : 'false', 'name' : chain_name, 'key' : AUTH_KEY}
            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
#             print '%s\n' % (url)
        else:
            # Search with "radarsearch"
            params = {'location' : location, 'radius' : RADIUS, 'types': TYPE, 'language' : LANGUAGE, 'sensor' : 'false', 'name' : chain_name, 'key' : AUTH_KEY}
            url = 'https://maps.googleapis.com/maps/api/place/radarsearch/json'
#             print '%s\n' % (url)
    else:
        if SEARCH == 'distance':
            # Search with "rank by distance"
            params = {'location' : location, 'rankby' : 'distance', 'types': TYPE, 'language' : LANGUAGE, 'pagetoken': pagetoken, 'sensor' : 'false', 'name' : chain_name, 'key' : AUTH_KEY}
            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
#             print '%s\n' % (url)
        elif SEARCH == 'prominence':
            # Search with "prominece with radius"
            params = {'location' : location, 'radius' : RADIUS, 'types': TYPE, 'language' : LANGUAGE, 'pagetoken': pagetoken, 'sensor' : 'false', 'name' : chain_name, 'key' : AUTH_KEY}
            url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'


    # Send the GET request to the Place details service (using url from above)    
    
    try:
        response = requests.get(url,headers={'User-agent': 'Mozilla/5.0 (Linux i686)'},params=params)
        json_data = response.json()
    except Exception as e:
        log('ERROR GETTING PAGE!', log_dict, 'error_logger','critical')
        log(e, log_dict, 'error_logger','critical')
        return 500
    
    # Get the response and use the JSON library to decode the JSON
#     json_raw = response.read()
    
        
#     # Conection to DB
#     try:
#         conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
#     except:
#         log('Connection Failed', log_dict, 'error_logger','critical')
    
#     cur = conn.cursor()
    
    # Iterate through the results and insert into the DB
    status = json_data['status']
    if status == 'OK':
        for place in json_data['results']:
            log(place, log_dict, 'places_logger','debug')
            idp = place['id'].encode("utf-8")
            reference = place['reference'].encode("utf-8")
            
#             cur.execute('SELECT 1 FROM place WHERE id=%s', [idp])
#             conn.commit()    
            if 'reference' in place:# and cur.rowcount == 0:
                status_details = get_chain_details(reference, polygon_id,chain_name)    
                
                if status_details == 'OVER_QUERY_LIMIT':
                    return status_details        
                elif status_details == 500:
                    return 500
        
    #     print '%s: %s, %s\n' % (idp, lat , reference)
    elif status == 'ZERO_RESULTS':
        # No results
        log('%s: %s \n' % ('ZERO_RESULTS', response.url), log_dict, 'error_logger','critical')
        
    elif status == 'OVER_QUERY_LIMIT':
        # change api_key or stop
        log('%s: %s \n' % ('OVER_QUERY_LIMIT', response.url), log_dict, 'error_logger','critical')
        return status
        
    elif status == 'REQUEST_DENIED':
        # deny conection, usually sensor information
        log('%s: %s \n' % ('REQUEST_DENIED', response.url), log_dict, 'error_logger','critical')
        return status
        
    elif status == 'INVALID_REQUEST':
        # deny conection, usually sensor information or not enought time to process pagetoke
        log('%s: %s \n' % ('INVALID_REQUEST Places', response.url), log_dict, 'error_logger','critical')
            
    else:
        log('%s: %s \n' % ('We Fucked up something!', response.url), log_dict, 'error_logger','critical')

    
#     if conn:
#         conn.close()
    
    if 'next_page_token' in json_data:
        next_page_token = json_data['next_page_token']
        gPnow = datetime.now()
        gPresto = int(gPnow.strftime('%s')) - int(gPstart.strftime('%s')) # seconds more
#         print gPresto
        if gPresto < 2:
            time.sleep( 2 )
        getPlaces(next_page_token, location, polygon_id)
                        
                        
def get_chain_details(reference, polygon_id,chain_name):
    # Compose a URL to query place details
    params = {'reference' : reference, 'language' : LANGUAGE, 'sensor' : 'false', 'key' : AUTH_KEY}
    url = 'https://maps.googleapis.com/maps/api/place/details/json'
    
#     print '%s\n' % (url)
    # Send the GET request to the Place details service (using url from above)
#     request = urllib2.Request(url)
#     request.add_header('User-agent', 'Mozilla/5.0 (Linux i686)')
    try:
        response = requests.get(url,headers={'User-agent': 'Mozilla/5.0 (Linux i686)'},params=params)
        json_data = response.json()
    except Exception as e:
        log('ERROR GETTING PAGE!', log_dict, 'error_logger','critical')
        log(e, log_dict, 'error_logger','critical')
        return 500
    # Get the response and use the JSON library to decode the JSON
#     json_raw = response.read()    
    
#     response.close()
        
    # Conection to DB
    try:
        conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
    except:
        log('Connection Failed', log_dict, 'error_logger','critical')
        
    
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
            cur.execute("BEGIN")
            cur.execute("SELECT id from chain where id=%s for update", (idp,))
            exists = cur.fetchone()
            if exists is not None:
                log("UPDATING", log_dict, 'places_logger','debug')
                log(idp, log_dict, 'places_logger','debug')
                cur.execute('UPDATE chain SET id=%s, name=%s, lat=%s, lng=%s, address=%s, rating=%s, reference=%s, website=%s, url_g=%s, phone=%s, place_polygon_id=%s,chain_name=%s,geom=(SELECT ST_SetSRID(ST_MakePoint(%s,%s),4326)) WHERE id=%s', (idp, name, lat, lng, address, rating, reference, website, url_g , phone, polygon_id,chain_name, lng,lat,idp))
                conn.commit()
            else:
                log("INSERTING", log_dict, 'places_logger','debug')
                log(idp, log_dict, 'places_logger','debug')
                cur.execute('INSERT INTO chain (id, place_polygon_id, name, lat, lng, address, rating, reference, website, url_g, phone, geom,chain_name) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s ,%s ,%s, %s, (SELECT ST_SetSRID(ST_MakePoint(%s,%s),4326)),%s)', (idp, polygon_id, name, lat, lng, address, rating, reference, website, url_g , phone,lng,lat,chain_name,))
                conn.commit()
        except:
            log("UPSERT FAIL!", log_dict, 'error_logger','critical')
            log(exists, log_dict, 'error_logger','critical')
            log("idp = %s" % idp, log_dict, 'error_logger','critical')
            
        else:    
            #Delete relation place - type
            cur.execute('DELETE from chain_type where chain_id=%s', (idp,))
            conn.commit()    
              
            # Insert Google plus types
            if url_g.find('plus.google.com') != -1:
                get_chain_types(url_g, idp)
            else: 
                log(url_g, log_dict, 'error_logger','critical')
              
            # Insert API Types
            for type in place['types']:
                insert_chain_type(type, 'API', idp)
        


    elif status == 'ZERO_RESULTS':
        # No results, close place
        # TODO delete place
        log('%s: %s \n' % ('ZERO_RESULTS', response.url), log_dict, 'error_logger','critical')
        
        
    elif status == 'OVER_QUERY_LIMIT':
        # change api_key or stop
        log('%s: %s \n' % ('OVER_QUERY_LIMIT', response.url), log_dict, 'error_logger','critical')
        return status
        
    elif status == 'REQUEST_DENIED':
        # deny conection, usually sensor information
        log('%s: %s \n' % ('REQUEST_DENIED', response.url), log_dict, 'error_logger','critical')
        return status
        
    elif status == 'INVALID_REQUEST':
        # mising reference
        log('%s: %s \n' % ('INVALID_REQUEST Places', response.url), log_dict, 'error_logger','critical')
        
    else:
        log('%s: %s \n' % ('We Fuck up something!', response.url), log_dict, 'error_logger','critical')        

    if conn:
        conn.close()
        
def get_chain_types(url_g, chain_id):
    
    try:        
        r = requests.get(url_g)
        
        data = r.text
    
        soup = html.fromstring(data)
        
        # Skip first element
        tags = soup.xpath('//span[@class="d-s JPa Jhb"]')
        for tag in tags[1:]:
            str = tag.get('data-payload')
            str = str.lower()
            str = str.replace(" ", "_")
            
            if str.find('...') == -1 and str.strip():
                insert_chain_type(str,'GP', chain_id)
#             else:
#                print str.encode("utf-8")
    
    except requests.exceptions.RequestException as e:
        # Add a type for the missing Google Plus Types so we can keep track of the place and update it        

        r = requests.get(url_g)
        data = r.text
        
        insert_chain_type('MGPT','GP', chain_id)
        log('%s: %s \n %s \n' % (chain_id, url_g, e), log_dict, 'error_logger','critical')
    
    
    
def insert_chain_type(type, origin, chain_id):
    
    # Conection to DB
    try:
        conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
    except:
        log('Connection Failed', log_dict, 'error_logger','critical')
    
    cur = conn.cursor()
    
    cur.execute('INSERT INTO type (name_en, origin) SELECT %s, %s WHERE NOT EXISTS (SELECT 1 FROM type WHERE name_en=%s)', (type, origin, type))
    conn.commit()
    
    cur.execute('SELECT id FROM type where name_en=%s ', [type])
    type_id = cur.fetchall()    
    conn.commit()
    
    try:
        cur.execute('INSERT INTO chain_type (chain_id, type_id) SELECT %s, %s WHERE NOT EXISTS (SELECT 1 FROM chain_type WHERE (chain_id=%s AND type_id=%s))', (chain_id, type_id[0], chain_id, type_id[0]))
    except psycopg2.IntegrityError:
        conn.rollback()
    else:
        conn.commit()
    
    if conn:
        conn.close()


# -----------------------------------------------------------------------------------------------------------------------------------------------------



places_log_file = open_log("placesLogger", "/home/alberto/scraping/places/logs/places_%s.log" % os.getpid(), "DEBUG")
error_log_file = open_log("errorLogger", "/home/alberto/scraping/places/logs/errors_%s.log" % os.getpid(), "DEBUG")
crit_error_log_file = open_log("criterrorLogger", "/home/alberto/scraping/places/logs/crit_errors_%s.log" % os.getpid(), "DEBUG")
log_dict = {
    'places_logger' : {
        'debug' : places_log_file.debug,
        'critical' : places_log_file.critical,
        'info' : places_log_file.info
    },
    'error_logger' : {
        'critical' : error_log_file.critical 
    },
    'crit_error_logger': {
        'critical' : crit_error_log_file.critical 
    }
}

done = False
# Las Vegas polygon
# polygon_id = 163534

# Conection to DB
try:
    conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
except:
    log('Connection Failed', log_dict, 'error_logger','critical')
    
cur = conn.cursor()

chain_names_file =  open('/home/alberto/scraping/places/chainnames.csv')
chain_names_reader = csv.reader(chain_names_file)
chain_names = []
for chain in chain_names_reader:
    chain_names.append(chain[0])

while not done:
    # cur.execute('SELECT lat, lng FROM point where scraped = FALSE and (polygon_id=92 or polygon_id=80 or polygon_id=100 or polygon_id=120)')
    cur.execute('BEGIN')
    cur.execute('SELECT ST_X(geom) as x, ST_Y(geom) as y, polygon_id,geom FROM chain_point where idx = FALSE order by polygon_id LIMIT %s for update', (LIMIT,))
    points = cur.fetchall()
    if cur.rowcount < 1:
        done = True
        conn.commit()
        conn.close()
        log('Done', log_dict, 'places_logger','info')
        break
    cur.execute('UPDATE chain_point SET idx = TRUE WHERE ST_ASTEXT(geom) in (SELECT ST_ASTEXT(geom) FROM chain_point where idx = FALSE order by polygon_id LIMIT %s)', [LIMIT])
    conn.commit()    
    
    for point in points:
        lat = point[1]
        lng = point[0]
        polygon_id = point[2]
        location = '%s,%s' % (lat, lng)
        log(location, log_dict, 'places_logger','debug')
        log(chain_names, log_dict, 'places_logger','debug')
        for chain in chain_names:
            try:
                log(chain, log_dict, 'places_logger','debug')
                res = get_chain_places(chain,False, location, polygon_id)
                while res == 'OVER_QUERY_LIMIT' or res == 'REQUEST_DENIED':
                    # Change api_key or stop
                    if KEY_ARRAY_INDEX == 0:
                        today = datetime.now(timezone('America/Los_Angeles'))
                        start = datetime(today.year, today.month, today.day, tzinfo=tz.tzutc())
                        end = start + timedelta(1)
                        resto = int(end.strftime('%s')) - int(today.strftime('%s')) + 60 # seconds more
                    if KEY_ARRAY_INDEX == len(KEY_ARRAY) - 1:             
                        log('OVER_QUERY_LIMIT and last key!', log_dict, 'error_logger','critical')
                        log('Key Index: %s' % KEY_ARRAY_INDEX, log_dict, 'error_logger','critical')
                        log('Will wait for %s' % resto, log_dict, 'error_logger','critical')
                        exit()       
#                         time.sleep(resto)
#                         KEY_ARRAY_INDEX = 0                    
#                         AUTH_KEY = KEY_ARRAY[KEY_ARRAY_INDEX]
#                         res = get_chain_places(chain,False, location, polygon_id)
                    else:
                        KEY_ARRAY_INDEX = KEY_ARRAY_INDEX + 1
                        AUTH_KEY = KEY_ARRAY[KEY_ARRAY_INDEX]
                        res = get_chain_places(chain,False, location, polygon_id)
                
                cur.execute('BEGIN')
                cur.execute('UPDATE chain_point SET scraped = TRUE where lat=%s and lng=%s', (lat, lng))
                conn.commit()
            except Exception as e:
                log('something failed!', log_dict, 'crit_error_logger','critical')
                log(e, log_dict, 'crit_error_logger','critical')
                pass       
            
if conn:
    conn.close()
