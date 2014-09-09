import psycopg2
import csv

conn = psycopg2.connect('host=54.217.205.13 dbname=mapplas_postgis user=postgres password=Y0tsuba!')
cur = conn.cursor()

chain_names_file = open('chains.csv')
chain_names_reader = csv.reader(chain_names_file)
chain_names = []
i=0
for chain in chain_names_reader:
    if i == 198:
        break
    chain_names.append(chain[0])
#     cur.execute("insert into chains(name) values (%s)" , (chain[0],))
#     conn.commit()
    i+=1
    
cur.execute("select id,name,lat,lng from place where place_polygon_id<125 or place_polygon_id is NULL")
# cur.execute("SELECT id,name,lat,lng from place where st_intersects((select polygon from polygon where id=1),st_setsrid(st_makepoint(lng,lat),4326))" , (chain_names,))

places = cur.fetchall()

for place in places:
    cur.execute("select id from entity_extractor_entities where st_intersects(mpoly,st_setsrid(st_makepoint(%s,%s),4326)) and id<125 and region_type_id='CC'", (place[3],place[2],))
    parent_id = cur.fetchone()
    if parent_id is None:
        cur.execute("select id from entity_extractor_entities where st_intersects(mpoly,st_setsrid(st_makepoint(%s,%s),4326)) and id<125 and region_type_id='P'", (place[3],place[2],))
        parent_id = cur.fetchone()
    id = place[0]
    if place[1] in chain_names:
        cur.execute("select id from chains where name=%s" , (place[1],))
        chain_id = cur.fetchone()
        cur.execute("update place set (is_chain,chain_id,place_polygon_id)=(TRUE,%s,%s) where id=%s" , (chain_id,parent_id,id,))
    else:
        cur.execute("update place set place_polygon_id=%s where id=%s" , (parent_id,id,))
    conn.commit()
