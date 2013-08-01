<?php

$basedir = '/home/encoder/encoding/'; //your base directory including the trailing /

if($_GET['q']=="prog")
	{
		flush();
		$type = shell_exec('cat '.$basedir.'encodelog.log | grep "Output #0"'); //checks if encoding type is avi or mp4
		//echo $type;
		if (strpos($type,"mp4") !==false)
			{
				$type = "mp4";
				$details = shell_exec('sed -e \'s/\r/\n/g\' '.$basedir.'encodelog.log | grep frame= | tail -n 1'); //assumes mp4 type
				//echo $type;
			}
		elseif (strpos($type,"avi") !==false) {
				$type = "avi";
				$pass = shell_exec('cat '.$basedir.'encodelog.log | grep "xvid: 2Pass Rate Control" | tail -n 1');
				$pass = substr($pass,strpos($pass,"--")+3,1);
				if (empty($pass))
				{
					$details = shell_exec('sed -e \'s/\r/\n/g\' '.$basedir.'encodelog.log | grep frame= | tail -n 1');
				}
				else{
				$details = shell_exec('sed -e \'s/\r/\n/g\' '.$basedir.'encodelog.log | grep Pos: | tail -1'); //assumes avi type otherwise - courtesy of duckwad. because i can't into sed
				}
				echo "Encoding ".$type." - pass ";
			}
		
		$slen = 90; //modify for desired log width (90 is good to start)
		$details = preg_replace('/\s+?(\S+)?$/', '', substr($details, 0, $slen));
		
		if (empty($details))
			{
			echo "No encode in progress";
			$bar = "";
			goto end;
			}
		else
			{
				if($type=="avi")
				{
					//check pass
					//$pass = shell_exec('cat '.$basedir.'encodelog.log | grep "xvid: 2Pass Rate Control" | tail -n 1');
					//$pass = substr($pass,strpos($pass,"--")+3,1);
					//echo $pass;
				}
				
		$total_frames = shell_exec('cat '.$basedir.'encodelog.log | grep "Duration:.*start."');
		$hours = substr($total_frames,12,2);
		$mins = substr($total_frames, 15,2);
		$secs = substr($total_frames, 18,5);
		
		$total_frames = (($hours*3600)+($mins*60)+($secs))*23.976;
		
		if($type=="avi")
		{
			
			if(empty($pass))
			{	
				$fps_loc = strpos($details, "fps");
				$frame = substr($details,6,$fps_loc - 7);
				$prog = round(($frame/$total_frames*100),2);
				echo "0 - ffmpeg subtitle burn-in";
			}
			else
			{
				$prog = substr($details,strpos($details,"(")+1,2);
				echo $pass;
			}
		}
		else
		{
			$fps_loc = strpos($details, "fps");
			$frame = substr($details,6,$fps_loc - 7);
			$prog = round(($frame/$total_frames*100),2);
		}
		echo "<pre>$details</pre>";
		$bar = '$(function() {$("#enc-progress").progressbar({value:'.$prog.'});});';
		
		}
		$details = shell_exec('cat '.$basedir.'*.log | grep "Input #0"'); //same as above - change to match your directory
		$title = substr($details,strpos($details,"from")+6,-3);
		echo $prog.'% - '.$title;
		end:
	}
	
elseif($_GET['q']=="update")
	{
		$name = $_GET["name"];
		$type = $_GET["format"];
		
		$line = $name."|-tl -o ".$type." -m completed/";
		chdir($basedir);
		file_put_contents('queue.txt', trim($line).PHP_EOL, FILE_APPEND);
		
		echo "Added to queue...probably. Refreshing now";
	}	
	
elseif($_GET['q']=="wget")
	{
		flush();
		$url = 'wget --spider "'.$_GET["url"].'"';
		$dl = shell_exec($url.' 2>&1 | grep Length:');
		
		if($_GET["dl"]=="true")
			{
				$url = 'wget -o '.$basedir.'logfile -P '.$basedir.' "'.$_GET["url"].'" &';
				//same as above - change to match where you want the files to be downloaded. "logfile" is the wget log, -P is the dl directory
				shell_exec($url);
			}
		elseif($_GET["dl"]=="false")
			echo $dl;
	}

elseif($_GET['q']=="size")
	{
		flush();
		$logfile = shell_exec('cat '.$basedir.'logfile | tail -n 2');//once more - i should probably use a variable instead :/
		$dlprog = substr($logfile,strpos($logfile, "%")-3,3);
		if (strpos($dlprog,']') !==false)
			$dlprog = 100;
		$bar = '$(function() {$("#dl-prog").progressbar({value:'.$dlprog.'});});';
		
		echo $dlprog;
	}
elseif($_GET['q']=="dir")
	{
		flush();
		getfiles($basedir); //and again
	}

elseif($_GET['q']=="dircomp")
	{
		flush();
		getfiles($basedir.'completed/'); //and again
	}

elseif($_GET['q']=="start")
	{
		flush();
		chdir($basedir); //seriously - one more time. search+replace is probably useful
		$running = shell_exec('ps aux | grep "[e]ncode5.py"');
		if (empty($running))
				{
					flush();
					echo 'Encode started - probably successful. Don\'t take my word for it though...<br>';
					flush();
					$lel = shell_exec('sudo -u encoder python encode5.py -f queue.txt 2>&1'); //yay last time
					//echo $lel;
					
				}
			else echo "Noap noap noap. Already running. Not starting a new one :<";
	}

elseif($_GET['q']=="newfiles")
	{
		flush();
		chdir($basedir);
		
		$files = scan_dir($basedir);
		$filtered = Array();
		foreach($files as $file){
			if ((strpos($file,".mkv"))!==false){
				array_push($filtered,$file);
				}
			if ((strpos($file,".mp4"))!==false){
				array_push($filtered,$file);
				}
			if ((strpos($file,".ts"))!==false){
				array_push($filtered,$file);
				}
			}
		
		echo '<select id="fnames">';
		foreach($filtered as $file){
			echo '<option value="'.$file.'">'.$file.'</option>';
			}
		echo '</select>';
	}

function hsize($bytes, $decimals = 2) {
	$size = array('B', 'kB', 'MB', 'GB', 'TB');
	$factor = floor((strlen($bytes) - 1)/3);
	return sprintf("%.{$decimals}f", $bytes / pow(1024, $factor)). @$size[$factor];
	}

	
function getfiles($dir){
		$files = scan_dir($dir);
		$fsize = count($files);
		for ($i = 0; $i <=$fsize; $i++)
			{
				if (preg_match('/.mp4|.mkv|.avi|.ts|log/', $files[$i])){
					if (preg_match('/.mkv|.ts/', $files[$i])){
						$color = 'red';
						}
					elseif (preg_match('/.mp4|.avi/', $files[$i])){
						$color = 'orange';
						}
					else {
						$color = 'gray';
						}
				echo '<span class="leftnm" style="float: left; color:'.$color.';">'.$files[$i].' </span><span class="leftnm" style="float: right; color:'.$color.'">'.hsize(filesize($dir.$files[$i])).'</span><br>';
				}
			}
	}

function scan_dir($dir){
	$ignored = array('.', '..');
	$files = array();
	foreach (scandir($dir) as $file) {
		if (in_array($file,$ignored)) continue;
		$files[$file] = filemtime($dir.'/'.$file);
		}
	
	arsort($files);
	$files = array_keys($files);
	return ($files) ? $files : false;
}
	
?>
<script type="text/javascript">
	<?php echo $bar; ?>;
	$('#progresstext').html();
 </script>