function update_visibilities(selector) {
	$(selector).each(
		function(index,elem) {
			var visible = 1;
			classes = $(elem).attr('class').split(/\s+/);
			for(var i = 0; i < classes.length-1; ++i)
			{
				if((classes[i] in visibilities) && !visibilities[classes[i]])
				{
					visible = 0;
					break;
				}
			}
			if(!visible)
			{
				$(elem).hide();
			} else {
				$(elem).show();
			}
		}
	);
}

var finished_engines = 0;
function add_tooltips() {
	if(finished_engines >= 1)
	{
		alert('adding tooltips');
		$(document).tooltip({
			items: '.ap-with-tooltip',
			content: function() {
				if(!$(this).data('tooltip'))
				{
					$(this).data('tooltip', $(this).next().detach().html());
				}
				return $(this).data('tooltip');
			},
			show: true,
			track: false,
			position: {
        		at: "left+30 top+30",
        		my: "right bottom",
        		collision: "flipfit",
        		within: $('#panel')
        	}
        	});
	}
}

function update_search_results(search_url) {
    var qq = '';
	var aa = '';
    if($('#q').val() != $('#q').data('init')) { qq = $('#q').val(); }
    if($('#a').val() != $('#a').data('init')) { aa = $('#a').val(); }
    $('#ap-panel').html('');
	$.ajax({
	    url: search_url,
	    type: "GET",
	    data: { q:qq, a:aa, t:$('#t').val()},
	    success: function (data) {
	    	// add results in listing
	    	data.map(function(result) {
	    		//alert(result['rendered']);
	    		$('#ap-panel').append($(result['rendered']));
	    	});
	    	add_tooltips();
	    },
	    error: function(data) {
	    	alert('error!')
	    }
	}); 
}
	
		
