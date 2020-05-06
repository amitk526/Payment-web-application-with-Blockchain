$(document).ready(function() {

	$('form').on('submit', function(event) {

		$.ajax({
			data : {
                fname : $('#fname').val(),
                lname : $('#lname').val(),
                adhn : $('#aadhar_no').val(),
                phnn : $('#phn_no').val(),
				email : $('#email').val(),
                pwd : $('#pwd').val(),
                pwdr : $('#pwd_repeat').val(),
			},
			type : 'POST',
			url : '/processEditProfile',
			success: function(data) {
				console.log('success', data);
			}
		})

		.done(function(data) {

			if (data.response==0) {
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