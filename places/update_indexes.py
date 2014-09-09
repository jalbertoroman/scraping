import psycopg2

conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
cur = conn.cursor()
cur.execute('update chain_point SET idx=FALSE where scraped=FALSE')
conn.commit()
cur.close()
conn.close()
