<?php

	include 'vars.php';
	$files = $_POST['files'];
	
	foreach($files as $file){
		unlink($basedir.$file);
	}

?>