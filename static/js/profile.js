$(document).ready(function() {

	$('form').on('submit', function(event) {
        event.preventDefault();
        window.location = '/editProfile';	
	});

});