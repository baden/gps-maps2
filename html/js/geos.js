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

				var _slice=5, _tail='';
				if(data.points.length > 5000){
					_slice = 3;
					_tail = '00';
				} else if(data.points.length > 280){
					_slice = 4;
					_tail = '0';
				} 

				function add_data(name, row, digits){
					var value = parseFloat((vdata[name].vsum/vcnt).toFixed(digits));
					vdata[name].data.addRow([row+_tail, value]);
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

					var p = data.points[i];
					var row = '<tr>';
					row += td([p[0], p[1].toFixed(5), p[2].toFixed(5), p[3], p[6].toFixed(1), p[4].toFixed(2), p[5].toFixed(1)]);
					row += '</tr>';
					tbody.append(row);

					vdata.vout.vsum += p[4];
					vdata.vin.vsum += p[5];
					vdata.speed.vsum += p[6];
					vdata.sats.vsum += p[3];
					vcnt += 1;

					if(phm != p[0].slice(0,_slice)){
						phm = p[0].slice(0,_slice);

						add_data('vout', p[0].slice(0,_slice), 2);
						add_data('vin', p[0].slice(0,_slice), 3);
						add_data('speed', p[0].slice(0,_slice), 2);
						add_data('sats', p[0].slice(0,_slice), 2);

						vcnt = 0;
					}
					//vdata.addRow([p[0].toString(), 1.2]);
				}
				if(vcnt){
						add_data('vout', p[0].slice(0,_slice), 1);
						add_data('vin', p[0].slice(0,_slice), 2);
						add_data('speed', p[0].slice(0,_slice), 1);
						add_data('sats', p[0].slice(0,_slice), 1);
				}

				// Create and draw the visualization.
				function draw_data(name, title){
					vdata[name].data.sort([{column: 0}]);
					$('#geos_vis_' + name).empty();
					if(vdata[name].data.getNumberOfRows()>0){
						var chart = new google.visualization.LineChart(document.getElementById('geos_vis_' + name));
						chart.draw(vdata[name].data, {
							curveType: "function",
							title: title,
							width: 400, height: 300,
							vAxis: {minValue: vdata[name].vmin, maxValue: vdata[name].vmax},
							chartArea:{left:40,top:20,width:350,height:230},
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
		var type = $(this).attr('value');
		log('showchart', type);
		$('.geos_vis').hide();
		$('#geos_vis_' + type).show();
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
