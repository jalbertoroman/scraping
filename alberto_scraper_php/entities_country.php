<?php //SCRAPPER COMPLETO
set_time_limit(0);//casi 3 horas 10000//36000 10 horas
ignore_user_abort(true);
header('Content-Type: text/html; charset=UTF-8'); 
date_default_timezone_set('America/Los_Angeles');
mb_internal_encoding("UTF-8"); 
gc_enable();

include_once('./phpQuery/phpQuery/phpQuery.php');

//$host = "50.18.210.164";
$host = "54.215.168.125";
$db = "play";
$user = "postgres";
$pass = "admin";

$limit = 1000;
$language = "en";
$language_code = "en_US";
// change torr nodes if are used

$con = pg_connect("host=$host dbname=$db user=$user password=$pass") or die ("Could not connect to server\n"); 



	
	//$query = "SELECT name FROM entities group by name";
	$query = "SELECT name2 FROM entities group by name2";
	$results = pg_query($query); 
		
	while($row = pg_fetch_row($results))
	{                
		$entitie = $row[0];
		$entitie = urlencode($entitie);
		
		for ($j = 0; $j <= 2; $j++) {
			
		    $url = sprintf("https://play.google.com/store/search?q=%s&c=apps&price=%s&hl=%s", $entitie, $j, $language);
		    
		    echo 'URL:   '.$url.PHP_EOL;
			
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
		       		echo 'Not found'.PHP_EOL;
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
		    
		    //usleep(rand(2000000,4000000));
		
		}
						
	} 


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
	global $language;
	
	switch ($language) {
        case "en":
        	$developer_web_text = " Visit Developer's Website ";
        	$developer_mail_text = " Email Developer ";	
        	$developer_privacy_text = " Privacy Policy ";
        	//sudo locale-gen es_ES.utf8
			setlocale(LC_ALL, "en_US.UTF-8"); 
			$formato = "%B %d, %Y";	
			$storefront_id = 1002;
			$whatsnew_text = " What's New ";	        
			break;
        case "es":
        	$developer_web_text = "Acceder al sitio web del desarrollador";	
        	$developer_mail_text = "Correo del desarrollador";	
        	$developer_privacy_text = "Política de privacidad";
        	setlocale(LC_ALL,"es_ES.utf8");
			$formato = "%d de %B de %Y";		
			$storefront_id = 1001;
			$whatsnew_text = "Novedades";	
        	break;      
    }
    
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
					echo "Debería introducir la app: '$recomendation'".PHP_EOL;
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