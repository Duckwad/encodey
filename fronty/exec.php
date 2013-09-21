<?php

	include 'vars.php';

if($_GET['q']=="update")
	{
		$name = $_GET["name"];
		$type = $_GET["format"];
		
		$line = $name."|-o ".$type." -m completed/";
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

elseif($_GET['q']=="dl")
	{
		$file = $basedir.$_GET['file'];
		if (file_exists($file)) {
			header('Content-Description: File Transfer');
			header('Content-Type: application/octet-stream');
			header('Content-Disposition: attachment; filename='.basename($file));
			header('Content-Transfer-Encoding: binary');
			header('Expires: 0');
			header('Cache-Control: must-revalidate');
			header('Pragma: public');
			header('Content-Length: ' . filesize($file));
			ob_clean();
			flush();
			readfile($file);
			exit;
			}
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
					$lel = shell_exec('sudo -u '.$user.' python encode6.py -f queue.txt 2>&1'); //yay last time
					//echo $lel;
					flush();
					
				}
			else echo "Noap noap noap. Already running. Not starting a new one :<";
			flush();
	}
	
elseif($_GET['q']=="stop-all")
	{
		flush();
		killall();
		flush();
	}

elseif($_GET['q']=="stop-cur")
	{
		flush();
		killall();
		$file = file($basedir."queue.txt");
		array_shift($file);
		
		$fp = fopen($basedir."queue.txt","w+");
		for ($x=0; $x < sizeof($file); $x++)
		{
			fputs($fp,$file[$x]);
		}
		fclose($fp);
		
		chdir($basedir);
		$running = shell_exec('ps aux | grep "[e]ncode6.py"');
		if (empty($running))
				{
					flush();
					echo 'Encode stopped - continuing from next item in queue<br>';
					$lel = shell_exec('sudo -u '.$user.' python encode6.py -f queue.txt 2>&1'); //yay last time
					//echo $lel;
					flush();
					
				}
			else echo "Noap noap noap. Already running. Not starting a new one :<";
			flush();
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

elseif($_GET['q']=="dllist")
		{
			flush();
			$dir = $basedir.'completed/';
			$files = scan_dir($dir);
			echo '<select id="dllinks">';
			foreach($files as $file){
				echo '<option value="'.$dir.$file.'">'.$file.'</option>';
				}
			echo '</select>';	
				
		}

function killall(){
		echo "Killing all running encodes, bunnies, and ponies...";
		shell_exec('sudo -u '.$user.' pkill python');
		shell_exec('sudo -u '.$user.' pkill ffmpeg');
		shell_exec('sudo -u '.$user.' pkill mencoder');
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