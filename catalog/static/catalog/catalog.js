function makeLayout() {
	$('#ap-content').css({
            height: $(window).height()-$('#ap-headbar').outerHeight()
        });
}

$(makeLayout);
$(window).resize(makeLayout);
