# 	-------------	
# 	SEARCH FOR @MEDIA ONLY SCREEN IN CSS FILES DEFINED AS <link type='text/css' />				
# 	-------------
def extract(soup, cur, place_id):

	found = False
	
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
	
			if '@media only screen' in css_text:
				print 'MOBILE WEB (@media / <link): ' + place_name + ' - ' + place_web
				cur.execute('UPDATE place SET has_mobile_web = 1 where id = %s', place_id)
				cur.commit()
				found = True
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
					cur.execute('UPDATE place SET has_mobile_web = 1 where id = %s', place_id)
					cur.commit()
					found = True
					break
		
		if found:
			break
			
	return found
