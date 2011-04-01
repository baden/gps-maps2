// usage: log('inside coolFunc',this,arguments);
// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function(){
  log.history = log.history || [];   // store logs to an array for reference
  log.history.push(arguments);
  if(this.console){
    console.log( Array.prototype.slice.call(arguments) );
  }
};



// catch all document.write() calls
(function(doc){
  var write = doc.write;
  doc.write = function(q){ 
    log('document.write(): ',arguments); 
    if (/docwriteregexwhitelist/.test(q)) write.apply(doc,arguments);  
  };
})(document);

function f2d(n) {
  if (n < 10) {
    return '0' + n;
  }
  return String(n);
};

function dt_to_Date(dt) {
	var date = new Date(Date.UTC(
		parseInt('20'+dt[0]+dt[1], 10),
		parseInt(dt[2]+dt[3], 10)-1,
		parseInt(dt[4]+dt[5], 10),
		parseInt(dt[6]+dt[7], 10),
		parseInt(dt[8]+dt[9], 10),
		parseInt(dt[10]+dt[11], 10)
	));
	return date;
}

function dt_to_date(dt) {
	var date = dt_to_Date(dt);
	return f2d(date.getDate()) + '/' + f2d(date.getMonth()+1) + '/' + date.getFullYear();
}

function dt_to_time(dt) {
	var date = dt_to_Date(dt);
	return date.toLocaleTimeString();
}


function dt_to_datetime(dt) {
	return dt_to_date(dt) + ' ' + dt_to_time(dt);
/*
	//log('dt_to_datetime dt:', dt);
	var date = new Date(Date.UTC(
		parseInt('20'+dt[0]+dt[1], 10),
		parseInt(dt[2]+dt[3], 10)-1,
		parseInt(dt[4]+dt[5], 10),
		parseInt(dt[6]+dt[7], 10),
		parseInt(dt[8]+dt[9], 10),
		parseInt(dt[10]+dt[11], 10)
	));
	//log('dt_to_datetime dt:', dt, 'date: ', date);
		
	return f2d(date.getDate()) + '/' + f2d(date.getMonth()+1) + '/' + date.getFullYear() + ' ' + date.toLocaleTimeString();
	//return dt[4]+dt[5] + '/' + dt[2]+dt[3] + '/20' + dt[0]+dt[1] + ' ' + dt[6]+dt[7] + ':' + dt[8]+dt[9] + ':' + dt[10]+dt[11];
*/
}


function td_to_hms(d) {
	var minutes = (d - (d % 60)) / 60;
	var hours = (minutes - (minutes % 60)) / 60;
	minutes = minutes % 60;
	var seconds = d % 60;
	if(hours) return hours + ' ч ' + minutes + ' мин ' + seconds + ' сек';
	else if(minutes) return minutes + ' мин ' + seconds + ' сек';
	else return seconds + ' сек';
}

function td_to_time(d) {
	var minutes = (d - (d % 60)) / 60;
	var hours = (minutes - (minutes % 60)) / 60;
	minutes = minutes % 60;
	var seconds = d % 60;
	var r = '';
	if(hours<10) r+='0'+hours+':'; else r+=hours+':';
	if(minutes<10) r+='0'+minutes+':'; else r+=minutes+':';
	if(seconds<10) r+='0'+seconds; else r+=seconds;
	return r;
}

//function date_to_url(ymd) {
//	return ymd.slice(8,10) + ymd.slice(3,5) + ymd.slice(0,2);
//}

function Date_to_daystart(d) {
	var date = new Date(d);
	date.setHours(0);
	date.setMinutes(0);
	date.setSeconds(0);
	return date;
}

function Date_to_daystop(d) {
	var date = new Date(d);
	date.setHours(23);
	date.setMinutes(59);
	date.setSeconds(59);
	return date;
}

function Date_to_url(d) {
	return f2d(d.getUTCFullYear()-2000) + f2d(d.getUTCMonth()+1) + f2d(d.getUTCDate()) + 
		f2d(d.getUTCHours()) + f2d(d.getUTCMinutes()) + f2d(d.getUTCSeconds());
}

function ln_to_km(l) {
//	var k = parseInt(l, 10);
//	var m = Math.round((l-parseInt(l, 10))*1000);
//	if(k) return Math.round(l*10)/10 + ' км (' + k + ' км ' + m + ' м)';
//	else return Math.round(l*10)/10 + ' км (' + m + ' м)';

	if(l>=1.0) return Math.round(l*10)/10 + ' км';
	else return Math.round(l*1000) + ' м';

}

