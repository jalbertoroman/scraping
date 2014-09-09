import psycopg2

conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
cur = conn.cursor()

cur.execute("select id from place where place_polygon_id is null")
null_places = cur.fetchall()

for null_place in null_places:
    cur.execute("select place_polygon_id,is_chain,chain_id from place_new where id=%s" , (null_place,))
    info = cur.fetchone()
    cur.execute("update place set (place_polygon_id,is_chain,chain_id)=(%s,%s,%s)" , (info[0],info[1],info[2]))
    conn.commit()