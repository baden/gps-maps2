﻿/*
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
			//date = $.datepicker.formatDate('ymmdd', new Date());
			date = new Date();
		} else {
			//date = $.datepicker.formatDate('ymmdd', $('#geos_datepicker').datepicker('getDate'));
			date = $('#geos_datepicker').datepicker('getDate');
			if(!date) return;
			log('date', date);
			//if(date == '') return;
		}

//		$.getJSON('/api/geo/report', {skey: skey, from: date+'000000', to: date+'235959'}, function (data) {
		$.getJSON('/api/geo/report', {skey: skey, from: Date_to_url(Date_to_daystart(date)), to: Date_to_url(Date_to_daystop(date))}, function (data) {
			if (data.answer && data.answer == 'ok') {

				var vdata = {
					vout: {
						data: new google.visualization.DataTable(),
						vmin: 1000, vmax: -1000, vsum: 0
					},
					vin: {
						data: new google.visualization.DataTable(),
						vmin: 1000, vmax: -1000, vsum: 0
					},
					speed: {
						data: new google.visualization.DataTable(),
						vmin: 1000, vmax: -1000, vsum: 0
					},
					sats: {
						data: new google.visualization.DataTable(),
						vmin: 1000, vmax: -1000, vsum: 0
					}
				};
				vdata.vout.data.addColumn('string', 'x');	// Часы
				vdata.vin.data.addColumn('string', 'x');	// Часы
				vdata.speed.data.addColumn('string', 'x');	// Часы
				vdata.sats.data.addColumn('string', 'x');	// Часы

			        vdata.vout.data.addColumn('number', 'Основное питание');
			        vdata.vin.data.addColumn('number', 'Резервное питание');
			        vdata.speed.data.addColumn('number', 'Скорость');
			        vdata.sats.data.addColumn('number', 'Спутники');

				var phm = '';
				var vcnt = 0;
				var p;

				var _slice=5, _tail='';
				/*if(data.points.length > 10000){
					_slice = 3;
					_tail = '00';
				} else */if(data.points.length > 200){
					_slice = 4;
					_tail = '0';
				} 

				function add_data(name, digits){
					var value = parseFloat((vdata[name].vsum/vcnt).toFixed(digits));
					vdata[name].data.addRow([dt_to_time(p[0]).slice(0,_slice)+_tail, value]);
					vdata[name].vsum = 0;
					vdata[name].vmin = Math.min(vdata[name].vmin, value);
					vdata[name].vmax = Math.max(vdata[name].vmax, value);
				}

				tbody.empty();
				//var progress = $( "#progressbar" );
				//progress.progressbar({value: 0});
				for(var i in data.points){
					//if(i%10 == 0){
					//	progress.progressbar({value: i*100/data.points.length});
					//}

					p = data.points[i];
					var row = '<tr>';
//					row += td([p[0], p[1].toFixed(5), p[2].toFixed(5), p[3], p[6].toFixed(1), p[4].toFixed(1), p[5].toFixed(2)]);
					row += td([dt_to_time(p[0]), p[1].toFixed(5), p[2].toFixed(5), p[3], p[6].toFixed(1), p[4].toFixed(1), p[5].toFixed(2)]);
					row += '</tr>';
					//tbody.append(row);
					tbody.prepend(row);

					vdata.vout.vsum += p[4];
					vdata.vin.vsum += p[5];
					vdata.speed.vsum += p[6];
					vdata.sats.vsum += p[3];
					vcnt += 1;

					if(phm != dt_to_time(p[0]).slice(0,_slice)){
						phm = dt_to_time(p[0]).slice(0,_slice);

						add_data('vout', 2);
						add_data('vin', 3);
						add_data('speed', 2);
						add_data('sats', 2);

						vcnt = 0;
					}
					//vdata.addRow([p[0].toString(), 1.2]);
				}
				/*if(vcnt){
						add_data('vout', 2);
						add_data('vin', 3);
						add_data('speed', 2);
						add_data('sats', 2);
				}*/

				// Create and draw the visualization.
				function draw_data(name, title){
					//vdata[name].data.sort([{column: 0}]);
					$('#geos_vis_' + name).empty();
					if(vdata[name].data.getNumberOfRows()>0){
						//var delta = (vdata[name].vmax - vdata[name].vmin) / 1.0;
						var chart = new google.visualization.LineChart(document.getElementById('geos_vis_' + name));
						chart.draw(vdata[name].data, {
							curveType: "function",
							title: title,
							width: 700, height: 400,
							vAxis: {minValue: vdata[name].vmin /*- delta*/, maxValue: vdata[name].vmax /*+ delta*/},
							chartArea:{left:40,top:20,width:650,height:330},
		                  			legend: 'none',
							hAxis: {slantedTextAngle: 90}
		                		});
					}
				}

				draw_data('vout', 'Основное питание');
				draw_data('vin', 'Резервное питание');
				draw_data('speed', 'Скорость (средняя)');
				draw_data('sats', 'Спутники (усредненное значение)');
			}
		});
	}

	$('span.showchart').click(function(){
		var name = $(this).attr('value');
		log('showchart', name);
		//if(vdata[name].data.getNumberOfRows()>0){
			$('.geos_vis').hide();
			$('#geos_vis_' + name).show();
			$('#geos_previev').show('fast');
		//}
	});

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