/*
	Выделение компонентов адреса
*/
function geocode_to_addr(results) {
	var comp = {
		street_address: '',
		route: '',
		locality: '',
		sublocality: '',
		administrative_area_level_2: '',
		administrative_area_level_1: '',
		country: ''
	};
	// 'country' - страна
	// 'administrative_area_level_1' - область
	// 'administrative_area_level_2' - район (?)
	// 'sublocality' - район (?)
	// 'locality' - населенный пункт
	// 'street_address' - Дом
	// 'route' - трасса или улица при отсутствии street_address

	for(var i in results){
		for(var j in results[i].address_components){
			var c = results[i].address_components[j];
			comp[c.types[0]] = c.long_name;
		}
	}

	return '' +
		comp.country + ', ' +
		comp.administrative_area_level_1 + ', ' +
		((comp.locality == '')?(((comp.sublocality != '')?comp.sublocality:comp.administrative_area_level_2) + ' район, '):'') +
		((comp.locality != '')?(comp.locality+', '):'') +
		comp.route +
		((comp.street_address != '')?(', ' + comp.street_address):'');
}


function geocode_to_addr2(results) {

	for(var i in results){
		var r = results[i];
//		console.log(r.types);
/*
Приоритет выдачи адреса:
'street_address'	Точность до улицы
'sublocality'		Точность до района
'locality'		Точность до города
results[1]		Как повезет :)
*/
		if((r.types.indexOf('street_address') != -1) ||
		   (r.types.indexOf('sublocality') != -1) ||
		   (r.types.indexOf('locality') != -1))
		{
			return r.formatted_address;
			//break;
		}
	}
	if(results[1]){
		return results[1].formatted_address;
	} else if(results[0]) {
		return results[0].formatted_address;
	} else {
		return 'Адрес неизвестен';
	}
	return 'Ошибка';
}


var config = config || {};

// Система автообновления
config.updater = {}
config.updater.queue = {};

config.updater.add = function(msg, foo){
	config.updater.queue[msg] = config.updater.queue[msg] || [];
	config.updater.queue[msg].push(foo);
}

config.updater.process = function(msg){
	/*
	if(config.updater.queue[msg.msg]){
		for(var i in config.updater.queue[msg.msg]){
			config.updater.queue[msg.msg][i](msg);
		}
	}
	*/

	if(config.updater.queue[msg.msg]){
		for(var i in config.updater.queue[msg.msg]){
			config.updater.queue[msg.msg][i](msg);
		}
	}
	if(config.updater.queue['*']){
			for(var i in config.updater.queue['*']){
				config.updater.queue['*'][i](msg);
			}
		}

}

config.updater.add('*', function(msg){
	//console.log("goog.appengine.Channel: onMessage");
	//console.log(msg);
	//log('goog.appengine.Channel: onMessage:', msg);
	//connected = true;
	if(config.admin){
		if(msg.msg) message('Получено сообщени об обновлении:<b>' + msg.msg + '</b>');
	}
});

config.updater.tabs = [];

config.updater.add('changedesc', function(msg) {
	//log('Обработчик события для обновления списка config.systems', msg);
	for(var i in config.systems){
		if(config.systems[i].skey == msg.data.skey){
			config.systems[i].desc = msg.data.desc;
		}
	}
	if(msg.data.skey in config.sysbykey){
		config.sysbykey[msg.data.skey].desc = msg.data.desc;
	}
	//log('CONFIG==', config);
});

config.syslist = function(options){
	var list = $('#'+options.id);

	function Make_SysList(){
		list.empty();
		for(var i in config.systems){
			var s = config.systems[i];
			//list.append('<option imei="'+s.imei+'" value="'+s.skey+'"'+(config.skey==s.skey?' selected':'')+'>'+s.desc+'</option>');
			list.append('<option imei="'+s.imei+'" value="'+s.skey+'">'+s.desc+'</option>');
		}
	}

	Make_SysList();

	$(list).bind({
		/*click: function(ev){
			Make_SysList();
			log('click');
			},*/
		change: options.change
	});

	config.updater.add('changeslist', function(msg) {
		log('config.syslist: Update system list');
		Make_SysList();
	});

	config.updater.add('changedesc', function(msg) {
		$(list).children('option[value="'+msg.data.skey+'"]').html(msg.data.desc);
	});

}

function UpdateAccountSystemList() {
	if(config && config.akey)
	$.getJSON('/api/info?akey='+config.akey, function (data) {
		if(data){
			log('UpdateAccountSystemList data:', data);
			//var config = config || {};
			config.systems = [];
			config.sysbykey = {};
			for(var i in data.info.account.systems){
				var s = data.info.account.systems[i];
				config.systems.push({
					'imei': s.imei,
					'skey': s.key,
					'desc': s.desc
				});
				config.sysbykey[s.key] = {imei: s.imei, desc: s.desc};
			}

			config.updater.process({msg: 'changeslist'});
		}
	});
}

UpdateAccountSystemList();

config.updater.add('change_slist', function(msg) {
	log('BASE: Update system list');
	UpdateAccountSystemList();
});


var alertcnt = 0;
var geocoder;
if('google' in window) geocoder = new google.maps.Geocoder();
//var sound;

