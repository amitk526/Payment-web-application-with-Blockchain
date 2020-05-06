var otpgen;
$(document).ready(function() {
	$('#req_otp').on('click', function(event) {

		$.ajax({
			data : {},
			type : 'GET',
			url : '/otp',
			success: function(data) {
				console.log('success', data);
			}
		})
		.done(function(data) {
            otpgen = data.otp;
            $('#successAlert').text(" OTP : "+data.otp).show().delay(10000).fadeOut();
            $('#errorAlert').hide();
		});

		event.preventDefault();

	});
    $('form').on('submit', function(event) {
    
            $.ajax({
                data : {
                    payee : $('#payee_acn').val(),
                    amt : $('#amt').val(),
                    otp_enter : $('#otp').val(),
                    otp_gen : otpgen
                 },
                type : 'POST',
                url : '/processTransferFunds',
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
/*
$(document).ready(function() {

$('form').on('submit', function(event) {

		$.ajax({
			data : {
                payee : $('#payee_acn').val(),
                amt : $('#amt').val(),
 			},
			type : 'POST',
			url : '/processTransferFunds',
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
*/