import psycopg2
import alternate_extractor, user_agent_extractor
from bs4 import BeautifulSoup


# Conection to DB
try:
	conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
except:
	print('%s: %s \n' % ('Connection Failed', time.time()))

cur = conn.cursor()

#  Get websites from DB
try:
	cur.execute("SELECT name, website, id FROM place WHERE website != ''")
			
except:
	print('Fail to do SELECT')


places = cur.fetchall()

for place in places:
	
	place_name = place[0]
	place_web = place[1]
	place_id = place[2]

# 	Add http://to the begin of the url	
	if not place_web.startswith('http'):
		place_web = 'http://' + place_web
	
# 	Open url with urllib and beautifulsoup
	try:
		sock = urllib2.urlopen(place_web)
		soup = BeautifulSoup(sock)
		
	except urllib2.HTTPError, e:
# 		print('HTTPError = ' + str(e.code) + place_web)
		continue
	except urllib2.URLError, e:
# 		print('URLError = ' + str(e.reason) + place_web)
		continue
	except httplib.HTTPException, e:
# 		print('HTTPException ' + place_web)
		continue
	except Exception:
# 		import traceback
# 		print('generic exception: ' + traceback.format_exc() + ' ' + place_web)
		continue
		
		
# 	-------------	
# 	SEARCH FOR rel=alternate DEFINED IN HEAD AS <link rel=alternate />				
# 	-------------
	possible_alternate = alternate_extractor.extract(soup)
	
	if possible_alternate:
		print 'MOBILE WEB (rel=alternate): ' + place_name + ' - ' + place_web
		cur.execute('UPDATE place SET has_mobile_web = 1 where id = %s', place_id)
		cur.commit()
		has_mobile_web = True
		continue
		
	else:

#	 	-------------	
# 		SEARCH FOR navigator.userAgent AND android IN JAVASCRIPT SCRIPTS <script type='text/javascript' />
# 		-------------		
		user_agent_found = user_agent_extractor.extract(soup, cur, place_id)
		
		if user_agent_found:
			has_mobile_web = True
			continue
			
		else:
		
# 			-------------			
# 			SEARCH FOR @MEDIA ONLY SCREEN IN CSS FILES DEFINED IN <style type='text/css' />
# 			-------------
			media_style_found = media_only_screen_extractor_style.extract(soup, cur, place_id)
			
			if media_style_found:
				has_mobile_web = True
				continue
				
			else:
			
# 				-------------	
# 				SEARCH FOR @MEDIA ONLY SCREEN IN CSS FILES DEFINED AS <link type='text/css' />				
# 					-------------
				media_link_found = media_only_screen_extractor_link.extract(soup, cur, place_id)
				
				if media_link_found:
					has_mobile_web = True
					continue
					
				else:
					cur.execute('UPDATE place SET has_mobile_web = 0 where id = %s', place_id)
					cur.commit()