config.updater.add('addlog', function(msg) {

	log('BASE: Alert message', msg);
	//UpdateAccountSystemList();
	if(msg.data['mtype'] != 'alarm') return;

	var messageBox = document.createElement('div');
	//messageBox.id = 'alarmmap_' + String(new Date().getTime());
	messageBox.className = 'alertmsg';
	messageBox.innerHTML = 'Система: <b>' + config.sysbykey[msg.data.skey].desc + '</b>';

	if (document.body.firstChild) document.body.insertBefore(messageBox, document.body.firstChild);
	else document.body.appendChild(messageBox);

	/*var sound = document.createElement('audio');
	//sound.attributes.add('source', 'sound/alarm.ogg');
	//sound.src = 'sound/alarm.ogg';
	sound.innerHTML = '<source src="sound/alarm.ogg"><source src="sound/alarm.mp3">';
	log('sound', sound);
	//sound.control
	messageBox.appendChild(sound);
*/
	/*
	if(!sound) sound = document.getElementById('sound_alarm');
	//sound.play();

	sound.pause();
        sound.currentTime = 0;
        sound.play();

	log('sound', sound);
	*/
	var sound = new Audio();
	sound.src = 'sound/alarm.' + (sound.canPlayType('audio/ogg') ? 'ogg' : sound.canPlayType('audio/mp3') ? 'mp3' : 'wav');
	sound.play();
	console.dir(sound);

	var addres = document.createElement('div');
	messageBox.appendChild(addres);

	var dmap = document.createElement('div');
	dmap.id = 'alarmmap_' + String(new Date().getTime());
	dmap.className = 'alertmap';
	messageBox.appendChild(dmap);

	if('google' in window){
		var position = new google.maps.LatLng(msg.data.data.lat, msg.data.data.lon);
		var $map = $(dmap).gmap({
			pos: position,
			zoom: 15,
			marker: 'center',
			//markertitme: 'aaa'
		});

		//var map = $('#map').gmap('option', 'getMap');
		var map = $($map).gmap('option', 'map');

		var marker_stop = new google.maps.Marker({
			position: position,
			map: map,
			title: 'Стoянка: ',// +
			//	'\n' + dt_to_datetime(data.points[0][0]) + '...' + dt_to_datetime(data.points[data.points.length-1][0]),
			icon: $.gmap.images['alarm'],//Image_Stop,
	       		draggable: false
			//zIndex: -1000
		});
		log('map is', map, 'marker is', marker_stop);
	} else {
		dmap.innerHTML = 'Сервер Google недоступен. Отображение карты невозможно.';
	}

	//$(
	//log('CreateMap:', map);
	if(geocoder) geocoder.geocode({'latLng': position}, function(results, status) {
	      if (status == google.maps.GeocoderStatus.OK) {
		var address = geocode_to_addr(results);

	  	//console.log(results);
	
		addres.innerHTML = 'Адрес: <b>' + address + '</b>';
		addres.title = 'Нажмите чтобы центровать на миникарте.';
		addres.style.cursor = 'pointer';
		$(addres).bind('click', function(event){
			map.panTo(position);
			//log('click');
		});

	      } else {
	        //alert("Geocoder failed due to: " + status);
	      }
	});


	//$(messageBox).dialog('open');
	alertcnt++;

	//var buttons = {};
	//if(config.map){
	//	buttons = 
	//}

	$(messageBox).dialog({
		title: '<span class="ui-icon ui-icon-alert" style="display:inline-block;"></span> <span style="color:red;">Внимание! Нажата тревожная кнопка.</span>',
		//hide: 'slide',
		//show: 'drop',
		//stack: false,
		resizable: false,
		modal: false,
		autoOpen: true,
		width: 630,
		height: 400,
		buttons:{
			'Центровать на большой карте': function(){
				$(this).dialog("close");

				//var handler = function() {
				//	log('The quick brown fox jumps over the lazy dog.');
				//};

				if($('#tabs').tabs( "option", "selected" ) != 0){
					$('#tabs').bind('tabsshow', function(event, ui) {
						log('binded tab show');
						config.map.panTo(position);
						config.map.setZoom(15);
						$('#tabs').unbind(event);
					});
					$('#tabs').tabs('select', 0);		// TBD! Если карта не открывалась еще то нужна задержка.
				} else {
					config.map.panTo(position);
					config.map.setZoom(15);
				}
			},
			'Закрыть': function(){
				$(this).dialog("close");
			}
		},
		open: function(event, ui) {
			var position = $(this).dialog( "option", "position" );
			log('position', position);
			//position.offset = {left: alertcnt * 10, top: alertcnt * 10};
			position.offset = '' + (alertcnt * 16) + ' ' + (alertcnt * 16);
			//position.offset.;
			$(this).dialog( "option", "position", position );
			//$(this).animate({
			//	backgroundColor: "#aa0000"
			//}, 200);
			//$(this).parent().effect('pulsate');
			//$(this).effect('pulsate');
			$(this).parent().css('border', '3px solid red');
			$(this).parent().children().first().children().first().effect('pulsate');
		},
		close: function(event, ui) {
			alertcnt--;
			if(alertcnt<0) alertcnt = 0;
		}
	});
});
