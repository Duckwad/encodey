$(document).ready(function()
  {
	var files = new Array();
	//exec.php is called every second to get current file listing
   var refreshId = setInterval(function() 
   {
	 $('#timeval').load('prog.php');
   }, 1000);
   //stop the update when this button is clicked
   $("#stop").click(function() 
   {
   	clearInterval(refreshId);
   });
   
   
   $("#get-info").click(function()
   {
		
				var link = $("#ubox").val();
				var url = "exec.php?q=wget&dl=false&url="+link;
				$("#dl").load(url);
			
	});
	
	$("#start-dl").click(function()
	{
		$("#dl").fadeIn('slow',function()
			{
				var link = $("#ubox").val();
				var url = "exec.php?q=wget&dl=true&url="+link;
				$(this).load(url);
				var refreshId2 = setInterval(function()
				{
					$("#dl").load('exec.php?q=size');
				},1000);
				$("#stop-dlrefresh").click(function()
				{
					clearInterval(refreshId2);
				});
			});
	});
	
	$("#enc-start").click(function()
	{
		$("#enc-conf").html("Encode probably started. Don't take my word for it though");
		$("#enc-conf").load('exec.php?q=start');
	});
	
	$("#stop-all").click(function()
	{
		if(confirm('Really stop all encodes?')){
			$("#enc-conf").empty();
			$("#enc-conf").load('exec.php?q=stop-all');
			}
	});
	
	$("#stop-cur").click(function()
	{
		if(confirm('Really stop current encode?')){
			$("#enc-conf").empty();
			$("#enc-conf").load('exec.php?q=stop-cur');
			setTimeout(function() {
				$("#ed-frame").attr('src', $("#ed-frame").attr('src'));
				return false;
				}, 1000);
			}
	});
	
	$("#refr-list").click(function()
	{
		$("#filelist").load('exec.php?q=dir');
		$("#completed").load('exec.php?q=dircomp');
	});
	
	$("#selfile").click(function()
	{
		var name = $('#fnames').val();
		var type = $('#format').val();
		var loader= "exec.php?q=update&name="+name+"&format="+type;
		$.ajax({
			url: loader,
			datatype: 'html',
			success: function(html) {
				$("#update").html(html);
				setTimeout(function() {
					$("#update").empty();
					$("#ed-frame").attr('src', $("#ed-frame").attr('src'));
					return false;
					}, 2500);
			}
		});
	});
	
	$("#filelist").load('exec.php?q=dir');
	$("#completed").load('exec.php?q=dircomp');
	$("#newfiles").load('exec.php?q=newfiles');
	$("#dlfiles").load('exec.php?q=dllist');
	setInterval(function() 
   {
	 $("#sysinfo").load('sysinfo.php');
   }, 2000);
		
	$("#dlnow").click(function()
	{
		var file = $('#dllinks').val();
		window.open("download.php?file="+file);
	});
	
	$("#del").click(function()
	{
		var sel = $('#dllinks').val();
		var pos = sel.indexOf("completed");
		sel = sel.substring(pos);
		files.push(sel);
		if (files.length==1)
		{
			$('#dellist').empty();
		}
		$('#dellist').append(files[files.length-1]+"<br>");
	});
	
	$("#del1").click(function()
	{
		var sel = $('#fnames').val();
		files.push(sel);
		if (files.length==1)
		{
			$('#dellist').empty();
		}
		$('#dellist').append(files[files.length-1]+"<br>");
	});
	
	$("#delnow").click(function()
	{
		if(confirm('Really delete these files?')){
		$.post('delete.php', { 'files':files});
		$("#filelist").load('exec.php?q=dir');
		$("#completed").load('exec.php?q=dircomp');
		$("#newfiles").load('exec.php?q=newfiles');
		$("#dlfiles").load('exec.php?q=dllist');
		files.length = 0;
		$('#dellist').html("Deleted... probably");
		}
		
	});

	
	$(function() {
    $( "input[type=submit], a, button" )
      .button()
      .click(function( event ) {
        event.preventDefault();
      });
  });
				
   });