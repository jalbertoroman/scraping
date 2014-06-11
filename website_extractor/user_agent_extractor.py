from bs4 import BeautifulSoup

# 	-------------	
# 	SEARCH FOR navigator.userAgent AND android IN JAVASCRIPT SCRIPTS <script type='text/javascript' />
# 	-------------	
def extract(soup, cursor, place_id):

	found = False

	for script in soup.find_all('script'):
	
		if script.text and 'navigator.userAgent' in script.text and 'android' in script.text:
			print 'USER AGENT (javascript): ' + place_name + ' - ' + place_web
			cur.execute('UPDATE place SET has_mobile_web = 1 where id = %s', place_id)
			cur.commit()
			found = True
			break
			
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
					cur.execute('UPDATE place SET has_mobile_web = 1 where id = %s', place_id)
					cur.commit()
					found = True
					break
					
	return found