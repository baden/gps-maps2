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

function td_to_time(d) {
	var minutes = (d - (d % 60)) / 60;
	var hours = (minutes - (minutes % 60)) / 60;
	minutes = minutes % 60;
	var seconds = d % 60;
	var r = '';
	if(hours==0) r+='00:';
	else if(hours<10) r+='0'+hours+':';
	else r+=hours+':';
	if(minutes==0) r+='00:';
	else if(minutes<10) r+='0'+minutes+':';
	else r+=minutes+':';
	if(seconds==0) r+='00:';
	else if(seconds<10) r+='0'+seconds+':';
	else r+=seconds+':';
	return r;
}

function date_to_url(ymd) {
	return ymd.slice(8,10) + ymd.slice(3,5) + ymd.slice(0,2);
}


function ln_to_km(l) {
//	var k = parseInt(l, 10);
//	var m = Math.round((l-parseInt(l, 10))*1000);
//	if(k) return Math.round(l*10)/10 + ' км (' + k + ' км ' + m + ' м)';
//	else return Math.round(l*10)/10 + ' км (' + m + ' м)';

	if(l>=1.0) return Math.round(l*10)/10 + ' км';
	else return Math.round(l*1000) + ' м';

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
