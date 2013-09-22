<?php

$info = shell_exec('sar -u 2 1 | tail -n 1');
$cpu = round(100-(substr($info, -6,4)),1);

$mem = shell_exec('free -m | grep "cache:"');
$mem = substr($mem,19);
$mem = explode(' ',trim($mem));

echo "CPU Usage: ".$cpu."% <strong>|</strong> ";
echo "RAM Usage: ".$mem[0]."MB";


?>