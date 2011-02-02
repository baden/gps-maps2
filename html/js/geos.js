/*
*/
(function(){

$(document).ready(function() {

	var tbody = $('#geos_body table tbody');
	var skey;

	function td(value){
		var res = '';
		$.each(value, function(i, v){
			res += '<td>' + v + '</td>'
		});
		return res;
	}

	function genReport(){
		log('GEOS: Update report');
		skey = $('#geos_syslist').val();

		var type = $('#geos_type_last').attr('checked');

		var date;
		if(type){
			date = $.datepicker.formatDate('ymmdd', new Date());
		} else {
			date = $.datepicker.formatDate('ymmdd', $('#geos_datepicker').datepicker('getDate'));
			if(date == '') return;
		}

		$.getJSON('/api/geo/report', {skey: skey, from: date+'000000', to: date+'235959'}, function (data) {
			if (data.answer && data.answer == 'ok') {
				tbody.empty();
				for(var i in data.points){
					var p = data.points[i];
					var row = '<tr>';
					row += td([p[0], p[1].toFixed(5), p[2].toFixed(5), p[3], p[4].toFixed(1), p[5].toFixed(2), p[6].toFixed(1)]);
					row += '</tr>';
					tbody.append(row);
				}
			}
		});
	}

	config.updater.add('geo_change', function(msg) {
		log('GEOS: geo_change: ', msg.data);
		if(skey == msg.data.skey) {
			if($('#geos_type_last').attr('checked')) genReport();
		}
	});

	config.syslist({
		id: 'geos_syslist',
		change: function(){
			genReport();
		}
	});

	genReport();

	$('#geos_viewtype').buttonset({
	}).change(function(){
		//log('geo: buttonset_change');
		genReport();
	});
	$('#geos_datepicker').datepicker();

});

})();
