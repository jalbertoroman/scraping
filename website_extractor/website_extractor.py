import urllib2, urllib
import sys, psycopg2
import httplib, md5, time

from xml.dom import minidom
from bs4 import BeautifulSoup


# Conection to DB
try:
	conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
except:
	print('%s: %s \n' % ('Connection Failed', time.time()))

cur = conn.cursor()


try:
	cur.execute("SELECT name, website FROM place WHERE website != ''")
			
except:
	print('Fail to do SELECT')

places = cur.fetchall()

# eo = True
# while eo:

for place in places:
	
	place_name = place[0]
	place_web = place[1]
	
# 	place_name = ''
# 	place_web = 'http://www.bitez.com/'
# 	
# 	print(place_web)
		
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

# 	Define boolean to compare ALL alternate links of a url
	possible_alternate = False

	for link in soup.find_all('link'):

		if link.get('rel'):
			for rel in link.get('rel'):
				if rel == 'alternate':
					if link.get('hreflang') or link.get('type') or link.get('data-kss-base-url'):
						continue
						
					else:
						if link.get('media'): # FACEBOOK and old mobile web designing.   and link.get('media') != 'handheld' or link.get('media').contains('only screen and')
							if link.get('media') == 'handheld' or (link.string and 'only screen' in link.string):
								possible_alternate = True
							
						else:			
							href = link.get('href')
							if not href.endswith('.css'):
								possible_alternate = True
					
	if possible_alternate:
		print 'MOBILE WEB (rel=alternate): ' + place_name + ' - ' + place_web
		continue
		
		
# 	-------------	
# 	SEARCH FOR navigator.userAgent AND android IN JAVASCRIPT SCRIPTS <script type='text/javascript' />
# 	-------------
	for script in soup.find_all('script'):
	
		if script.text and 'navigator.userAgent' in script.text and 'android' in script.text:
			print 'USER AGENT (javascript): ' + place_name + ' - ' + place_web
			
# 		Search inside javascript scripts	
		else:
			if script.get('href'):
			
				script_url = link.get('href')
	
				# If scripts are saved as local urls
				if not script_url.startswith('http://') and not script_url.startswith('www.'):
					script_url = place_web + '/' + script_url
				
				try:
					script_web = urllib2.urlopen(script_url)
			
				except urllib2.HTTPError, e:
	# 				print str(e) + ' - ' + place_web
					continue
				except urllib2.URLError, e:
	# 				print str(e) + ' - ' + place_web
					continue
				except httplib.HTTPException, e:
	# 				print str(e) + ' - ' + place_web
					continue
				except Exception:
	# 				print 43534543
					continue
				
				script_text = script_web.read()
		
				if 'android' in script_text and 'navigator.userAgent' in script_text:
					print 'USER AGENT (javascript/inside): ' + place_name + ' - ' + place_web
					break

# 	-------------			
# 	SEARCH FOR @MEDIA ONLY SCREEN IN CSS FILES DEFINED IN <style type='text/css' />
# 	-------------	
	for css in soup.find_all('style'):
	
		if css.get('type') and css.get('type') == 'text/css':
	
			if css.string and '@import' in css.string:
	
				text = css.string.replace('@import', '')
				text = text.replace('url', '')
				text = text.replace('(', '')
				text = text.replace(')', '')
				text = text.replace('"', '')
				text = text.replace(' ', '')
				
				text_splitted = text.split(';')
	
				for text_splitted_url in text_splitted:
					if text_splitted_url != '':
						try:
							text_splitted_css = urllib2.urlopen(text_splitted_url)
							text_splitted_css_content = text_splitted_css.read()
							
							if '@media only screen' in text_splitted_css_content or '@media (max-width' in text_splitted_css_content:
								print 'MOBILE WEB (@media / <style): ' + place_name + ' - ' + place_web
				
						except urllib2.HTTPError, e:
# 							print('HTTPError = ' + str(e.code) + place_web)
							continue
						except urllib2.URLError, e:
# 							print('URLError = ' + str(e.reason) + place_web)
							continue
						except httplib.HTTPException, e:
# 							print('HTTPException ' + place_web)
							continue
						except Exception:
							import traceback
# 							print('generic exception: ' + traceback.format_exc() + ' ' + place_web)							
							continue
	
# 	-------------	
# 	SEARCH FOR @MEDIA ONLY SCREEN IN CSS FILES DEFINED AS <link type='text/css' />				
# 	-------------	
	for link in soup.find_all('link'):
	
		if link.get('type') == 'text/css':
			css_url = link.get('href')

			# If css are saved as local urls
			if css_url and not css_url.startswith('http://') and not css_url.startswith('www.'):
				css_url = place_web + '/' + css_url
			
			try:
				css_web = urllib2.urlopen(css_url)
		
			except urllib2.HTTPError, e:
# 				print str(e) + ' - ' + place_web
				continue
			except urllib2.URLError, e:
# 				print str(e) + ' - ' + place_web
				continue
			except httplib.HTTPException, e:
# 				print str(e) + ' - ' + place_web
				continue
			except Exception:
# 				print 43534543
				continue
			
			css_text = css_web.read()
	
			if '@media only screen' in css_text: # or '@media (max-width' in css_text:
				print 'MOBILE WEB (@media / <link): ' + place_name + ' - ' + place_web
				break
		
		else:
			css_url = link.get('href')
			if css_url and css_url.endswith('.css'):
				
				# If css are saved as local urls
				if not css_url.startswith('http://') and not css_url.startswith('www.'):
					css_url = place_web + '/' + css_url
				
				try:
					css_web = urllib2.urlopen(css_url)
			
				except urllib2.HTTPError, e:
# 					print str(e) + ' - ' + place_web
					continue
				except urllib2.URLError, e:
# 					print str(e) + ' - ' + place_web
					continue
				except httplib.HTTPException, e:
# 					print str(e) + ' - ' + place_web
					continue
				except Exception:
# 					print 43534543
					continue
				
				css_text = css_web.read()
		
				if '@media only screen' in css_text:#  or '@media (max-width' in css_text:
					print 'MOBILE WEB (@media / <link): ' + place_name + ' - ' + place_web
					break
	
		

# if __name__ == "__main__":
#     check(sys.argv[1])