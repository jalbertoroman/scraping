'''

Created on Nov 26, 2013

@author: alberto

'''

# Import the relevant libraries
import psycopg2
import sys



POLYGON_TYPE = "CC"

#Conection to DB
try:
	conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
except:
	f.write('%s: %s \n' % ('Connection Failed', time.time()))

cur = conn.cursor()

cur.execute("Select id, name from polygon where type=%s order by (ST_Area(polygon)*POWER(0.3048,2)) desc", [POLYGON_TYPE])

for polygon in cur.fetchall():
	
	#Delete the old points
	cur.execute('DELETE FROM point WHERE polygon_id=%s', [polygon[0]])
	conn.commit()

	# 0.00225degrees ~ 250 meters buffer the area to get border points	
	#cur.execute("Select ST_Buffer(polygon,0.00225) from polygon where id=%s", [polygon[0]])
	cur.execute("Select polygon from polygon where id=%s", [polygon[0]])
	area = cur.fetchall()
	
	#Make grid each 707 meters: hexagon -> l= sqr(2)* r
	cur.execute("SELECT makegrid(%s, 707, 4326) from polygon", area)
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
		
		cur.execute("Insert into point (polygon_id, lat, lng, geom) VALUES (%s, %s, %s, ST_SetSRID(ST_MakePoint(%s,%s),4326))", (polygon[0], lat, lng, lng, lat))
		conn.commit()
		
		i += 1
		
# 		print "%s-%s: %s , %s" % (i, polygon[1], lat, lng)

	print "%s: %s" % (polygon[1], i)
	
	
if conn:
		conn.close()	
	

	
# visualize in google earth, console comand
# ogr2ogr -f "KML" points.kml PG:"host=85.86.85.120 user=postgres dbname=google_places password=admin" -sql "select geom from point"
# or
# ogr2ogr -f "KML" points.kml PG:"host=85.86.85.120 user=postgres dbname=google_places password=admin" "point" -s_srs EPSG:4326 -t_src EPSG:4326

