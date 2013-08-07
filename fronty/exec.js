$(document).ready(function()
  {
	//exec.php is called every second to get current file listing
   var refreshId = setInterval(function() 
   {
	 $('#timeval').load('exec.php?q=prog');
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
	
		
	$(".fname").hover(
    function() {
        $(this).css("color", "red");
    },
    function() {
        $(this).css("color", "green");
    });
	$(function() {
    $( "input[type=submit], a, button" )
      .button()
      .click(function( event ) {
        event.preventDefault();
      });
  });
				
   });