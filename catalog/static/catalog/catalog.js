function makeLayout() {
/*	$('#ap-content').css({
            height: $(window).height()-$('#ap-headbar').outerHeight()
        });
	$('#ap-panel').css({
        width: $(window).width()-$('#ap-sidebar').outerWidth()-getBrowserScrollSize().width,
        height: $(window).height()-$('#ap-headbar').outerHeight()
    });
	$('#ap-sidebar').css({
        height: $(window).height()-$('#ap-headbar').outerHeight()
	});
*/
   	$('#ap-source-container').css({
            width: $(window).width()-$('#ap-sidebar').outerWidth()-$('#ap-rightbar').outerWidth(),
        });
        
    $('#ap-rightbar').css({
            height: $(window).height()-$('#ap-headbar').outerHeight()
        }); 
    $('#ap-source-container').show();
    $('#ap-rightbar').show();
}

$(window).load(makeLayout);
$(window).resize(makeLayout);

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

var active_tab = 0;
function switch_tabs() {
	if(active_tab == 0)
	{
		$('#ap-info-tab').hide();
		$('#ap-versions-tab').show();
		active_tab = 1;
		$('#ap-versions-button img').css({'border':'1px solid red'});
	} else {
		$('#ap-versions-tab').hide();
		$('#ap-info-tab').show();
		active_tab = 0;
		$('#ap-versions-button img').css({'border':''});
	}
}