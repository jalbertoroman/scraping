'''

Created on Nov 26, 2013

@author: alberto

'''

# Import the relevant libraries
import psycopg2
import sys


# CC Spain urban areas
# UA urban areas of the world
# P USA + Gipuzkoa
POLYGON_TYPE = 'P'


#Conection to DB
try:
	conn = psycopg2.connect('host=54.217.205.13 dbname=mapplas_postgis user=postgres password=Y0tsuba!')
except:
	print "Connection fail"

cur = conn.cursor()

#cur.execute("Select id, name from polygon where type=%s order by (ST_Area(polygon)*POWER(0.3048,2)) desc", [POLYGON_TYPE])
# USA
cur.execute("select id,name1 from entity_extractor_entities where id=40")
# cur.execute("Select id, name from polygon where type=%s and id!=40", (POLYGON_TYPE,))
#id=4 is las vegas
# cur.execute("SELECT id, name FROM polygon WHERE ID=4", )
for polygon in cur.fetchall():
# 	print polygon
	#Delete the old points
	cur.execute('DELETE FROM point WHERE polygon_id=%s', [polygon[0]])
	conn.commit()
	# 0.00225degrees ~ 250 meters buffer the area to get border points	
	#cur.execute("Select ST_Buffer(polygon,0.00225) from polygon where id=%s", [polygon[0]])
	print polygon[0]
	cur.execute("Select mpoly from entity_extractor_entities where id=%s", [polygon[0]])
	area = cur.fetchall()
	#Make grid each 707 meters: hexagon -> l= sqr(2)* r
	cur.execute("SELECT makegrid(%s, 70711, 4326) from entity_extractor_entities", area)
	grid = cur.fetchall()
# 	cur.execute('UPDATE grid SET id=%s, name=%s, geom=%s, type=%s WHERE id=%s', (polygon[0], polygon[1], grid[0], POLYGON_TYPE, polygon[0]))
# 	
#  	cur.execute("Insert into  grid (id, name, geom, type) SELECT %s, %s, %s, %s WHERE NOT EXISTS (SELECT 1 FROM grid WHERE id=%s)", (polygon[0], polygon[1], grid[0], POLYGON_TYPE, polygon[0]))
#  	conn.commit()
# 		
# 	cur.execute("select st_x(geom) as x, st_y(geom) as y from (select (st_dump(mpt.geom)).geom from grid mpt where id=%s) as mpt;", [polygon[0]])
	
	cur.execute("select st_x(geom) as x, st_y(geom) as y from (select (st_dump(%s)).geom from (select %s) mpt) as mpt;", (grid[0], grid[0]))
	i=0
	for item in cur.fetchall():
	
		lat = item[1]
		lng = item[0]
		print "inserting"
		cur.execute("Insert into point (polygon_id, lat, lng, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s,%s),4326))", (polygon[0], lat, lng, lng, lat))
		conn.commit()
		i += 1
		
# 		print "%s-%s: %s , %s" % (i, polygon[1], lat, lng)

# 	print "%s: %s" % (polygon[1], i)
	
	
if conn:
		conn.close()	
	

	
# visualize in google earth, console comand
# ogr2ogr -f "KML" points.kml PG:"host=85.86.85.120 user=postgres dbname=google_places password=admin" -sql "select geom from point"
#
# ogr2ogr -f "KML" spain.kml PG:"host=85.86.85.120 user=postgres dbname=google_places password=admin" -sql "select * from polygon where type = 'S'"
#
# ogr2ogr -f "KML" points.kml PG:"host=85.86.85.120 user=postgres dbname=google_places password=admin" "point" -s_srs EPSG:4326 -t_src EPSG:4326
#
#
