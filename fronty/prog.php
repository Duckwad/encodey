<?php

	include 'vars.php';
	flush();
	$info = shell_exec('cat '.$basedir.'progress.log'); //reads progress file
	
	if (strpos($info,"FINISHED") !==false){
		echo "<script type='text/javascript'>
		$('#bardivs').empty();
		$('#filelist').load('exec.php?q=dir');
		setTimeout(function() {
			$('#update').empty();
			$('#ed-frame').attr('src', $('#ed-frame').attr('src'));
			$('completed').load('exec.php?q=dircomp');
			return false;
			}, 2500);
		</script>";
}
	
	if (empty($info))
		{
			echo "No encode in progress";
			$bar = "";
			goto end;
		}
		
	echo "<pre>$info</pre>";
	
	$loc = array();
	
	for ($x = 0; $x <=5; $x++){
		$end = strpos($info,"|");
		$loc[$x] = substr($info,0,$end);
		$info = substr($info,$end+1);
		}
	
	$loc[1] = substr($loc[1],0,-1);
	echo $loc[1].' - '.$loc[0];
	$bar1 = '$(function() {$("#enc-progress").progressbar({value:'.$loc[1].'});});';
		
	end:
?>
<script type="text/javascript">
	<?php echo $bar1; ?>;
	$('#progresstext').html();
 </script>