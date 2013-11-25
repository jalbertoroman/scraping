from xml.dom import minidom


xmldoc = minidom.parse('/home/alberto/scraping/data/website_nodes.xml')

nodes = xmldoc.getElementsByTagName('node') 
print len(nodes)

for node in nodes:
	print(node.attributes['lat'].value)
	print(node.attributes['lon'].value)	
	
	tags = node.getElementsByTagName('tag')
	for tag in tags:
		if tag.attributes['k'].value == 'name':
			print(tag.attributes['v'].value)
		if tag.attributes['k'].value == 'website':
			print(tag.attributes['v'].value)