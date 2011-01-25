/*
	Что хочется от маркера.
	В идеале Svg-представление.
	Задание цвета, иконки, меню по нажатию (показать трек, послать команду системе и т.п.)
	В идеале автоматическое обновление положения объекта
*/

(function(){		// Не захламляем глобальное пространство имен временными функциями и переменными

function LastMarker(options)
{
        this.map = options.map;
        this.div = null;
        this.arrdiv = null;
	this.title = options.title || "";
	this.position = options.position;
	this.point = this.position;
	this.infowindow = null;
	this.skey = null;
	this.color = options.color || 'green';
	this.car = options.car || 'Не определено';
	this.skey = options.skey;

	this.setMap(options.map);

	//console.log('last marker at '+ options.position);
}

LastMarker.prototype = new google.maps.OverlayView();

function add_geo_row(label, value) {
	$('#tbl_info tbody').append('<tr><td>'+label+'</td><td><b>'+value+'</b></td></tr>');
}

function more_info(data){
	//$("#moreinfo").html("Ура: " + ":" + data.answer);
	$("#moreinfo").html('');
	add_geo_row('Спутники', data.point.sats);
	add_geo_row('Скорость', data.point.speed + 'км/ч');
	add_geo_row('Основное питание', data.point.vout + 'В');
	add_geo_row('Резервное питание', data.point.vin + 'В');
	add_geo_row('Тип метки', data.point.fsource);
}

/*
function dt_to_date(dt){
	return dt[4]+dt[5] + '/' + dt[2]+dt[3] + '/20' + dt[0]+dt[1] + ' ' + dt[6]+dt[7] + ':' + dt[8]+dt[9] + ':' + dt[10]+dt[11];
}
*/

LastMarker.prototype.Info = function() {
	//alert('Bo ' + this.point.date);
	var point = this.point;
	var skey = this.skey;
	/*console.*/log("skey = " + skey);
	if(this.infowindow) this.infowindow.close();
	this.infowindow = new google.maps.InfoWindow({content:
		'<div style="width: 220px; height: 220px; border: none;"><div class="info-header">' + dt_to_datetime(point.date) + "</div>" +
		/*'Скорость: <b>' + point.speed.toFixed(1) + " км/ч" +*/
		'<table id="tbl_info" width="100%">' +
		'<tr><td>Направление:</td><td><b>' + point.angle.toFixed(0) + "°</b></td></tr>" +
		'<tr><td>Долгота:</td><td><b>' + point.lat().toFixed(5) + "</b></td></tr>" +
		'<tr><td>Широта:</td><td><b>' + point.lng().toFixed(5) + "</b></td></tr>" +
		/*'</b><br />Спутники: <b>' + results[i].sats +*/
		/*'</b><br />Питание: <b>' + vtext +*/
		/*'</b><br />Датчик 1: <b>' + results[i].in1.toFixed(3) +
		'</b><br />Датчик 2: <b>' + results[i].in2.toFixed(3) +*/
		'</table>' + 
		'<div id="moreinfo" title="Ожидайте, идет получение дополнительной информации."><center><img src="/images/loading.gif" /></center></div></div>',
		position: point
	})
	//self = this;
		//$('#moreinfo').slideUp().delay(300).fadeIn();
		//$("#moreinfo").animate({left:'+=200'},2000);
		var self = this;
		url = "/api/geo/info?skey="+skey+"&point="+point.date;
		$.getJSON(url, function (data) {
			//$("#progress").html("Обрабатываем...");
			/*console.*/log("JSON data: ", data);
			if (data.answer && data.answer === 'ok'){
				/*this.infowindow.close();
				this.infowindow = new google.maps.InfoWindow({content:
					position: point,
				});*/

				//if(!$('#tbl_info tbody')){ sleep(10); }

				if($('#tbl_info tbody')){
					$('#tbl_info tbody').ready(function(){
						/*console.*/log("JSON data: jquery domready.");
						more_info(data);
					});
					//console.log("JSON data: ready on request.");
					//more_info(data);
				}/*else{
					$('#tbl_info tbody').ready(function(){
						console.log("JSON data: jquery domready.");
						more_info(data);
						}); 
				}*/
				//google.maps.event.addListener(self.infowindow, 'domready', function(){
				//	console.log("JSON data: domready");
				//	more_info(data);
				//});
			}
			/*console.log("getJSON parce");
			if (data.answer && data.points.length > 0) {
				ParcePath(data.points, data.bounds);
			}*/
		});

//	infowindow.open(map, map.getMarker(i));
	this.infowindow.open(map);
}

LastMarker.prototype.onAdd = function() {

	// Note: an overlay's receipt of onAdd() indicates that
	// the map's panes are now available for attaching the overlay to the map via the DOM.

	var div = document.createElement('div');
	div.marker = this;

	div.setAttribute("class", "lastmarker");
	div.setAttribute("title", this.title);
	div.setAttribute("skey", this.skey);
	//div.addEventListener('mouseover', function(e){
	//	console.log('aa');
	//});
	//div.setAttribute("onclock", "function(){console.log('aa');}");
	//div.innerHTML = '2';

	//var title = document.createElement('div');
	//title.setAttribute("class", "lastmarker-title");
	//title.setAttribute("style", "background-color:"+this.color+";");
	//div.appendChild(title);
	//title.innerHTML = '<p>'+Math.round(Math.random()*9)+'</p>';

	var label = document.createElement('div');
	label.setAttribute("class", "lastmarker-label");
	label.innerHTML = this.car;

	var control = document.createElement('div');
	control.setAttribute("class", "lastmarker-control");
	var panel = ''
	panel += '<table><tbody>';
	panel += '<tr><td>Время</td><td>-</td></tr>';
	panel += '<tr><td>Скорость</td><td>-</td></tr>';
	panel += '<tr><td>Питание</td><td>-</td></tr>';
	panel += '<tr><td>Спутники</td><td>-</td></tr>';
	panel += '<tr><td>Топливо</td><td>-</td></tr>';
	panel += '<tr><td>Рефрижератор</td><td>-</td></tr>';
	panel += '</tbody></table>';
	panel += '<button title="Послать сигнал системе.">Вызов</button>';
//	panel += '<button title="Послать сигнал системе." class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-icon-primary" name="btn_menu" id="nav_logs" href="/s/Logs" role="button" aria-disabled="false"><span class="ui-button-icon-primary ui-icon ui-icon-alert"></span><span class="ui-button-text">Сигнал</span></button>'
	control.innerHTML = panel;
	label.appendChild(control);

	//console.log($(control).find('button'));
	$(control).find('button').button();

	div.appendChild(label);

//	div.setAttribute("class", (this.result.speed < 1.0)?"mymarker-stop":"mymarker-move");

	div.addEventListener('click', function(e){
		//this.marker.Info();
	}, false);

/*
	div.addEventListener('mouseover', function(e){
		//this.marker.Info();
		//console.log('aaa');
		var minind = 10000;
		var maxind = -10000;
		var log = 'before: ';
		$('.lastmarker').each(function(){
			var ind = $(this).css('z-index');
			//console.log(ind);
			if(ind == 'none' || ind == 'auto') ind = 0; else ind = parseInt(ind, 10);
			log += ' ' + ind;
			minind = Math.min(minind, ind);
			maxind = Math.max(maxind, ind);
			$(this).css('z-index', '' + (ind-1));
		});
		$(this).css('z-index', ''+(maxind+1));
		console.log(log);
		log = 'after: ';
		$('.lastmarker').each(function(){
			var ind = $(this).css('z-index');
			//console.log(ind);
			if(ind == 'none' || ind == 'auto') ind = 0; else ind = parseInt(ind, 10);
			log += ' ' + (ind-minind+1);
			$(this).css('z-index', '' + (ind-minind+1));
		});

		console.log(log);
	}, false);
*/


	if(0){
	div.addEventListener('mouseover', function(e){
		arrdiv = document.getElementById("arrowdiv");
		if(arrdiv == null){
			arrdiv = document.createElement('div');
			arrdiv.setAttribute("id", "arrowdiv");
			arrdiv.setAttribute("class", "arrowdiv");
			panes.overlayMouseTarget.appendChild(arrdiv);
		}
		arrdiv.setAttribute("style", "-webkit-transform: rotate(" + this.marker.angle + "deg);z-index:-1;");

		var overlayProjection = this.marker.getProjection();

		// Retrieve the southwest and northeast coordinates of this overlay
		// in latlngs and convert them to pixels coordinates.
		// We'll use these coordinates to resize the DIV.
		//var divpx = overlayProjection.fromLatLngToDivPixel(this.marker.div.point);

		arrdiv.style.left = parseInt(this.marker.div.style.left, 10) - 13 + 'px';
		arrdiv.style.top = parseInt(this.marker.div.style.top, 10) - 13 + 'px';

		/*this.marker.arrdiv.style.display = "block";*/

		//this.marker.div.style['background-image'] = 'url(images/marker-select.png)'
		//this.marker.div.style.width = 16;
		//this.marker.div.style.height = 16;
	}, false);

	div.addEventListener('mouseout', function(e){
		arrdiv = document.getElementById("arrowdiv");
		if(arrdiv) arrdiv.style.display = "none";
		/*if(this.marker.i % 8) this.marker.arrdiv.style.display = "none";*/
	}, false);
	}

	if(0){
	var arrdiv = document.createElement('div');
	arrdiv.setAttribute("class", "arrowdiv");
	arrdiv.setAttribute("style", "-webkit-transform: rotate(" + this.angle + "deg);z-index:-1;");

	if(this.i % 8) arrdiv.style.display = "none";
	}

	this.div = div;
//	this.label = label;
//	this.arrdiv = arrdiv;
	//this.arrdiv = arrdiv;

	// We add an overlay to a map via one of the map's panes.
	// We'll add this overlay to the overlayImage pane.
	var panes = this.getPanes();
	this.panes = panes;
//  	panes.overlayLayer.appendChild(arrdiv);
//	panes.overlayLayer.appendChild(div);
//	panes.overlayMouseTarget.appendChild(arrdiv);
//	panes.overlayMouseTarget.appendChild(div);

//	panes.floatPane.appendChild(div);
	panes.overlayImage.appendChild(div);
//	panes.overlayImage.appendChild(label);

	//$(div).mouseover(function(){console.log('aaa');});

}

LastMarker.prototype.setPosition = function(point) {
	log('Marker change position', point);
	this.position = point;
	this.point = point;
//	this.arrdiv.setAttribute("style", "-webkit-transform: rotate(" + point.angle + "deg);z-index:-1;");
//	console.log('MyMarker.protorype.setPosition');
//	this.setTitle(dt_to_datetime(point.date));
	this.draw();
}


LastMarker.prototype.onRemove = function() {
	this.div.removeChild(this.arrdiv);
	this.div.parentNode.removeChild(this.div);
	this.arrdiv = null;
	this.div = null;
/*
	if(this.arrdiv){
		this.arrdiv.parentNode.removeChild(this.arrdiv);
		this.arrdiv = null;
	}
*/
}

LastMarker.prototype.draw = function() {

	if(this.position){
		// Size and position the overlay. We use a southwest and northeast
		// position of the overlay to peg it to the correct position and size.
		// We need to retrieve the projection from this overlay to do this.
		var overlayProjection = this.getProjection();

		// Retrieve the southwest and northeast coordinates of this overlay
		// in latlngs and convert them to pixels coordinates.
		// We'll use these coordinates to resize the DIV.
		var divpx = overlayProjection.fromLatLngToDivPixel(this.position);
		// var lng = overlayProjection.fromLatLngToDivPixel(this.point.lng());

		// Resize the image's DIV to fit the indicated dimensions.
		var div = this.div;
		div.style.left = divpx.x - 8 + 'px';
		div.style.top = divpx.y - 8 + 'px';
	}
/*
	if(this.arrdiv){
		var arrdiv = this.arrdiv;
		arrdiv.style.left = divpx.x - 16 + 'px';
		arrdiv.style.top = divpx.y - 16 + 'px';
	}
*/
//	console.log('LastMarker.protorype.draw.');
}
	window.LastMarker = LastMarker;

})();
