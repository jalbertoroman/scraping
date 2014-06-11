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
$language = "es";
$language_code = "es_ES";

$con = pg_connect("host=$host dbname=$db user=$user password=$pass") or die ("Could not connect to server\n"); 

$upsert = 0;

//coger los app_id de la BD  
$done = false;
while (!$done){  

	$query = "BEGIN";
	$results = pg_query($query);
	
	//$query = "SELECT app_id_id FROM rest_api_appprice where price ~ '^[$]' and storefront_id_id = 1001";
    //$query = "SELECT app FROM play_apps_index EXCEPT SELECT app_id FROM rest_api_application";         
	//$query = "SELECT app_id_id FROM rest_api_appprice where storefront_id_id = 1001 and price != 'Gratis' except SELECT app FROM play_apps_index where index = TRUE limit '$limit'";

	$query = "SELECT app FROM play_apps_index where index = FALSE order by app ASC LIMIT '$limit' for Update";
	$results = pg_query($query); 
	
	if (pg_num_rows($results)<1) {
		$done = true;
	}
		
	//$query = "UPDATE play_apps_index SET index = TRUE WHERE app in (SELECT app_id_id FROM rest_api_appprice where storefront_id_id = 1001 and price != 'Gratis' except SELECT app FROM play_apps_index where index = TRUE limit '$limit')";
	
	$query = "UPDATE play_apps_index SET index = TRUE WHERE app in (SELECT app FROM play_apps_index where index = FALSE order by app ASC LIMIT '$limit')";
	pg_query($query);
	
	$query = "COMMIT";
	pg_query($query);

 	
	// free ram memory launch script from root...
	shell_exec('sudo sync && sudo echo 3 > /proc/sys/vm/drop_caches');

	while($row = pg_fetch_row($results))
	{                
		$app_id = $row[0];
				
	    $url = sprintf("https://play.google.com/store/apps/details?hl=%s&id=%s",$language, $app_id);
	    //echo 'URL:   '.$url.PHP_EOL;
		
		
		//$start = microtime(true); 
	    $i=0; 
	    $response = false;
	    while (!$response && $i<3) {
	        $response = getpage($url);
	        $i++;
	    }
		//echo 'GetPage'.$i.': '.(microtime(true) - $start).' '.$app_id.PHP_EOL;

	    if(!$response)
	    {
	    	//response False try again the next time ...        	
	       	$f = fopen('elog.txt','a+');
			fwrite($f, 'curl fail: '.$app_id.PHP_EOL);
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
	        
	        // Pillados change or wait for new IP
				$ipOld = miIP();	
				
				echo "Mi ipOld: ".$ipOld.PHP_EOL;
				
				$block = true;
			
				while($block){		
					sleep(10);	
					echo "esperando..........".PHP_EOL;		
					$ipNew = miIP();						
					$block = ($ipOld == $ipNew ? true : false);                               
				}
	
	            
	        } 
	        elseif (strlen($notfound) > 0) 
	        {
	        // Not Found Delete App from the DB of Scrapping Apps
/* 	        	echo 'App not found, deleting app:  '.$app_id.PHP_EOL; */
	        	$sql = "DELETE FROM play_apps_index WHERE app = '$app_id'";
				pg_query($con, $sql);    
				
				$sql = "DELETE FROM rest_api_application WHERE app_id = '$app_id'";
				pg_query($con, $sql);   
	 
	        }
	        else 
	        {
	        	// Ok, call getApp and insert related apps
				//$start = microtime(true); 
	            $app = getApp($app_id);
				//echo 'GetApp: '.(microtime(true) - $start).' '.$app_id.PHP_EOL;
				
	            if ($app['estado'] != 'OK')
	            {
	            	//Missing Data... The url return an empty page.
		            echo 'Missing Data: '.$app['estado'].'  '.$app_id.PHP_EOL;
		            $f = fopen('elog.txt','a+');
					fwrite($f, 'Missing Data: '.$app_id.PHP_EOL);
					fclose($f);
					/*
					$sql = "DELETE FROM play_apps_index WHERE app = '$app_id'";
					pg_query($con, $sql) ;   
					
					$sql = "DELETE FROM rest_api_application WHERE app_id = '$app_id'";
					pg_query($con, $sql);          
					*/
	            }
	            else 
	            { 
	            	// Insert or Update the app...
	            	$upsert++;
/* 					echo 'Nº :: '.$upsert.' App:: '.$app_id.PHP_EOL; */
					//$start = microtime(true); 
	           		upsert($app);
	           		//echo 'Upsert: '.(microtime(true) - $start).' '.$app_id.PHP_EOL;
	           		
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

function upsert($app) 
{
	global $con;
	global $language_code;
	
	//$query = pg_query($con, 'Begin;');
	
	$query = "UPDATE rest_api_application SET 
		version = '".$app['version']."' ,		
		version_updated = '".$app['version_updated']."',			
		file_size = '".$app['size']."',		
		rating = '".$app['rating']."',		
		votes = '".$app['votes']."',			
		privacy = '".$app['deveoper_privacy']."',
		updated = ".time().",
		developer_web = '".$app['developer_web']."',
		developer_email = '".$app['developer_mail']."' WHERE app_id = '".$app['app_id']."'  ";

	pg_query($con, $query);

	$query = "INSERT INTO rest_api_application (
		app_id,		
		version,			
		version_updated,			
		file_size,			
		rating,			
		votes,			
		privacy,	
		created,
		updated,			
		developer_web,			
		developer_email) SELECT
		'".$app['app_id']."',
		'".$app['version']."',
		'".$app['version_updated']."',
		'".$app['size']."',
		'".$app['rating']."',
		'".$app['votes']."',
		'".$app['deveoper_privacy']."',
		".time().",
		".time().",
		'".$app['developer_web']."',
		'".$app['developer_mail']."' WHERE NOT EXISTS (SELECT 1 FROM rest_api_application WHERE app_id = '".$app['app_id']."')";			
						
	$res = pg_query($con, $query);
	
	if (!$res) {
		//$query = pg_query($con, 'rollback;');
		return $res;
	}
	
	$query = "UPDATE rest_api_appdetails SET 
		title = '".$app['app_name']."',
		description = '".$app['app_description']."', 
		description_key = '".$app['app_description_key']."', 
		icon_url = '".$app['icon_url']."',
		phone_screenshots = '".$app['screenshots']."',
		video = '".$app['video']."',
		video_img = '".$app['video_img']."',
		release_notes = '".$app['whatsnew']."',
		related_apps = '".$app['related']."',
		more_from_dev_apps = '".$app['more_from_developer']."',
		content_rating = '".$app['contentRating']."',	
		operating_system = '".$app['operatingSystems']."',
		updated = ".time()."  WHERE (app_id = '".$app['app_id']."' AND language_code = '".$language_code."') ";
	
	@pg_query($con, $query);

	$query = "INSERT INTO rest_api_appdetails (
		app_id,
		language_code,
		title,
		description,
		description_key,
		icon_url,
		phone_screenshots,
		video,
		video_img,
		release_notes,
		related_apps,
		more_from_dev_apps,
		content_rating,
		operating_system,
		created,
		updated) SELECT
		'".$app['app_id']."',
		'".$language_code."',
		'".$app['app_name']."',
		'".$app['app_description']."',
		'".$app['app_description_key']."', 
		'".$app['icon_url']."',
		'".$app['screenshots']."',
		'".$app['video']."',
		'".$app['video_img']."',
		'".$app['whatsnew']."',
		'".$app['related']."',
		'".$app['more_from_developer']."',
		'".$app['contentRating']."',		
		'".$app['operatingSystems']."',
		".time().",
		".time()." WHERE NOT EXISTS (SELECT 1 FROM rest_api_appdetails WHERE (app_id = '".$app['app_id']."' AND language_code = '".$language_code."') )";
					
	@pg_query($con, $query);
	
	$query = "UPDATE rest_api_developer SET 
		name = '".$app['developer_name']."' WHERE developer_id = '".$app['developer_id']."' ";
	
	pg_query($con, $query);

	$query = "INSERT INTO rest_api_developer (
			developer_id,			
			name) SELECT
			'".$app['developer_id']."',
			'".$app['developer_name']."' WHERE NOT EXISTS (SELECT 1 FROM rest_api_developer WHERE developer_id = '".$app['developer_id']."' ) ";
				
	pg_query($con, $query);
		
	$query = "UPDATE rest_api_developerapp SET app_id_id = '".$app['app_id']."' , developer_id_id = '".$app['developer_id']."' WHERE  app_id_id = '".$app['app_id']."' ";							
	pg_query($con, $query);
	
	$query = "INSERT INTO rest_api_developerapp (app_id_id , developer_id_id) 
				SELECT '".$app['app_id']."','".$app['developer_id']."' WHERE NOT EXISTS (SELECT 1 FROM rest_api_developerapp WHERE app_id_id = '".$app['app_id']."') ";
	pg_query($con, $query);

	// Alerta New Genre.
	$query = "SELECT * FROM rest_api_genre WHERE genre_id = '".$app['genre']."' ";
	$result = pg_query($con, $query) ;
	
	if (pg_num_rows($result) < 1) 
	{ 
		$f = fopen('elog.txt','a+');
		fwrite($f, 'ALERT!!!  CATEGORY MISING : '.$app['genre'].' '.$app['app_id'].'---------------------------------------------------------------------'.PHP_EOL);
		fclose($f);
		//exit("ALERT!!!  CATEGORY MISING : ".$app['genre']."   ".$app['app_id']."  ");
	}
		
		
		
	$query = "UPDATE rest_api_genreapp SET genre_id_id = '".$app['genre']."', app_id_id = '".$app['app_id']."' WHERE  app_id_id = '".$app['app_id']."' ";							
	pg_query($con, $query);	
		
	$query = "INSERT INTO rest_api_genreapp (genre_id_id , app_id_id) 
				SELECT '".$app['genre']."','".$app['app_id']."' WHERE NOT EXISTS (SELECT 1 FROM rest_api_genreapp WHERE app_id_id = '".$app['app_id']."')  ";							
	pg_query($con, $query);
	
	$query = "UPDATE rest_api_appprice SET app_id_id = '".$app['app_id']."', storefront_id_id = '".$app['storefront_id']."', price = '".$app['price']."' 
				WHERE  app_id_id = '".$app['app_id']."' AND storefront_id_id = '".$app['storefront_id']."'  ";
	pg_query($con, $query);	
	
	$query = "INSERT INTO rest_api_appprice (app_id_id,storefront_id_id,price) 
				SELECT '".$app['app_id']."','".$app['storefront_id']."','".$app['price']."'
				WHERE NOT EXISTS (SELECT 1 FROM rest_api_appprice WHERE (app_id_id = '".$app['app_id']."') AND storefront_id_id = '".$app['storefront_id']."')  ";
	pg_query($con, $query);

	$query = "select range_id from rest_api_range where apps_range = '".$app['installs']."' LIMIT 1";
	$result = pg_query($con, $query);
	
	$range_id_id = pg_fetch_row($result);
	if (pg_num_rows($result) < 1) 
	{ 
		$query = "INSERT INTO rest_api_range (apps_range) VALUES ('".$app['installs']."')";							
		pg_query($con, $query) ;
		
		$query = "select range_id from rest_api_range where apps_range = '".$app['installs']."' LIMIT 1";
		$result = pg_query($con, $query) ;
	
		$range_id_id = pg_fetch_row($result);
		
		$query = "UPDATE rest_api_rangeapp SET range_id_id = '".$range_id_id[0]."', app_id_id = '".$app['app_id']."' WHERE  app_id_id = '".$app['app_id']."' ";							
		pg_query($con, $query);	
		
		$query = "INSERT INTO rest_api_rangeapp (range_id_id, app_id_id) 
					SELECT '".$range_id_id[0]."','".$app['app_id']."' WHERE NOT EXISTS (SELECT 1 FROM rest_api_rangeapp WHERE app_id_id = '".$app['app_id']."') ";
		pg_query($con, $query);
				
	} else 
	{
		$query = "UPDATE rest_api_rangeapp SET range_id_id = '".$range_id_id[0]."', app_id_id = '".$app['app_id']."' WHERE  app_id_id = '".$app['app_id']."' ";							
		pg_query($con, $query);	
		
		$query = "INSERT INTO rest_api_rangeapp (range_id_id, app_id_id) 
					SELECT '".$range_id_id[0]."','".$app['app_id']."' WHERE NOT EXISTS (SELECT 1 FROM rest_api_rangeapp WHERE app_id_id = '".$app['app_id']."') ";
		pg_query($con, $query);
	}
	
	// Flag scrapped App
	$query = "UPDATE play_apps_index SET scraped = TRUE WHERE app = '".$app['app_id']."' ";
	pg_query($con, $query); 
	
	//$query = pg_query($con, 'commit;');

	
}

function  miIP()
{
    $ch = curl_init();

    // Set the website you would like to scrape
    curl_setopt($ch, CURLOPT_URL, "http://www.fixitts.com/whatismyip.php");
    curl_setopt($ch, CURLOPT_USERAGENT, '');
    curl_setopt($ch, CURLOPT_REFERER, '');
    curl_setopt($ch, CURLOPT_PROXY, '127.0.0.1:8118');
    
    // Set cURL to return the results into a PHP variable
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    
    // This executes the cURL request and places the results into a variable.
    $curlResults= curl_exec($ch);
    curl_close($ch);
    return $curlResults;
    
}
			

function getApp($app_id)
{

$total = microtime(true); 

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
         
        $app_name = trim($page->find('.document-title')->text());        
        if ($app_name == '') {
        	$app=array('estado'=> 'EmptyName');
            return $app;	                
        }     
        
        $price =  trim($page->find('.price span meta[itemprop="price"]')->attr('content'));      


		$s=0;
        $recommendations = $page->find('.rec-cluster');
        if (!empty($recommendations)) {
            foreach ($recommendations as $recomendation) {
            	$recomendation = \pq($recomendation);
            	$type = ( $s==0  ? 'related' : 'more_from_developer');
            	$s++;
            	$recomendation = $recomendation->find('.card.apps'); 
            	$similar = '';
            	foreach ($recomendation as $related) {
            		$related = \pq($related);
					$related = $related->attr('data-docid');  
					$similar[].=$related;
            		//Introducimos App en la lista de Scraping
                    $sql = "SELECT * FROM play_apps_index WHERE app = '$related' LIMIT 1";
					if (pg_num_rows(pg_query($sql)) < 1) 
					{  //New App: Introducing into the DB
						//echo "Debería introducir la app: '$related'".PHP_EOL;
						$sql = "INSERT INTO play_apps_index (app) VALUES ('$related')";
						pg_query($con, $sql);
					}
            	}
            	$similars[$type]= $similar;
            }
        }
        
        $related = '';
		if (!empty($similars['related'])) {
        	$related = implode(',', $similars['related']);
        }

        $more_from_developer = '';
		if (!empty($similars['more_from_developer'])) {
        	$more_from_developer = implode(',', $similars['more_from_developer']);
        }

        $icon_url = $page->find('.cover-container img')->attr('src');

        $app_description = trim($page->find('.show-more-content.text-body')->html());
        $app_description_key = md5($app_description);
        $app_description = br2nl($app_description);
        $app_description= strip_tags($app_description, '');
        
        

		$version_updated = trim($page->find('.content[itemprop="datePublished"]')->text());  
		$fecha = strptime($version_updated, $formato);					
		$version_updated = ($fecha['tm_mon']+1).'/'.$fecha['tm_mday'].'/'.($fecha['tm_year']+1900);		
		$version_updated = strtotime($version_updated);
		if ($version_updated == '') {
        	$app=array('estado'=> 'EmptyDatePublished');
            return $app;	                
        }     
		
		$size = trim($page->find('.content[itemprop="fileSize"]')->text()); 
       
        $installs = trim($page->find('.content[itemprop="numDownloads"]')->text());
        $installs = str_replace(',' , '', $installs);
        $installs = str_replace('.' , '', $installs);
        if (!isset($installs)) {
	    	$installs = 'Unset';	                    
        }  
 
        $version =  trim($page->find('.content[itemprop="softwareVersion"]')->text()); 

        $operatingSystems = trim($page->find('.content[itemprop="operatingSystems"]')->text()); 

		$contentRating = trim($page->find('.content[itemprop="contentRating"]')->text()); 

        $genre = trim($page->find('.category')->attr('href'));
	    if (isset($genre)) {
	    	$genre = str_replace('/store/apps/category/', '', $genre);
	    }

        $votes = $page->find('.score-container meta[itemprop="ratingCount"]')->attr('content');
        $votes = str_replace(',', '', $votes);
        $votes = str_replace('.', '', $votes);
        $votes = intval($votes);       

        $developer_name = trim($page->find('.info-container div a[itemprop="name"]')->text());

        $developer_id = trim($page->find('.info-container div meta[itemprop="url"]')->attr('content'));
        if (strlen($developer_id)>0) {
           $developer_id = urldecode(str_replace('/store/apps/developer?id=', '', $developer_id));
        }        

        $whatsnew = trim($page->find('.details-section.whatsnew')->html());
        $whatsnew = str_replace($whatsnew_text, '', $whatsnew);
        $whatsnew = strip_tags($whatsnew, '');
        $whatsnew = br2nl($whatsnew);

		$rating = 0.0000;
        $rating = $page->find('.score-container meta[itemprop="ratingValue"]')->attr('content');
        		
        $developer_web = $page->find(".dev-link:contains('".$developer_web_text."')")->attr('href');
        if (strlen($developer_web)>0) {
           $developer_web=substr($developer_web, strlen('https://www.google.com/url?q='));               
        }
        $developer_web = explode('&', $developer_web);
        $developer_web = $developer_web[0];
        
        $developer_mail = $page->find(".dev-link:contains('".$developer_mail_text."')")->attr('href');
        if (strlen($developer_mail)>0) {
           $developer_mail = str_replace('mailto:', '', $developer_mail);
        }
        
        $developer_privacy = $page->find(".dev-link:contains('".$developer_privacy_text."')")->attr('href');
        if (strlen($developer_privacy)>0) {
           $developer_privacy=substr($developer_privacy, strlen('https://www.google.com/url?q='));               
        }
        $developer_privacy = explode('&', $developer_privacy);
        $developer_privacy = $developer_privacy[0];
        $developer_privacy = str_replace("'", "%27", $developer_privacy);
        
        $video = $page->find('.play-click-target')->attr('data-video-url');
        $video = explode('?', $video);
        $video = $video[0];
        
        $video_image = $page->find('.video-image')->attr('src');

        $screen = array();
        $screenshots = $page->find('.thumbnails img[itemprop="screenshot"]');
        if (!empty($screenshots)) {
            foreach ($screenshots as $screenshot) {
                $screenshot = \pq($screenshot);
                //modificar los tamaños
                $screenshot = $screenshot->attr('src');  
                $screen[].=$screenshot;
            }
        }
        $screenshots = implode(",",$screen);

        //crear el array de salida con todos los datos
        $app['estado'] = 'OK';
        $app['app_id'] = pg_escape_string($app_id);
        $app['icon_url'] = $icon_url;
        $app['app_name'] = pg_escape_string($app_name);
        $app['app_description'] = pg_escape_string($app_description);
        $app['app_description_key'] = $app_description_key;
        $app['whatsnew'] = pg_escape_string($whatsnew);        
        $app['screenshots'] = $screenshots;    
        $app['video'] = $video;
        $app['video_img'] = $video_image;
        $app['genre'] = pg_escape_string($genre);
        $app['price'] = $price;
        $app['rating'] = $rating;
        $app['votes'] = $votes;
        $app['installs'] = $installs;
		$app['version'] = pg_escape_string($version);
		$app['version_updated'] = $version_updated ;        
        $app['operatingSystems'] = $operatingSystems;
        $app['size'] = $size;
        $app['contentRating'] = pg_escape_string($contentRating);    
        $app['developer_id'] = pg_escape_string($developer_id);
        $app['developer_name'] = pg_escape_string($developer_name); 
        $app['developer_web'] = pg_escape_string($developer_web);
        $app['developer_mail'] = $developer_mail;     
        $app['deveoper_privacy'] = pg_escape_string($developer_privacy);    
        $app['more_from_developer'] = $more_from_developer; 
        $app['related'] = $related;
        $app['storefront_id'] = $storefront_id;
        
        
        //print_r($app);
        //echo miIP().PHP_EOL;
        return $app;  
        
        phpQuery::unloadDocuments();
		$app = null;
		unset($app);
        
	} //end try
	catch (Exception $e) {
		return $app;
	} //end catch
    
}

function br2nl($string)
{
    return preg_replace('/\<br(\s*)?\/?\>/i', "\n", $string);    
    /*
    return preg_replace('/<br\\s*?\/??>/i', '', $text);    
    return preg_replace('#<br\s*?/?>#i', "\n", $string);      
    return preg_replace('/\<br\s*\/?\>/i', "\n", $string);           
    return preg_replace('/<br ?\/?>/', "\n",$string);
    return str_replace('<br>', '\n', $string);
    */
}
			       	
pg_close($con);

?>