$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
				email : $('#email').val(),
				password : $('#pwd').val(),
				passwordr : $('#pwdr').val(),
			},
			type : 'POST',
			url : '/processSignup',
			success: function(data) {
				console.log('success', data);
			}
		})
		.done(function(data) {

			if (data.error) {
				$('#errorAlert').text(data.error).show().delay(5000).fadeOut();
                $('#successAlert').hide();
			}
			else {
				$('#successAlert').text(data.msg).show().delay(5000).fadeOut();
                $('#errorAlert').hide();
			}

		});

		event.preventDefault();

	});

});