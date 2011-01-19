
// Private
(function($){
	function log_line(d) {
		var row = '<td>'+d.time+'</td><td>'+d.text+'<td>'+d.label+'</td></td>';
		if(config.admin){
			row += '<td class="del_log" title="Удалить сообщение\nБез подтверждения!" key='+d.key+'><span class="ui-icon ui-icon-close"></span></td>'
		}
		return row;
	}

	function UpdateLog() {
		log('UpdateLog');
		var table = $("#log_table tbody");
		table.empty();

		var url = '/api/logs/get?skey=' + config.skey;
		$.getJSON(url, function (data) {
			//$("#progress").html("Обрабатываем...");
			log("getJSON parce");
			if (data.answer && data.answer == 'ok') {
				for(var i in data.logs){
					table.append('<tr>' + log_line(data.logs[i]) + '</tr>');
				}
			}
			$('td.del_log').click(function(){
				log('del:' + $(this).attr('key'));
			});
		});
	}

	$(document).ready(function() {
		log('Загрузка закладки. События.');

		UpdateLog();

		var list = $('#log_syslist');

		list.empty();
		for(i in config.systems){
			var s = config.systems[i];
			list.append('<option imei="'+s.imei+'" value="'+s.skey+'">'+s.desc+'</option>');
		}
		config.updater.add('changedesc', function(msg) {
			//log('LOGS: Update descriptions');
			$(list).find('option[value="' + msg.data.skey + '"]').html(msg.data.desc);
		});

		list.bind('change', function(){
			config.skey = $(this).attr('value');
			UpdateLog();
		});

		config.updater.add('addlog', function(msg) {
			if(msg.data.skey == config.skey){
				$("#log_table tbody tr:first").before('<tr>' + log_line(msg.data) + '</tr>');
			}
		});
	});
	
})(jQuery);
