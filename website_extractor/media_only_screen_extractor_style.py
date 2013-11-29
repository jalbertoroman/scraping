
# 	-------------			
# 	SEARCH FOR @MEDIA ONLY SCREEN IN CSS FILES DEFINED IN <style type='text/css' />
# 	-------------	
def extract(soup, cur, place_id):

	found = False

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
								cur.execute('UPDATE place SET has_mobile_web = 1 where id = %s', place_id)
								cur.commit()
								found = True
								print 'MOBILE WEB (@media / <style): ' + place_name + ' - ' + place_web
								break
				
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
							
		if found:
			break
						
	return found
