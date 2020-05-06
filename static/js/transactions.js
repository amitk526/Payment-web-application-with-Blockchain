$(document).ready(function() {
    var vtime; 
    sendRequest();

function sendRequest(){
    $.ajax({
			type : 'GET',
			url : '/processTransactions',
			success: function(data) {
                console.log('success', data);
            }
                  
		})
		.done(function(data) {
            var response = data;
                    var rows= "";
                    $.each(response, function(i, item) {
                        rows = rows+'<tr>'+
                            '<td>'+item.tid+
                            '<td>'+item.date+
                            '<td>'+item.acnn+
                            '<td>'+item.transact+
                            '<td>'+item.balance+'</tr>';
                    });
                    var table = '<div class="bootstrap_datatables" id="div1">'+
                    '<div class="container py-5" id="div2">'+
                      '<div class="row py-5" id="div3">'+
                        '<div class="col-lg-10 mx-auto" id="div4">'+
                          '<div class="card rounded shadow border-0" id="div5">'+
                            '<div class="card-body p-5 bg-white rounded" id="div6">'+
                              '<div class="table-responsive" id="div7">'+
                                '<table id="example" style="width:100%" class="table table-striped table-bordered" id="t1">'+
                                  '<thead>'+
                                    '<tr>'+
                                      '<th>ID</th>'+
                                      '<th>Date-Time</th>'+
                                      '<th>Account No.</th>'+
                                      '<th>Transact</th>'+
                                      '<th>Balance</th>'+
                                    '</tr>'+
                                  '</thead>'+
                                  '<tbody id="table_body">'+
                                    '<tr>'+
                                      '<td></td>'+
                                      '<td></td>'+
                                      '<td></td>'+
                                      '<td></td>'+
                                      '<td></td>'+
                                    '</tr>'+
                                    rows+
                                  '</tbody>'+
                                '</table>'+
                              '</div>'+
                            '</div>'+
                          '</div>'+
                        '</div>'+
                      '</div>'+
                    '</div>'+
                    '</div>'
                    $("#table_div").empty();
                    $('#table_div').append($.parseHTML(table)); 
                    clearTimeout(vtime);
                    vtime = setInterval(sendRequest, 10000);
            });
        };
    });




    //PRIOR ATTEMPTS:
                //response = $.parseJSON(response);

                /*
                $.each(response, function(i, item) {
                    var $tr = $('<tr>').append(
                        $('<td>').text(item.tid),
                        $('<td>').text(item.date),
                        $('<td>').text(item.debit),
                        $('<td>').text(item.credit),
                        $('<td>').text(item.balance)
                    );
                    //console.log($tr.html());
                });
                //$('#table_body').append($tr);
                */
                     
                /*
                $("#div1").addClass("bootstrap_datatables");
                $("#div2").addClass("container py-5");
                $("#div3").addClass("row py-5");
                $("#div4").addClass("col-lg-10 mx-auto");
                $("#div5").addClass("card rounded shadow border-0");
                $("#div6").addClass("card-body p-5 bg-white rounded");
                $("#div7").addClass("table-responsive");
                $("#t1").addClass("table table-striped table-bordered");
                */