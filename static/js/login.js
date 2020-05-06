$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				email : $('#email').val(),
                password : $('#pwd').val(),
			},
			type : 'POST',
			url : '/processLogin',
			success: function(data) {
				console.log('success', data);
			}
		})
		.done(function(data) {

			if (data.response == 0) {
				$('#errorAlert').text(data.error).show().delay(5000).fadeOut();
			}
			else{
				window.location = data.redirecturl;
			}

		});

		event.preventDefault();

	});

});