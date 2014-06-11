import urllib2
import urllib
import sys
import httplib
import md5
import StringIO

from xml.dom import minidom
from bs4 import BeautifulSoup


# Start script
xmldoc = minidom.parse('/home/alberto/scraping/data/website_nodes.xml')

nodes = xmldoc.getElementsByTagName('node') 

for node in nodes:

# 	print(node.attributes['lat'].value)
# 	print(node.attributes['lon'].value)	
	
	tags = node.getElementsByTagName('tag')
	for tag in tags:
	
# 		if tag.attributes['k'].value == 'name':
# 			print(tag.attributes['v'].value)

		if tag.attributes['k'].value == 'website':
# 			print(tag.attributes['v'].value)

			url = tag.attributes['v'].value
			
			if not url.startswith('http'):
				url = 'http://' + url

			try:
				sock = urllib2.urlopen(url)
				soup = BeautifulSoup(sock)
				
# 				Define boolean to compare ALL alternate links of a url
				possible_alternate = False
				
				for link in soup.find_all('link'):
								
# 					SEARCH FOR @MEDIA ONLY SCREEN IN WEB CSS FILES					
					if link.get('type') and link.get('type') == 'text/css':
						
						css_url = link.get('href')
						
						if css_url.endswith('.css'):
						
							try:
								css_web = urllib2.urlopen(css_url)
							
							except urllib2.HTTPError, e:
								pass
							except urllib2.URLError, e:
								pass
							except httplib.HTTPException, e:
								pass
							except Exception:
								pass
							
							css_text = css_web.read()
			
							if '@media only screen' in css_text:
								print 'MOBILE WEB (@media): ' + url
								break
								
# 					SEARCH FOR rel=alternate LINKS IN WEB HEAD
					if link.get('rel')[0] == 'alternate':

						if link.get('hreflang') or link.get('type') or link.get('data-kss-base-url'):
							break
							
 						else:
 							if link.get('media'): # FACEBOOK and old mobile web designing.   and link.get('media') != 'handheld' or link.get('media').contains('only screen and')
 								if link.get('media') == 'handheld' or link.get('media').contains('only screen and'):
									possible_alternate = True
									
							else:			
								href = link.get('href')
								if not href.endswith('.css'):
									possible_alternate = True
								
				if possible_alternate:
					print 'MOBILE WEB (rel=alternate): ' + url + ' _ ' + href
					break
							
			except urllib2.HTTPError, e:
				pass
# 				print('HTTPError = ' + str(e.code) + url)
			except urllib2.URLError, e:
				pass
# 				print('URLError = ' + str(e.reason) + url)
			except httplib.HTTPException, e:
				pass
# 				print('HTTPException ' + url)
			except Exception:
				pass
# 			    import traceback
# 			    print('generic exception: ' + traceback.format_exc() + ' ' + url)
			
 
# 			# Check URL
# 			values = {'name' : 'Michael Cook',
# 			          'location' : 'London',
# 			          'language' : 'Python' }
# 			          
# 			data = urllib.urlencode(values)
# 			
# # 			Normal browser
# 			user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.45 Safari/535.19'
# 			headers = { 'User-Agent' : user_agent }
# 			req = urllib2.Request(url)
# 			req.addheaders = headers
# 			
# 			try:
# 				response = urllib2.urlopen(req)
# 				the_page = response.read()
# 				
# # 				Mobile
# 				user_agent_mobile = 'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76K) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19'
# 				headers_mobile = { 'User-Agent' : user_agent_mobile }
# 				req_mobile = urllib2.Request(url)
# 				req_mobile.addheaders = headers_mobile
# 				response_mobile = urllib2.urlopen(req_mobile)
# 				the_page_mobile = response_mobile.read()
# 				
# 				if md5.md5(the_page).hexdigest() != md5.md5(the_page_mobile).hexdigest():
# 					print(url)
# 					print 'different'
					
# 					Vary header
# 					vary = response.info().getheader('Vary')
# 					vary_mobile = response_mobile.info().getheader('Vary')
# 					print vary
# 					print vary_mobile

# 			except urllib2.HTTPError, e:
# 			    print('HTTPError = ' + str(e.code))
# 			except urllib2.URLError, e:
# 			    print('URLError = ' + str(e.reason))
# 			except httplib.HTTPException, e:
# 			    print('HTTPException')
# 			except Exception:
# 			    import traceback
# 			    print('generic exception: ' + traceback.format_exc())
			


# if __name__ == "__main__":
#     check(sys.argv[1])