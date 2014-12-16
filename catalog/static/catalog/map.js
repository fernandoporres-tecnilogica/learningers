function initialize_map(marker_data) {
	
	if(!marker_data.length)
		return;
	
	var map = new ol.Map({
		  layers: [
		    new ol.layer.Tile({
		      source: new ol.source.OSM()
		    })
		  ],
		  controls: ol.control.defaults({
		    attributionOptions: /** @type {olx.control.AttributionOptions} */ ({
		      collapsible: false
		    })
		  }),
		  target: 'ap-osm-map',
	});
		  		
	var view = new ol.View();
	
	var extent = [10000000000, 1000000000000, -100000000000, -100000000000];
	
	for(var i = 0; i < marker_data.length; i++)
	{
		var pos = ol.proj.transform([marker_data[i].x, marker_data[i].y], 'EPSG:4326', 'EPSG:3857');
		extent[0] = Math.min(extent[0],pos[0]);
		extent[1] = Math.min(extent[1],pos[1]);
		extent[2] = Math.max(extent[2],pos[0]);
		extent[3] = Math.max(extent[3],pos[1]);
		var marker_element = $('#marker').clone();
		$(marker_element).data('i',i);
		var marker = new ol.Overlay({
		  position: pos,
		  positioning: 'center-center',
		  element: marker_element,
		  stopEvent: false
		});
		map.addOverlay(marker);
		// Popup showing the position the user clicked
		var popup_element = $('#popup').clone(); 
		$(popup_element).attr('id','popup' + i.toString());
		$(popup_element).hide();
		$(popup_element).find('.popup-content').html(marker_data[i].title);
		var popup = new ol.Overlay({
		  element: popup_element,
		  position: pos,
		  positioning: 'center-center',
		  stopEvent: false
		});
		map.addOverlay(popup);
		
		$(marker_element).on('click', function(evt) {
			  $('#popup' + $(this).data('i').toString()).show();
		});

	}
	
	extent[0] -= 100;
	extent[1] -= 100;
	extent[2] += 100;
	extent[3] += 100;	
	view.setZoom(2);
	map.setView(view);
	view.fitExtent(extent,map.getSize());
//	map.zoomToExtent(annotations.getDataExtent());
}