<?php //SCRAPPER COMPLETO
set_time_limit(0);//casi 3 horas 10000//36000 10 horas
ignore_user_abort(true);
header('Content-Type: text/html; charset=UTF-8'); 
date_default_timezone_set('America/Los_Angeles');
mb_internal_encoding("UTF-8"); 
gc_enable();

include_once('./phpQuery/phpQuery/phpQuery.php');

//$host = "50.18.210.164";
$host  = "82.130.205.182";
$host2 = "54.215.168.125";
$db = "play";
$user = "postgres";
$pass = "admin";

$limit = 1000;

$con  = pg_connect("host=$host dbname=$db user=$user password=$pass") or die ("Could not connect to server\n"); 
$con2 = pg_connect("host=$host2 dbname=$db user=$user password=$pass") or die ("Could not connect to server2\n"); 

$query = "SELECT app FROM play_apps_index";
$results = pg_query($con, $query); 

$i=0;	
while($row = pg_fetch_row($results))
{      
	$i++;          
	$app_id = $row[0];
	//Introducimos App en la lista de Scraping
    $sql = "SELECT * FROM play_apps_index WHERE app = '$app_id' LIMIT 1";
	
	if (pg_num_rows(pg_query($con2, $sql)) < 1) 
	{  //New App: Introducing into the DB
	  echo "Debería introducir la app: '$app_id'".PHP_EOL;
	  $sql = "INSERT INTO play_apps_index (app) VALUES ('$app_id')";
	  pg_query($con2, $sql);
	}
	echo 'Nº :: '.$i.PHP_EOL;
				
} 
pg_close($con);
pg_close($con2);


?>