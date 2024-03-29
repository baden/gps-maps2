"use strict";
//012; //Восьмеричный литерал запрешен. Выбросит исключение SyntaxError в Strict Mode// usage: log('inside coolFunc',this,arguments);
//console.log('strict mode is not worked!');

// paulirish.com/2009/log-a-lightweight-wrapper-for-consolelog/
window.log = function(){
  log.history = log.history || [];   // store logs to an array for reference
  log.history.push(arguments);
//  if(this.console){
  if(window.console){
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

var f2d = function(n) {
  if (n < 10) {
    return '0' + n;
  }
  return String(n);
};

var dt_to_Date = function(dt) {
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

var dt_to_date = function (dt) {
	var date = dt_to_Date(dt);
	return f2d(date.getDate()) + '/' + f2d(date.getMonth()+1) + '/' + date.getFullYear();
}

var dt_to_time = function (dt) {
	var date = dt_to_Date(dt);
	return date.toLocaleTimeString();
}

var dt_to_datetime = function (dt) {
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

var Date_to_date = function(date) {
	return f2d(date.getDate()) + '/' + f2d(date.getMonth()+1) + '/' + date.getFullYear();
}

var Date_to_time = function (date) {
	return date.toLocaleTimeString();
}

var Date_to_datetime = function (date) {
	return Date_to_date(date) + ' ' + Date_to_time(date);
}


var td_to_hms = function (d) {
	var minutes = (d - (d % 60)) / 60;
	var hours = (minutes - (minutes % 60)) / 60;
	minutes = minutes % 60;
	var seconds = d % 60;
	if(hours) return hours + ' ч ' + minutes + ' мин ' + seconds + ' сек';
	else if(minutes) return minutes + ' мин ' + seconds + ' сек';
	else return seconds + ' сек';
}

var td_to_time = function (d) {
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

var Date_to_daystart = function (d) {
	var date = new Date(d);
	date.setHours(0);
	date.setMinutes(0);
	date.setSeconds(0);
	return date;
}

var Date_to_daystop = function (d) {
	var date = new Date(d);
	date.setHours(23);
	date.setMinutes(59);
	date.setSeconds(59);
	return date;
}

var Date_to_url = function (d) {
	return f2d(d.getUTCFullYear()-2000) + f2d(d.getUTCMonth()+1) + f2d(d.getUTCDate()) + 
		f2d(d.getUTCHours()) + f2d(d.getUTCMinutes()) + f2d(d.getUTCSeconds());
}

var ln_to_km = function (l) {
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
var geocode_to_addr = function (results) {
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
		((comp.street_number != '')?(', ' + comp.street_number):'');
}


var geocode_to_addr2 = function (results) {

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

	var Make_SysList = function(){
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

var UpdateAccountSystemList = function() {
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

