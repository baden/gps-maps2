(function(window, $){
	var document = window.document;

	function sendGet(url) {
		var xhr = new XMLHttpRequest();
		xhr.open('GET', url, true);
		xhr.send();
	}

	function saveconfig(it, val){
		config.ui[it] = val;
		$.ajax({
		  url: '/api/system/config?akey=' + config.akey,
		  dataType: 'json',
		  data: config.ui,
		  type: 'POST',
		  success: function(){log('Saved.');}
		});
	}

	function UpdateSysList(){
		$.getJSON('/api/info?acckey='+config.akey, function (data) {
			if(data){
				$("#config_sys_list").empty();
				for(var i in data.info.account.systems){
					var s = data.info.account.systems[i];
					$("#config_sys_list").append(
						'<li class="sli" imei="'+s.imei+'"><span class="ui-icon ui-icon-arrowthick-2-n-s mm msp"></span>' +
						'<span class="bico hl mm" title="Выбрать пиктограмму">P</span>' +
						'<span class="bconf hl mm" title="Настроить систему">C</span>' +
						'IMEI:' + s.imei + ' <desc>' + s.desc + '</desc>'+
						'<button class="key bdesc" title="Изменить описание">...</button>' +
						'</li>'
					);
				}
				//$(".key").button();
				//$("#config_list").accordion("resize");
				/*
				$(".sli").bind('contextmenu', function(e) {
					//alert('Config');
					//$("body").append('<div style="position: absolute; left: 0px; top: 0px; border:1px solid black; width: 100px; height: 200px;">Menu</div>');
					$("#popup-sys").dialog('open');
                  			return false;
        			});
				*/
				$("#config_sys_list .bdesc").button().click(function(){
					//alert(this.attributes['imei'].value);
					//var i = this.attributes['index'].value;
					var par = $(this).parent();
					var imei = par.attr('imei');
					var desc = par.find('desc').html();
					var dialog = $('#config_dialog_sys_desc');
					//log(dialog);
					//log(imei);
					//$("#sysdesc_imei").html(sys_imeis[i])
					dialog.find('label').html(imei);
					//$("#sys_desc").val(sys_descs[i]);
					dialog.find('textarea').val(desc);
					//log('Dialog: dialog-sys-desc ' + sys_imeis[i] + ' (' + sys_descs[i] + ')');
					dialog.dialog('open');
				});

				$('#config_sys_list .bconf').button().click(function(){
					var par = $(this).parent();
					var imei = par.attr('imei');
					var desc = par.find('desc').html();
					log('TBD! config', i);
					div = $('body')
					.append('<div id="config_overlay" class="ui-widget-overlay"></div>')
					.append('<div id="config_params" style="">Тут будет окно настройки системы '+desc+'</div>');

					$('#config_params')
					.append('<div id="config_params_body">Всякая хрень</div>')
					.append('<div id="config_params_close" style="position: absolute; top: -10px; left: 50%; margin-left: -20px;"><span class="ui-icon ui-icon-close"></span></div>');

					$('#config_params_close').button().click(function(){
						$('#config_params, #config_overlay').remove();
					});


				});
			}
		});
	}

	$(document).ready(function() {
		log('Загрузка закладки. Конфигурация.');

		//$("#nav_config").button("option", "disabled", true);
		// a workaround for a flaw in the demo system (http://dev.jqueryui.com/ticket/4375), ignore!
		//$("#dialog:ui-dialog").dialog("destroy");

		//$('#switcher').themeswitcher();

		/*$("button").button();*/
		//$("#config_button_sys_update").click(UpdateSysList);

		UpdateSysList();

		// Закладка "Наблюдаемые системы"

		$("#config_button_sys_add").click(function(){ $("#config_dialog_addsys").dialog('open'); });
		$("#config_dialog_addsys").dialog({
			width: 400,
			height: 200,
			modal: true,
			autoOpen: false,
			buttons: {
				'Добавить систему.': function() {
					//var imei = document.getElementById('config_addsys_imei').value;
					var imei = $('#config_dialog_addsys #config_addsys_imei').val();
					//var phone = document.getElementById('addsys_phone').value;
					//$.getJSON("/config?cmd=addsys&imei=" + imei + "&phone=" + phone, function (data) {
					$.getJSON('/api/sys/add?acckey='+config.akey+'&imei=' + imei, function (data) {
						//window.location = "/config";
						//$(this).dialog('close');
						if(data.result){
							var result = data.result;
							if(result == "not found"){
								//alert("Система не найдена. возможно система ни разу не выходила на связь с сервером.");
								$("#dialog_addsys_not_found").dialog('open');
							} else if(result == "already"){
								//alert("Вы уже наблюдаете за этой системой");
								$("#dialog_addsys_already").dialog('open');
							} else if(result == "added") {
								UpdateSysList();
								//window.location = "/config";
							}
						}
					});
					$(this).dialog('close');
				},
				'Отменить': function() {
					$(this).dialog('close');
				}
			}
		});
		//$("#dialog-addsys").dialog('open');

		$("#config_dialog_sys_desc").dialog({
			width: 500,
			height: 150,
			modal: true,
			autoOpen: false,
			buttons: {
				'Применить изменения.': function() {

					var dialog = $(this);
					//log(dialog);
					//log($(this));
					//$("#sysdesc_imei").html(sys_imeis[i])
					var imei = dialog.find('label').html();
					//$("#sys_desc").val(sys_descs[i]);
					var desc = dialog.find('textarea').val();

					//var imei = $("#sysdesc_imei").html(); //document.getElementById('sysdesc_imei').value;
					//var desc = document.getElementById('sys_desc').value;
					log('Set desc for sys ' + imei + ' -> ' + desc);
					$.getJSON('/api/sys/desc?acckey='+config.akey+'&imei=' + imei + '&desc=' + desc, function (data) {
						if(data.result){
							var result = data.result;
							if(result == "disabled"){
								//$("#dialog-need-admin").dialog('open');
							} else if(result == "ok") {
								//UpdateSysList();
								//$("#config_sysdsc_"+imei).html(desc);
								$("#config_sys_list").find('li[imei="'+imei+'"]>desc').html(desc);
							}
						}
					});
					$(this).dialog('close');
				},
				'Отменить': function() {
					$(this).dialog('close');
				}
			}
		});

		$("#dialog_addsys_not_found").dialog({modal: true, autoOpen: false, buttons:{Ok: function(){$(this).dialog("close");}}});
		$("#dialog_addsys_already").dialog({modal: true, autoOpen: false, buttons:{Ok: function(){$(this).dialog("close");}}});
		$("#popup-sys").dialog({modal: true, autoOpen: false});
		$("#popup-sys li").button();


		$('#colorpickerHolder').ColorPicker({
			color: '#0000ff',
			onShow: function (colpkr) {
				$(colpkr).fadeIn(100);
				return false;
			},
			onHide: function (colpkr) {
				$(colpkr).fadeOut(100);
				return false;
			},
			onChange: function (hsb, hex, rgb) {
				$('#colorpickerHolder div').css('backgroundColor', '#' + hex);
			}
		});

		$("#config_list").accordion({fillSpace: true, collapsible: true});
		$("#config_sys_list").sortable({
			//delay: 500,
			//axis: 'y',
			//containment: 'parent',
			handle: '.msp',
			revert: true,
			scrollSpeed: 5,
			stop: function(event, ui){
				/*console.log(ui.item.index());
				console.log(ui.item.attr('imei'));
				console.log(ui);*/
				var imei = ui.item.attr('imei');
				var index = ui.item.index();
				$.getJSON('/api/sys/sort?acckey='+config.akey+'&imei=' + imei + '&index=' + index, function (data) {
					//window.location = "/config";
					//$(this).dialog('close');
					if(data.result){
						log('Set new position for ' + imei + ' to ' + index);
					}
				});

			},
		});
		$("#config_sys_list").disableSelection();


		// Выбор темы оформления

		$('#config_list select#config_set_theme option[value="'+config.ui.theme+'"]').attr('selected', 'selected');
		log('Set theme item:', config.ui.theme, $('#config_list select#config_set_theme option[value="'+config.ui.theme+'"]'));

		$('#config_list #config_set_theme').bind('change', function(){
			var themename = $(this).attr('value');
			//log(themename);
			saveconfig('theme', themename);

			var hl = $('head #themecss');
			hl.attr('href', '/plugins/jquery-ui-themes-1.8.7/jquery-ui-themes-1.8.7/themes/'+themename+'/jquery.ui.all.css');
			//log(hl);
		});


		// Административные и отладочные функции

		if(config.admin){
			$("button.dbg_send_msg").click(function(){
				var imei = $(this).attr('imei');
				var text = $(this).attr('value');
				//sendGet('http://localhost/addlog?imei='+imei+'&text=%D0%92%D0%BD%D0%B5%D1%88%D0%BD%D0%B5%D0%B5+%D0%BF%D0%B8%D1%82%D0%B0%D0%BD%D0%B8%D0%B5:+%3Cb%3E%D0%BD%D0%BE%D1%80%D0%BC%D0%B0%3C/b%3E');
				sendGet('/addlog?imei='+imei+'&text='+text);
			});
		}



		// Главный аккордион
		// Нужно добавить проверку что вкладка активна иначе вызвать при активации закладки
		$(window).resize(function(){$("#config_list").accordion("resize");});
		setTimeout(function(){$("#config_list").accordion("resize")}, 1000);

		//$(document).bind('contextmenu', function(e) {return false;});
	        //$(document).disableSelection();
	});

})(this, jQuery);
