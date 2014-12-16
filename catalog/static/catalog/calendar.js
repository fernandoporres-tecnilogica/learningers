function update_calendar(update_url,data) {
	$.ajax({
	    url: update_url,
	    type: "GET",
	    data: data,
	    success: function (data) {
	    		$('#ap-calendar').html($(data['rendered']));
	    		$('#ap-calendar-prev').on('click', function() { update_calendar(update_url,data['prev_date']); });
	    		$('#ap-calendar-next').on('click', function() { update_calendar(update_url,data['next_date']); });
	    },
	    error: function(data) {
	    	alert('error!')
	    }
	}); 
}
