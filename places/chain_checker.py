import sys,os,logging,csv
import psycopg2


def open_log(logger_name, filename, level):
    try:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        fh = logging.FileHandler(filename)
        fh.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger
    except:
        raise Exception("Error opening log file!")

def log(string, log_dict, logger, level):
    #print "[ %s ]%s" % (datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f"), string)
    log_dict[logger][level](string)

chains_log_file = open_log("chaincheckerLogger", "logs/chainchecker_%s.log" % os.getpid(), "DEBUG")
log_dict = {
    'places_logger' : {
        'debug' : chains_log_file.debug,
        'critical' : chains_log_file.critical,
        'info' : chains_log_file.info
    }
}

done = False

# Conection to DB
try:
    conn = psycopg2.connect('host=localhost dbname=google_places user=postgres password=admin')
except:
    log('Connection Failed', log_dict, 'error_logger','critical')
    
cur = conn.cursor()

chain_names_file =  open('chainnames.csv')
chain_names_reader = csv.reader(chain_names_file)
for chain in chain_names_reader:
    cur.execute("select name,type_id from chain c inner join chain_type on id=chain_id where chain_name=%s group by name,type_id order by count(*) desc limit 1" , (chain,))
    highest_chain = cur.fetchone()
    cur.execute("select name,type_id from chain c inner join chain_type on id=chain_id where chain_name=%s and (type_id!=%s or name!=%s) group by name,type_id" , (chain,highest_chain[1],highest_chain[0],))
    chain_places = cur.fetchall()
    for check_chain in chain_places:
        if check_chain[1] != highest_chain[1]:
            cur.execute("delete from chain where id in (select id from chain c inner join chain_type on id=chain_id where chain_name=%s and type_id=%s and name=%s)" , (chain,check_chain[1],check_chain[0],))
        elif highest_chain[0] not in check_chain[0]:
            cur.execute("delete from chain where id in (select id from chain c inner join chain_type on id=chain_id where chain_name=%s and type_id=%s and name=%s)" , (chain,check_chain[1],check_chain[0],))
    

