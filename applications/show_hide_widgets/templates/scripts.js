document.addEventListener("DOMContentLoaded", function(event){
	setTimeout( function(){
		document.getElementsByClassName('Start_Button')[0].style["display"] = "none";
		document.getElementsByClassName('Stop_Button')[0].style["display"] = "none"; 
		document.getElementsByClassName('Mass_of_m1')[0].style["display"] = "none"; 
		document.getElementsByClassName('Spark')[0].style["display"] = "none"; 
	}, 2000)
})