function dt_to_datetime(dt) {
	return dt[4]+dt[5] + '/' + dt[2]+dt[3] + '/20' + dt[0]+dt[1] + ' ' + dt[6]+dt[7] + ':' + dt[8]+dt[9] + ':' + dt[10]+dt[11];
}

function dt_to_date(dt) {
	return dt[4]+dt[5] + '/' + dt[2]+dt[3] + '/20' + dt[0]+dt[1];
}

function dt_to_time(dt) {
	return dt[6]+dt[7] + ':' + dt[8]+dt[9] + ':' + dt[10]+dt[11];
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

function ln_to_km(l) {
	var k = (l - (l % 1000)) / 1000;
	var m = l % 1000;
	if(k) return k + ' км ' + m + ' м';
	else return m + ' м';
}

function geocode_to_addr(results) {
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
