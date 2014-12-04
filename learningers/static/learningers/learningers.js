function makeLayout() {
	$('#ap-panel').css({
            width: $(window).width()-$('#ap-sidebar').outerWidth()-getBrowserScrollSize().width,
            height: $(window).height()-$('#ap-headbar').outerHeight()
        });
    $('#ap-sidebar').css({
            height: $(window).height()-$('#ap-headbar').outerHeight()
        });
}

$(makeLayout);
$(window).resize(makeLayout);

function makeLayout2() {
	$('#ap-source-container').css({
            width: $(window).width()-$('#ap-sidebar').outerWidth()-$('#ap-rightbar').outerWidth(),
        });
    $('#ap-rightbar').css({
            height: $(window).height()-$('#ap-headbar').outerHeight()
        }); 
    $('#ap-source-container').show();
    $('#ap-rightbar').show();
}
$(window).load(makeLayout2);
$(window).resize(makeLayout2);

function delete_resource(delete_url) {
	$( "#confirm-delete" ).dialog({ 
		buttons: [ { 
			text: gettext('Oui'), 
			click: function() { 
				$( this ).dialog( "close" );
				$.ajax({
			        url: delete_url,
			        type: "DELETE",
			        dataType: 'text',
			        success: function(data) {
		        		$( "#success-delete" ).dialog({ buttons: [{ text: "OK", click: function() { window.location.href="/"; } }]});
			        }
		   		});	
			 } }, { 
			text: gettext('Non'), 
			click: function() { 
				$( this ).dialog( "close" ); 
			} 
			}] 
	});
}