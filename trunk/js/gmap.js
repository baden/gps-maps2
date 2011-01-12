(function( $, undefined ) {


//$.extend($.ui, { gmap: { version: "0.0.1" } });

var PROP_NAME = 'gmap';
//var dpuuid = new Date().getTime();

/* Google Map v3 widget.
   Use the singleton instance of this class, $.gmap, to interact with the gmap widget.
   Settings for (groups of) gmap container are maintained in an instance object,
   allowing multiple different settings on the same page. */

function GMap() {
	this.debug = false; // Change this to true to start debugging
	this._curInst = null; // The current instance in use
	this._mainDivId = 'gmap'; // The ID of the main gmap widget
	this.regional = []; // Available regional settings, indexed by language code
	this.regional[''] = { // Default regional settings
		closeText: 'Close' // Display text for close link
	}
	this._defaults = { // Global defaults for all the gmap widget instances
		pos: new google.maps.LatLng(48.5000, 34.599), // Default position
		maptype: google.maps.MapTypeId.ROADMAP,
		zoom: 10,
		marker: 'none',
		markertitme: 'Ooooops!'
	}

	this.Image_Stop = new google.maps.MarkerImage(
		'/images/marker-stop.png',
		new google.maps.Size(16, 20),
		new google.maps.Point(0, 0),
		new google.maps.Point(7, 19)
	)

	this.Image_Halt = new google.maps.MarkerImage(
		'/images/marker-halt.png',
		new google.maps.Size(16, 20),
		new google.maps.Point(0, 0),
		new google.maps.Point(7, 19)
	)

	$.extend(this._defaults, this.regional['']);
//	this.addClass = "ui-widget ui-widget-content ui-helper-clearfix ui-corner-all";
	//this.dpDiv = $('<div id="' + this._mainDivId + '" class="ui-widget ui-widget-content ui-helper-clearfix ui-corner-all"></div>');
}

$.extend(GMap.prototype, {
	/* Class name added to elements to indicate already configured with a gmap widget. */
	markerClassName: 'hasGMap',
	/* Debug logging (if enabled). */
	log: function () {
		if (this.debug)
			console.log.apply('', arguments);
	},
	// TODO rename to "widget" when switching to widget factory
	_widgetGMap: function() {
		return this.dpDiv;
	},

	_getInst: function(target) {
		try {
			return $.data(target, PROP_NAME);
		}
		catch (err) {
			throw 'Missing instance data for this datepicker';
		}
	},

	_findPos: function(obj) {
		var inst = this._getInst(obj);
		var isRTL = this._get(inst, 'isRTL');
	        while (obj && (obj.type == 'hidden' || obj.nodeType != 1)) {
	            obj = obj[isRTL ? 'previousSibling' : 'nextSibling'];
	        }
        	var position = $(obj).offset();
		    return [position.left, position.top];
	},

	_setPos: function(inst, date, noChange) {
		//console.log('GMAP:setPos');
		//console.log(arguments);
	},

	_setPosGMap: function(target, pos) {
		//console.log('GMAP:setPos (' + target + ')');
		
		var inst = this._getInst(target);
		if (inst) {
			this._setPos(inst, pos);
			//console.log('inst:');
			//console.log(inst);
			//this._updateDatepicker(inst);
			//this._updateAlternate(inst);
		} else {
			//console.log('error inst');
		}
		
	},

	_destroyGMap: function(target) {
		console.log('GMAP: destroy');
		var $target = $(target);
		var inst = $.data(target, PROP_NAME);
		if (!$target.hasClass(this.markerClassName)) {
			console.log('not a map');
			return;
		}
		var nodeName = target.nodeName.toLowerCase();
		$.removeData(target, PROP_NAME);
		console.log($target);
		$target.removeClass(this.markerClassName).empty();
	},

	_attachMap: function(target, settings) {
		var nodeName = target.nodeName.toLowerCase();
		var id = this._mainDivId = target.id;
		var divSpan = $(target);
		//this._dialogInst
		//var nodeName = '';
		console.log('GMap:attach map to ' + nodeName + '(' + id + ') with settings:' + settings);

		//console.log(target);
		//console.log(settings);
		//var inst = this._newInst($(target));
		//inst.settings = $.extend({}, settings || {});
		divSpan.addClass(this.markerClassName);

		var instsettings = $.extend({}, this._defaults, settings || {});
		//console.log('inst.settings = ');
		//console.log(instsettings);

		var mapOptions = {
			center: instsettings.pos || new google.maps.LatLng(48.5000, 34.599),
			mapTypeId: instsettings.maptype,
			mapTypeControl: false,
			disableDoubleClickZoom: true,
			draggableCursor: "default",
			zoom: instsettings.zoom
		}
		instsettings.map = new google.maps.Map(document.getElementById(this._mainDivId), mapOptions);

		if(instsettings.marker == 'center'){
			var marker = new google.maps.Marker({
		        	position: instsettings.pos,
			        map: instsettings.map,
				title: instsettings.markertitme,
					//tp + td_to_hms(dt) +
					//'\n' + dt_to_datetime(data.points[data.stops[i].i][0]) + '...' + dt_to_datetime(data.points[data.stops[i].s][0]),
					//'\n' + dstop + '...' + dstart,
				//icon: icon,
				icon: this.Image_Stop,
			        draggable: false
				//zIndex: -1000
			});
		}
		//console.log();
		inst = $.data(target, PROP_NAME, instsettings);



	}

});


$.fn.gmap = function(options){
	/* Initialise the gmap widget. */
	if (!$.gmap.initialized) {
		// Do somthing
		$.gmap.initialized = true;
		//console.log('GMap:init(' + options + ')');
	}

	/*
	var otherArgs = Array.prototype.slice.call(arguments, 1);
	if (typeof options == 'string' && (options == 'isDisabled' || options == 'getDate' || options == 'widget'))
		return $.datepicker['_' + options + 'Datepicker'].
			apply($.datepicker, [this[0]].concat(otherArgs));
	if (options == 'option' && arguments.length == 2 && typeof arguments[1] == 'string')
		return $.datepicker['_' + options + 'Datepicker'].
			apply($.datepicker, [this[0]].concat(otherArgs));
	return this.each(function() {
		typeof options == 'string' ?
			$.datepicker['_' + options + 'Datepicker'].
				apply($.datepicker, [this].concat(otherArgs)) :
			$.datepicker._attachDatepicker(this, options);
	});
	*/
	
//	console.log('GMap:create');
	var otherArgs = Array.prototype.slice.call(arguments, 1);
//	if (options == 'option' && arguments.length == 2 && typeof arguments[1] == 'string'){
//		return $.gmap['_' + options + 'GMap'].apply($.gmap, [this[0]].concat(otherArgs));
//	}

	return this.each(function() {
		console.log('options==' + options);
		//console.log('arguments==' + arguments);
		//console.log($.gmap['_' + options + 'GMap']);
		//console.log('_' + options + 'GMap');
		typeof options == 'string' ?
			$.gmap['_' + options + 'GMap'].apply($.gmap, [this].concat(otherArgs)) :
			$.gmap._attachMap(this, options);
	});
}

$.gmap = new GMap(); // singleton instance
$.gmap.initialized = false;
//$.gmap.uuid = new Date().getTime();
$.gmap.version = "0.0.1";

// Workaround for #4055
// Add another global to avoid noConflict issues with inline event handlers
//window['DP_jQuery_' + dpuuid] = $;

})(jQuery);
