<?php 
set_time_limit(0);
ignore_user_abort(true);
mb_internal_encoding("UTF-8"); 

$home_host = "localhost";
$remote_host ="54.215.180.86";
$db = "play";
$user = "postgres";
$pass = "admin";

$con = pg_connect("host=$home_host dbname=$db user=$user password=$pass") or die ("Could not connect to server\n"); 
$query = "INSERT INTO play_apps_index 
			(SELECT R.* FROM dblink('host=$remote_host dbname=$db user=$user password=$pass', 'SELECT app FROM play_apps_index') AS R(app text))
			EXCEPT
			(SELECT app FROM play_apps_index)";
			
$result = pg_query($con, $query);
pg_close($con);

?>