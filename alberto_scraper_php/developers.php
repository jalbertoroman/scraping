<?php //SCRAPPER COMPLETO
set_time_limit(0);//casi 3 horas 10000//36000 10 horas
ignore_user_abort(true);
header('Content-Type: text/html; charset=UTF-8'); 
date_default_timezone_set('America/Los_Angeles');
mb_internal_encoding("UTF-8"); 
gc_enable();

include_once('./phpQuery/phpQuery/phpQuery.php');

$host = "localhost";
$db = "play";
$user = "postgres";
$pass = "admin";

$limit = 1000;

$con = pg_connect("host=$host dbname=$db user=$user password=$pass") or die ("Could not connect to server\n"); 

$page_number = 0;
$developers_deleted = 0;

//coger los developers de la BD  
$done = false;
while (!$done){  
	
	$offset =  $page_number * $limit;
	echo $offset.PHP_EOL;
	$query = "SELECT developer_id FROM rest_api_developer order by developer_id ASC Limit '$limit' Offset '$offset' ";
	$results = pg_query($query); 
		
	if (pg_num_rows($results)<1) {
		$done = true;
	}
	
	$page_number++;


	while($row = pg_fetch_row($results))
	{                
		$developer_id = $row[0];
		$developer_id = urlencode($developer_id);

	    $url = sprintf("https://play.google.com/store/apps/developer?id=%s&start=0&num=100", $developer_id);
	    
/* 	    echo 'URL:   '.$url.PHP_EOL; */
		
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
			fwrite($f, 'curl fail: '.$developer_id.PHP_EOL);
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
	        
	        	echo 'Pillados change or wait for new IP'.PHP_EOL;
					            
	        } 
	        elseif (strlen($notfound) > 0) 
	        {
/* 	       		echo 'Not found'.PHP_EOL; */
	       		$developers_deleted++;
/*
	       		$sql = "DELETE FROM rest_api_developer WHERE developer_id = '$developer_id'";
				pg_query($con, $sql);   
*/
	        }
	        else 
	        {
	        
	        	$app = getApp($developer_id);
				//garbage collector
				phpQuery::unloadDocuments();
				$app = null;
				unset($app);
				gc_collect_cycles();
	            //echo "Mem usage is: ", memory_get_usage(), "\n";
	        }                   
	    }
	
		
						
	} 
}
echo 'Developers Deleted: '.$developers_deleted.PHP_EOL;

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

function getApp($developer_id)
{

	global $con;
	    
    try {
    	
        $page = \pq('#body-content');  
         
		$s=0;
        $recommendations = $page->find('.card.apps');
        if (!empty($recommendations)) {
            foreach ($recommendations as $recomendation) {
            	$recomendation = \pq($recomendation);
            	$recomendation = $recomendation->attr('data-docid');
            	//echo $recomendation.PHP_EOL;
        		//Introducimos App en la lista de Scraping
                $sql = "SELECT * FROM play_apps_index WHERE app = '$recomendation' LIMIT 1";
				if (pg_num_rows(pg_query($con,$sql)) < 1) 
				{  //New App: Introducing into the DB
					//echo "Debería introducir la app: '$related'".PHP_EOL;
					$sql = "INSERT INTO play_apps_index (app) VALUES ('$recomendation')";
					pg_query($con, $sql);
				}
        	
            }
        }
        
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