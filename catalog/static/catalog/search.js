function update_visibilities(selector) {
	$(selector).each(
		function(index,elem) {
			var visible = true;
			var classes = $(elem).attr('class').split(/\s+/);
			for(var i = 0; i < classes.length-1; ++i)
			{
				if((classes[i] in visibilities) && !visibilities[classes[i]])
				{
					visible = false;
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
		//alert('adding tooltips');
		$(document).tooltip({
			items: '.ap-with-tooltip',
			content: function() {
				return $(this).find('.ap-resource-tooltip').html();
			},
			show: true,
			track: false,
			position: {
        		at: "left+30 top+30",
        		my: "right bottom",
        		collision: "flipfit",
        		within: $('#ap-panel')
        	}
        	});
	}
}

function update_search_results(search_urls) {
    var qq = '';
	var aa = '';
    if($('#q').val() != $('#q').data('init')) { qq = $('#q').val(); }
    if($('#a').val() != $('#a').data('init')) { aa = $('#a').val(); }
    $('#ap-panel').html('');
	// Interrogate search engines
	$.each(search_urls,function(idx,url) {
				$.ajax({
			             url: url,
			             type: "GET",
			             data: { q:qq, a:aa, t:$('#t').val()},
			             success: function (data) {
			             	// add results in listing
			             	data.map(function(result) {
			    	    		$('#ap-panel').append($(result['rendered']));
			             	});
			             	finished_engines++;
			             	add_tooltips();
			             },
			             error: function(data) {
			             	finished_engines++;
			             	add_tooltips();		             		
			             }
		        });
	});
}
	
var visibilities = {
		'resource' : true,
};

$(document).ready(function () {
	$('#ap-small-searchform-submit').attr('type','button');	
	$('#ap-small-searchform-submit').on('click', function() { update_search_results(search_urls); });
	$("#a,#q").keyup(function(event){ if(event.keyCode == 13){  $('#ap-small-searchform-submit').click(); }});
	$('#ap-small-searchform-submit').click();
	
	for(var i = 0; i < resource_types.length; i++)
	{
		visibilities[resource_types[i]] = $('#ap-filter-' + resource_types[i]).prop('checked');
		$('#ap-filter-' + resource_types[i]).data('resource_type',resource_types[i]);
		$('#ap-filter-' + resource_types[i]).change(function() {
			var r = $(this).data('resource_type');
			alert(r);
			visibilities[r] = !visibilities[r];
			update_visibilities('.ap-resource');
		});
		
	}
	update_visibilities('.ap-resource');
});
