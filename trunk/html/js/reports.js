
	var geocoder;

	var adrlist = [];

	function getGeocode(adrlist, i, recur) {
		//console.log(adrlist[i]);
		log('geoget at ' + i);
		if(adrlist[i].stop) log('stop: ' + i);

		geocoder.geocode({'latLng': new google.maps.LatLng(adrlist[i].pos[0], adrlist[i].pos[1]) }, function(results, status) {
			if(adrlist[i].stop) {log('stop2: ' + i); return;}
    			if (status == google.maps.GeocoderStatus.OK) {
				var address = geocode_to_addr(results);
				$('#'+adrlist[i].id).html(address);
				delete adrlist[i];
				//console.log(adrlist.some());
				var empty = true;
				for(var j in adrlist) {empty = false; break;}
				if(empty == true){
					$(".control").show();
				}

			} else {
				if(recur) {
					adrlist[i].cb = setTimeout(function(){getGeocode(adrlist, i, recur-1)}, 5000);
				} else {
					log('Error geocoding at ' + i + ' with ');
				}
			}
		});

	}

	function genReport(skey, start, stop) {
		//$(".control").hide();
		for(var i in adrlist) { clearInterval(adrlist[i].cb); adrlist[i].stop = true; }
		$( "#report tbody" ).empty();

		url = "/api/report/get?skey="+skey+"&from="+start+"&to="+stop;
		$.getJSON(url, function (data) {
			//$("#progress").html("Обрабатываем...");
			log("getJSON parce");
			if (data.answer == 'ok') {
				//ParcePath(data);
				log("Show report...");

				$("#report_total_dist").html(ln_to_km(data.summary.length));
				$("#report_total_movetime").html(td_to_hms(data.summary.movetime));

				var tbody = $( "#report tbody" );
				//console.log(tbody);
				adrlist = [];
				for(var i in data.report){
					var ad_id = 'ad_' + i;
					var rec = data.report[i];
					var tp;

					switch(rec.type){
						case 'move': {tp = 'Движение</td><td>' + ln_to_km(rec.length); break}
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
					
					tbody.append( "<tr>" +
						"<td>" + dt_to_date(start) + "</td>" + 
						"<td>" +
						'	<!--button class="ctl" style="float: left;"><span class="ui-icon ui-icon-cancel" title="Убрать из отчета информацию о движении"></span></button>' +
						'	<button class="ctl" style="float: left;"><span class="ui-icon ui-icon-locked" title="Оставить в отчете только информацию о движении"></span></button-->' +
						'	<button class="ctl" style="float: left;"><span class="ui-icon ui-icon-zoomin" title="Показать этот путь на карте" onclick="showMap(' + rec.start.pos + ',\'Стоянка ' + td_to_hms(rec.duration) + ' с ' + dt_to_time(rec.start.time) + ' по ' + dt_to_time(rec.stop.time) + '\');"></span></button>' +
						tp + "</td>" + 
						'<td>' + dt_to_time(rec.start.time) + ' - ' + dt_to_time(rec.stop.time) + "</td>" +
						'<td>' + /*td_to_hms(rec.duration) + */'' + td_to_time(rec.duration) + "</td>" +
					"</tr>" );
					
				}
				log(adrlist);
				for(i in adrlist){
					if(i==0){
						$(".control").hide();
					}
					//console.log(i);
					(function(i) {
						adrlist[i].cb = setTimeout(function(){getGeocode(adrlist, i, 10)}, 1000);
						//getGeocode(adrlist, i, 10);
					})(i);
				}

				$('.ctl').button(/*{ disabled: true }*/);
			}
		});

	}
	function purgeReport() {
		$( "#report tbody" ).empty();
	}

	function showMap(lat, lon, title) {
		//$(this).css('border','2px solid green');
		//map = $("#map_div");
		//map.css({'left': me.pageX+10, 'top': me.pageY+10});
		var map_div = $('#map_preview');
		if(map_div.length==0){
			div = $('body')
			.append('<div id="map_overlay" class="ui-widget-overlay"></div>')
			.append('<div id="map_preview" style="">Тут будет карта</div>');
			var map_div = $('#map_preview');
			$('#map_preview')
			.append('<div id="rmap"></div>')
			.append('<div id="map_close" style="position: absolute; top: -10px; left: 50%; margin-left: -20px;"><span class="ui-icon ui-icon-close"></span></div>');
			$('#rmap').gmap({
				pos: new google.maps.LatLng(lat, lon),
				zoom: 15,
				marker: 'center',
				markertitme: title
			});
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


	$(function(){
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
		$('#indatepicker').datepicker({altField: "#alternate",
			altFormat: "DD, d MM, yy",
			onSelect: function(dateText, inst) {
				//console.log(inst);
				log(dateText);
				var start = date_to_url(dateText) + '000000'; //inst.currentYear, inst.currentMonth, inst.currentDay, '000000');
				var stop = date_to_url(dateText) + '235959'; //inst.currentYear, inst.currentMonth, inst.currentDay, '235959');
				genReport($('#rep_syslist').attr('value'), start, stop);
				//console.log(dateText);
				//console.log(inst);
			}
		});

		$('#control_day').click(function(){
			//alert('bu');
		});

		$('#total tbody tr td').bind('click', function(me){
			log(me);
			//showMap();
		});
	});

	function Report_Make_SysList(list){
		list.empty();
		for(var i in config.systems){
			var s = config.systems[i];
			list.append('<option imei="'+s.imei+'" value="'+s.skey+'">'+s.desc+'</option>');
		}
	}

	$(document).ready(function() {
		log('Загрузка закладки. Отчеты.');

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

		//$('#log_syslist').bind('change', function(){
		/*
		list.bind('change', function(){
			config.skey = $(this).attr('value');
			//Report_Make_SysList(list);
		});
		*/


	});
