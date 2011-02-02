(function(){

var geocoder;

var adrlist = [];

function getGeocode(adrlist, i, recur) {
	//console.log(adrlist[i]);
	//log('geoget at ' + i);
	if(adrlist[i].stop) log('stop: ' + i);

	geocoder.geocode({'latLng': new google.maps.LatLng(adrlist[i].pos[0], adrlist[i].pos[1]) }, function(results, status) {
		if(adrlist[i].stop) {log('stop2: ' + i); return;}
		if (status == google.maps.GeocoderStatus.OK) {
			var address = geocode_to_addr(results);
			$('#'+adrlist[i].id).html(address).attr('title', '');
			delete adrlist[i];
			//console.log(adrlist.some());
			var empty = true;
			for(var j in adrlist) {empty = false; break;}
			if(empty == true){
				$(".control").show();
			}

		} else {
			if(recur) {
				adrlist[i].cb = setTimeout(function(){getGeocode(adrlist, i, recur-1)}, 6000);
			} else {
				log('Error geocoding at ' + i + ' with ');
			}
		}
	});
}

function genReport(skey, start, stop, title) {
	//$(".control").hide();
	for(var i in adrlist) { clearInterval(adrlist[i].cb); adrlist[i].stop = true; }

	$('#report_header').html('Отчет для системы ' + config.sysbykey[skey].desc + ' за <span style="border: 1px solid black; padding: 0 4px 0 4px">' + title + '</span>');

	$( "#report tbody" ).empty();

	$.getJSON('/api/report/get?skey='+skey+'&from='+start+'&to='+stop, function (data) {
		//$("#progress").html("Обрабатываем...");
		log("getJSON parce");
		if (data.answer == 'ok') {
			//ParcePath(data);
			log("Show report...");

			$("#report_total_dist").html(ln_to_km(data.summary.length));
			$("#report_total_movetime").html(td_to_hms(data.summary.movetime));
			$("#report_total_avspeed").html(data.summary.speed.toFixed(1) + ' км/ч');

			var tbody = $( "#report tbody" );
			//console.log(tbody);
			adrlist = [];
			var cur_date = '';
			if(data.report.length == 0){
				tbody.append('<tr><td>Нет данных.</td></tr>');
			}

			for(var i in data.report){
				var ad_id = 'ad_' + i;
				var rec = data.report[i];
				var tp;

				switch(rec.type){
					case 'move': {
						if(rec.duration == 0) continue;
						tp = 'Движение</td><td>' + ln_to_km(rec.length) + ', ' + rec.speed.toFixed(1) + ' км/ч'; break
					}
					case 'stop': {
						//var rdiv = $('div');
						//console.log(rdiv);
						if(rec.duration < 5*60) tp = 'Остановка';
						else tp = 'Стоянка';
						adrlist.push({pos: rec.start.pos, id: ad_id, stop: false});

						tp += '</td><td id="' + ad_id + '" title="Дождитесь окончания обновления">' + rec.start.pos;
						break
					}
					default: {tp = 'Неизвестное событие (' + rec.type + ')'}
				}

				var events = '';

				for(var j in rec.events){
					log('Event: ', j, rec.events[j]);
					switch(j){
						case 'path_break': {
							events += '<span class="ui-icon ui-icon-alert" style="float:right;" title="Разрыв или повреждение трека. Данные отчета могут быть не точными." value="'+rec.events[j]+'"></span>';
							break
						}
					}
				}

				if(cur_date != rec.start.time.slice(0,6)+'000000'){
					cur_date = rec.start.time.slice(0,6)+'000000';
					tbody.append( '<tr><td colspan="4" style="padding-top: 8px; padding-bottom: 8px; font-weight: bold;">' + dt_to_date(cur_date) + '</td></tr>');
				}
					
				tbody.append( "<tr>" +
					//"<td>" + dt_to_date(rec.start.time) + "</td>" + 
					'<td>' +
					'	<!--button class="ctl" style="float: left;"><span class="ui-icon ui-icon-cancel" title="Убрать из отчета информацию о движении"></span></button>' +
					'	<button class="ctl" style="float: left;"><span class="ui-icon ui-icon-locked" title="Оставить в отчете только информацию о движении"></span></button-->' +
					'	<!--button class="ctl" style="float: left;"><span class="ui-icon ui-icon-zoomin" title="Показать этот путь на карте" onclick="showMap(' + rec.start.pos + ',\'Стоянка ' + td_to_hms(rec.duration) + ' с ' + dt_to_time(rec.start.time) + ' по ' + dt_to_time(rec.stop.time) + '\', ' + rec.start.time + ');"></span></button-->' +
					'	<button class="ctl" style="float: left;"><span class="ui-icon ui-icon-zoomin" title="Показать на карте" onclick="showMap2(\'' + rec.start.time + '\',\'' + rec.stop.time + '\', \''+rec.type+'\');"></span></button>' +
					tp + events + "</td>" + 
					'<td>' + dt_to_time(rec.start.time) + ' - ' + dt_to_time(rec.stop.time) + "</td>" +
					'<td>' + /*td_to_hms(rec.duration) + */'' + td_to_time(rec.duration) + "</td>" +
				"</tr>" );
					
			}
			$(tbody).children('tr').click(function(){
				//log(this);
				$(this).css('font-weight', 'bold');
			});
			//log(adrlist);
			for(i in adrlist){
				if(i==0){
					$(".control").hide();
				}
				//console.log(i);
				(function(i) {
					adrlist[i].cb = setTimeout(function(){getGeocode(adrlist, i, 50)}, 1000);
					//getGeocode(adrlist, i, 10);
				})(i);
			}

			$('.ctl').button(/*{ disabled: true }*/);
		}
	});

}
function purgeReport() {
	$('#report tbody').empty();
}

/*
var Image_Start = new google.maps.MarkerImage(
	'/images/marker-start.png?v=1',
	new google.maps.Size(24, 20),
	new google.maps.Point(0, 0),
	new google.maps.Point(11, 19)
);

var Image_Finish = new google.maps.MarkerImage(
	'/images/marker-finish.png?v=1',
	new google.maps.Size(28, 20),
	new google.maps.Point(0, 0),
	new google.maps.Point(14, 19)
);

var Image_Stop = new google.maps.MarkerImage(
	'/images/marker-stop.png',
	new google.maps.Size(16, 20),
	new google.maps.Point(0, 0),
	new google.maps.Point(7, 19)
);
*/

function showMap2(from, to, type) {
	var map_div = $('#map_preview');
	if(map_div.length==0){
		div = $('body')
		.append('<div id="map_overlay" class="ui-widget-overlay"></div>')
		.append('<div id="map_preview" style="">Загрузка карты, ожидайте...</div>');
		var map_div = $('#map_preview');
		$('#map_preview')
		.append('<div id="rmap"></div>')
		.append('<div id="map_close" style="position: absolute; top: -10px; left: 50%; margin-left: -20px;"><span class="ui-icon ui-icon-close"></span></div>');

		$('#map_close').button().click(function(){
			$('#rmap').gmap('destroy');
			$('#map_preview').remove();
			$('#map_overlay').remove();
		});

		url = '/api/geo/get?skey='+config.skey+'&from='+from+'&to='+to+'&options=nosubbounds';
		$.getJSON(url, function (data) {
			//$("#progress").html("Обрабатываем...");
			//log("getJSON parce");
			if (data.answer && data.points.length > 0) {
				//ParcePath(data);
				log('ShowMap2:', data);

				var $map = $('#rmap').gmap({
					pos: new google.maps.LatLng(data.points[0][1], data.points[0][2]),
					zoom: 15,
					marker: 'center',
					//markertitme: title
				});
				var map = $($map).gmap('option', 'map');
				//console.log('Map: ', map);

				if(type == 'move'){
					map.fitBounds(new google.maps.LatLngBounds(
						new google.maps.LatLng(data.bounds.sw[0], data.bounds.sw[1]),
						new google.maps.LatLng(data.bounds.ne[0], data.bounds.ne[1])
					));

					var path = [];
					for(var i in data.points){
						var l = new google.maps.LatLng(data.points[i][1], data.points[i][2], false);
						path.push(l);
					}

					var flightPath = new google.maps.Polyline({
						//path: flightPlanCoordinates,
						map: map,
						path: path,
						strokeColor: config.ui.trackcolor || '#dc00dc',
						strokeOpacity: 1.0,
						strokeWeight: 3
					});

					// Маркеры начала и конца
					var marker_start = new google.maps.Marker({
						position: new google.maps.LatLng(path[0].lat(), path[0].lng()),
						map: map,
						title: 'Старт: ' + dt_to_datetime(data.points[0][0]),
							//tp + td_to_hms(dt) +
							//'\n' + dt_to_datetime(data.points[data.stops[i].i][0]) + '...' + dt_to_datetime(data.points[data.stops[i].s][0]),
							//'\n' + dstop + '...' + dstart,
						icon: $.gmap.images['start'],
			        		draggable: false
						//zIndex: -1000
					});
					var marker_finish = new google.maps.Marker({
						position: new google.maps.LatLng(path[path.length-1].lat(), path[path.length-1].lng()),
						map: map,
						title: 'Финиш: ' + dt_to_datetime(data.points[path.length-1][0]),
							//tp + td_to_hms(dt) +
							//'\n' + dt_to_datetime(data.points[data.stops[i].i][0]) + '...' + dt_to_datetime(data.points[data.stops[i].s][0]),
							//'\n' + dstop + '...' + dstart,
						icon: $.gmap.images['finish'],
			        		draggable: false
						//zIndex: -1000
					});
					//log('Marker: ', marker_start, marker_finish, path);
				} else {
					// Маркер стоянки
					var marker_stop = new google.maps.Marker({
						position: new google.maps.LatLng(data.points[0][1], data.points[0][2]),
						map: map,
						title: 'Стoянка: ' +
							'\n' + dt_to_datetime(data.points[0][0]) + '...' + dt_to_datetime(data.points[data.points.length-1][0]),
							//tp + td_to_hms(dt) +
							//'\n' + dt_to_datetime(data.points[data.stops[i].i][0]) + '...' + dt_to_datetime(data.points[data.stops[i].s][0]),
							//'\n' + dstop + '...' + dstart,
						icon: $.gmap.images['stop'],//Image_Stop,
			        		draggable: false
						//zIndex: -1000
					});
				}
				//flightPath.setMap(map);
			}
		});

		/*
		var mapOptions = {
			center: new google.maps.LatLng(48.5000, 34.599),
			mapTypeId: google.maps.MapTypeId.ROADMAP,
			//mapTypeControl: false,
			disableDoubleClickZoom: true,
			draggableCursor: "default",
			zoom: 10,
		};
     
		map = new google.maps.Map(document.getElementById("map"), mapOptions);
		*/
	}
	//log(map_div);
}

window['showMap2'] = showMap2;

if(0){
	function showMap(lat, lon, title) {
		//$(this).css('border','2px solid green');
		//map = $("#map_div");
		//map.css({'left': me.pageX+10, 'top': me.pageY+10});
		var map_div = $('#map_preview');
		if(map_div.length==0){
			div = $('body')
			.append('<div id="map_overlay" class="ui-widget-overlay"></div>')
			.append('<div id="map_preview" style="">Ошибка отображения карты</div>');
			var map_div = $('#map_preview');
			$('#map_preview')
			.append('<div id="rmap"></div>')
			.append('<div id="map_close" style="position: absolute; top: -10px; left: 50%; margin-left: -20px;"><span class="ui-icon ui-icon-close"></span></div>');

			console.log();
			var $map = $('#rmap').gmap({
				pos: new google.maps.LatLng(lat, lon),
				zoom: 15,
				marker: 'center',
				markertitme: title
			});
			var map = $($map).gmap('option', 'map');

			$('#map_close').button().click(function(){
				$('#map_preview').gmap('destroy');
				$('#map_preview').remove();
				$('#map_overlay').remove();
			});

			/*
			var mapOptions = {
				center: new google.maps.LatLng(48.5000, 34.599),
				mapTypeId: google.maps.MapTypeId.ROADMAP,
				//mapTypeControl: false,
				disableDoubleClickZoom: true,
				draggableCursor: "default",
				zoom: 10,
			};
     
			map = new google.maps.Map(document.getElementById("map"), mapOptions);
			*/
		}
		log(map_div);
	} 
}

function Report_Make_SysList(list){
	list.empty();
	for(var i in config.systems){
		var s = config.systems[i];
		list.append('<option imei="'+s.imei+'" value="'+s.skey+'">'+s.desc+'</option>');
	}
}

$(document).ready(function() {

	geocoder = new google.maps.Geocoder();
	$("#nav_reports").button("option", "disabled", true);

	$("#button_report_type_div").buttonset();

	$("#button_report_type_day").bind('change', function(){
		$('#report_div_type_interval').hide('slow');
		$('#report_div_type_day').show('slow');
		log('Boo');
	});
	$("#button_report_type_interval").bind('change', function(){
		$('#report_div_type_day').hide('slow');
		$('#report_div_type_interval').show('slow');
		log('Boo');
	});


	$('.control').button();

	$.datepicker.setDefaults( $.datepicker.regional[ "ru" ] );
	/*$( "#datepicker" ).datepicker($.datepicker.regional[ "ru" ], {altField: "#alternate",
		altFormat: "DD, d MM, yy"});*/

/*
	$('#indatepicker').datepicker({altField: "#alternate",
		altFormat: "DD, d MM, yy",
		onSelect: function(dateText, inst) {
			//console.log(inst);
			log(dateText);
			var start = date_to_url(dateText) + '000000'; //inst.currentYear, inst.currentMonth, inst.currentDay, '000000');
			var stop = date_to_url(dateText) + '235959'; //inst.currentYear, inst.currentMonth, inst.currentDay, '235959');
			config.skey = $('#rep_syslist').attr('value');
			genReport($('#rep_syslist').attr('value'), start, stop);
			//console.log(dateText);
			//console.log(inst);
		}
	});
	$('#control_day').click(function(){
		//alert('bu');
	});
*/

	$('#total tbody tr td').bind('click', function(me){
		log(me);
		//showMap();
	});

	log('Загрузка закладки. Отчеты.');

if(0){
	var list = $('#rep_syslist');
	Report_Make_SysList(list);
	//}
	//updateLogList();
	config.updater.add('changedesc', function(msg) {
		log('LOGS: Update descriptions');
		//updateLogList();
		$(list).find('option[value="' + msg.data.skey + '"]').html(msg.data.desc);
		//console.log(l);
	});
	config.updater.add('changeslist', function(msg) {
		Report_Make_SysList(list);
	});
}
	//$('#log_syslist').bind('change', function(){
	/*
	list.bind('change', function(){
		config.skey = $(this).attr('value');
		//Report_Make_SysList(list);
	});
	*/


/*
		onSelect: function(dateText, inst) {
			//console.log(inst);
			log(dateText);
			var start = date_to_url(dateText) + '000000'; //inst.currentYear, inst.currentMonth, inst.currentDay, '000000');
			var stop = date_to_url(dateText) + '235959'; //inst.currentYear, inst.currentMonth, inst.currentDay, '235959');
			config.skey = $('#rep_syslist').attr('value');
			genReport($('#rep_syslist').attr('value'), start, stop);
			//console.log(dateText);
			//console.log(inst);
		}
*/

	$('#report_date_by_day').datepicker({
		altField: "#report_dlg_byday_alternate",
			altFormat: "DD, d MM, yy"
	});

	$('#report_dlg_byday').dialog({
		modal: true,
		autoOpen: false,
		buttons:{
			'Отмена': function(){
				$(this).dialog("close");
			},
			'Построить отчет': function(){
				$(this).dialog("close");
				var dt = $('#report_date_by_day').datepicker('getDate');
				var start = $.datepicker.formatDate('ymmdd000000', dt);
				var stop = $.datepicker.formatDate('ymmdd235959', dt);
				config.skey = $('#report_dlg_byday_syslist').val();

				genReport(config.skey, start, stop, $.datepicker.formatDate('DD, d MM, yy', dt));

				/*
				var start = date_to_url(dateText) + '000000'; //inst.currentYear, inst.currentMonth, inst.currentDay, '000000');
				var stop = date_to_url(dateText) + '235959'; //inst.currentYear, inst.currentMonth, inst.currentDay, '235959');
				config.skey = $('#rep_syslist').attr('value');
				genReport($('#rep_syslist').attr('value'), start, stop);
				*/
			}
		},
		open: function(event, ui){
			log('Dialog open:', this, ui, event);
			var list = $('#report_dlg_byday_syslist');
			list.empty();
			for(var i in config.systems){
				var s = config.systems[i];
				list.append('<option imei="'+s.imei+'" value="'+s.skey+'"'+(s.skey==config.skey?' selected':'')+'>'+s.desc+'</option>');
			}
		}
	});

	var dates = $('#report_date_by_int_from, #report_date_by_int_to').datepicker({
		altFormat: "DD, d MM, yy",
		onSelect: function( selectedDate ) {
			var option = this.id == "report_date_by_int_from" ? "minDate" : "maxDate",
				instance = $( this ).data( "datepicker" );
				date = $.datepicker.parseDate(
					instance.settings.dateFormat ||
					$.datepicker._defaults.dateFormat,
					selectedDate, instance.settings );
			dates.not( this ).datepicker( "option", option, date );
		}
	});
	//log('Dates: ', dates);
	$('#report_date_by_int_from').datepicker('option', 'altField', '#report_dlg_byint_alternate_from');
	$('#report_date_by_int_to').datepicker('option', 'altField', '#report_dlg_byint_alternate_to');

	/*
	$('#report_dlg_byint_time_from_tp').timepicker({
		altField: '#report_dlg_byint_time_from',
		hourText: 'Часы',
		minuteText: 'Минуты',
    		amPmText: ['', ''],
		showPeriod: false,
		showLeadingZero: true,
		defaultTime: '00:00'
	});

	$('#report_dlg_byint_time_to_tp').timepicker({
		altField: '#report_dlg_byint_time_to',
		hourText: 'Часы',
		minuteText: 'Минуты',
    		amPmText: ['', ''],
		showPeriod: false,
		showLeadingZero: true,
		defaultTime: '23:59'
	});
	*/

	$('#report_dlg_byint').dialog({
		modal: true,
		autoOpen: false,
		width: 600,
		buttons:{
			'Отмена': function(){
				$(this).dialog("close");
			},
			'Построить отчет': function(){
				var dt_from = $('#report_date_by_int_from').datepicker('getDate');
				var dt_to = $('#report_date_by_int_to').datepicker('getDate');
				var time_from = $('#report_dlg_byint_time_from').val();
				var time_to = $('#report_dlg_byint_time_to').val();
				log(time_from, /^\d\d:\d\d:\d\d$/.test(time_from), time_to, /^\d\d:\d\d:\d\d$/.test(time_to));
				if(!(/^\d\d:\d\d:\d\d$/.test(time_from)) || !(/^\d\d:\d\d:\d\d$/.test(time_to))){
					alert('Время должно задаваться в формате ЧЧ:MM:CC');
					return
				}
				$(this).dialog("close");

				var start = $.datepicker.formatDate('ymmdd', dt_from) + time_from.replace(/:/g,'');
				var stop = $.datepicker.formatDate('ymmdd', dt_to) + time_to.replace(/:/g,'');
				config.skey = $('#report_dlg_byint_syslist').val();


				genReport(config.skey, start, stop,
					' интервал с ' + $.datepicker.formatDate('DD, d MM, yy ', dt_from) + $('#report_dlg_byint_time_from').val() +
					' по ' + $.datepicker.formatDate('DD, d MM, yy ', dt_to) + $('#report_dlg_byint_time_to').val()
				);

				/*
				var start = date_to_url(dateText) + '000000'; //inst.currentYear, inst.currentMonth, inst.currentDay, '000000');
				var stop = date_to_url(dateText) + '235959'; //inst.currentYear, inst.currentMonth, inst.currentDay, '235959');
				config.skey = $('#rep_syslist').attr('value');
				genReport($('#rep_syslist').attr('value'), start, stop);
				*/
			}
		},
		open: function(event, ui){
			log('Dialog open:', this, ui, event);
			var list = $('#report_dlg_byint_syslist');
			list.empty();
			for(var i in config.systems){
				var s = config.systems[i];
				list.append('<option imei="'+s.imei+'" value="'+s.skey+'"'+(s.skey==config.skey?' selected':'')+'>'+s.desc+'</option>');
			}
		}
	});

	$('#report_btn_do_by_day').button({
		icons: {
			primary: "ui-icon-note"
		}})
		.click(function(){$('#report_dlg_byday').dialog('open')})
		.next().button({
		icons: {
			primary: "ui-icon-note"
		}})
		.click(function(){$('#report_dlg_byint').dialog('open')});


});

})();
