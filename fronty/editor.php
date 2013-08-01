
<?php

$fn = "/home/encoder/encoding/queue.txt";
if (isset($_POST['content']))
{
    $content = stripslashes($_POST['content']);
    $fp = fopen($fn,"w") or die ("Error opening file in write mode!");
    fputs($fp,$content);
    fclose($fp) or die ("Error closing file!");
}

?>

<script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.1/jquery.min.js"></script>
 <link rel="stylesheet" href="http://code.jquery.com/ui/1.10.3/themes/trontastic/jquery-ui.css" />
<link href='http://fonts.googleapis.com/css?family=Expletus+Sans' rel='stylesheet' type='text/css'>
 <script src="http://code.jquery.com/ui/1.10.3/jquery-ui.js"></script>
  <script type="text/javascript" src="exec.js"></script>
 <link rel="stylesheet" href="style.css" type="text/css">

<form action="<?php echo $_SERVER["PHP_SELF"] ?>" method="post">
    <textarea rows="15" cols="70%" wrap="soft" name="content"><?php readfile($fn); ?></textarea>
    <span><button type="submit" value="Update" style="float: right;">Update</button></span>
</form>