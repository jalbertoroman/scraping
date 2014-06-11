<?php //SCRAPPER COMPLETO
ignore_user_abort(true);
mb_internal_encoding("UTF-8"); 
gc_enable();

include_once('/var/www/play/phpQuery/phpQuery/phpQuery.php');

echo 'Empieza: '.date('l jS \of F Y h:i:s A').PHP_EOL;

$host = "localhost";
$db = "play";
$user = "postgres";
$pass = "admin";

$num_apps_added = 0;

$con = pg_connect("host=$host dbname=$db user=$user password=$pass") or die ("Could not connect to server\n"); 	
	
$urls[] = "https://play.google.com/store/apps/collection/topselling_new_free";
$urls[] = "https://play.google.com/store/apps/collection/topselling_free";
$urls[] = "https://play.google.com/store/apps/collection/topselling_new_paid";
$urls[] = "https://play.google.com/store/apps/collection/topselling_paid";
$urls[] = "https://play.google.com/store/apps/collection/topgrossing";

$query = "SELECT genre_id FROM rest_api_genre where parent_id !='none'";
$results = pg_query($query); 

while($row = pg_fetch_row($results))
{   
             
$genre = $row[0];

$urls[] = sprintf("https://play.google.com/store/apps/category/%s/collection/topselling_new_free", $genre);
$urls[] = sprintf("https://play.google.com/store/apps/category/%s/collection/topselling_free", $genre);
$urls[] = sprintf("https://play.google.com/store/apps/category/%s/collection/topselling_new_paid", $genre);
$urls[] = sprintf("https://play.google.com/store/apps/category/%s/collection/topselling_paid", $genre);
$urls[] = sprintf("https://play.google.com/store/apps/category/%s/collection/topgrossing", $genre);

}

foreach ($urls as $url) {

	for ($a=1; $a<10; $a++){
		$urls[] = $url."?start=".$a*60;
	}

}

foreach ($urls as $url) {

/* 	echo 'URL:   '.$url.PHP_EOL; */

	$i=0; 
	$response = false;
	while (!$response && $i<3) {
	    $response = getpage($url);
	    $i++;
	}
	
	if(!$response)
	{
		//response False try again the next time ...        	
	   	$f = fopen('elog.txt','a+');
		fwrite($f, 'curl fail: '.$url.PHP_EOL);
		fclose($f);
	}
	else 
	{
	  //response, check the response...          
	           
	  $automates = (strstr($response,"but your computer or network may be sending automated queries"));
	  $unusual = (strstr($response,"www.google.com/sorry/?continue"));
	  $notfound = (strstr($response,"the requested URL was not found on this server"));
	              
	    if (strlen($automates) > 0 || strlen($unusual) > 0 ) 
	    {
	    
	    	echo 'Change or wait for new IP'.PHP_EOL;
				            
	    } 
	    elseif (strlen($notfound) > 0) 
	    {
/* 	   		echo 'Not found: '.$url.PHP_EOL; */
	    }
	    else 
	    {
	    
	    	$app = getApp();
			//garbage collector
			phpQuery::unloadDocuments();
			$app = null;
			unset($app);
			gc_collect_cycles();
	        //echo "Mem usage is: ", memory_get_usage(), "\n";
	    }                   
	}
						
} 
echo 'New Apps: '.$num_apps_added.PHP_EOL;
echo 'Acaba: '.date('l jS \of F Y h:i:s A').PHP_EOL;

function getpage($url){

	$ch = curl_init();      
        
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
    curl_setopt($ch, CURLOPT_USERAGENT,'Mozilla/5.0 (Windows NT 5.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1');
    curl_setopt($ch, CURLOPT_ENCODING, 'gzip,deflate');		
    //curl_setopt($ch, CURLOPT_PROXY, '127.0.0.1:8118');
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);

    $response = curl_exec($ch);
    
    //print_r($response);
    curl_close($ch);
      
    \phpQuery::newDocument($response);
    
    return $response;
    	
}

function getApp()
{

	global $con;
	global $num_apps_added;
    try {
    	
        $page = \pq('#body-content');  
         
		$s=0;
        $recommendations = $page->find('.card');
        if (!empty($recommendations)) {
            foreach ($recommendations as $recomendation) {
            	$recomendation = \pq($recomendation);
            	$recomendation = $recomendation->attr('data-docid');
            	$s++;
        		//Introducimos App en la lista de Scraping
                $sql = "SELECT * FROM play_apps_index WHERE app = '$recomendation' LIMIT 1";
				if (pg_num_rows(pg_query($con,$sql)) < 1) 
				{  //New App: Introducing into the DB
/* 					echo "Debería introducir la app: '$recomendation'".PHP_EOL; */
					$sql = "INSERT INTO play_apps_index (app) VALUES ('$recomendation')";
					pg_query($con, $sql);
					$num_apps_added++;
				}
        	
            }
        }
/*         echo $s.PHP_EOL; */
        $app=array('estado'=> 'OK');        
        
        //print_r($app);
        return $app;  
                
	} //end try
	catch (Exception $e) {
		return $app;
	} //end catch
    
}
			       	
pg_close($con);

?>