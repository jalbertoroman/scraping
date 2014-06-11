from bs4 import BeautifulSoup

# 	-------------	
# 	SEARCH FOR rel=alternate DEFINED IN HEAD AS <link rel=alternate />				
# 	-------------
def extract(soup):

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
					
	return possible_alternate