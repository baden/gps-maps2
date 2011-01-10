var show_bounds = false;

var geocoder;

var map = null;
var ruler1 = null;
var skey = null;
//var rulers = [];

var prev_minp = -1;

var flightPlanCoordinates = [];
//var zooms = []

var showed_path = [];
//showed_path = new google.maps.MVCArray();

var flightPath = null; //[];
var flightPathBounds = null;
//var fpi = 0;

var stop_markers = [];

function Profile(name){
	this.name = name;
	this.start = new Date();
	console.log("Profile: " + name + " start ");
}

Profile.prototype.show = function(){
	var end = new Date();
	var time = end.getTime() - this.start.getTime();
	console.log("Profile: " + this.name + " - " + time + " ms");
}


var main_bound_rectangle = null;
var sub_bounds = [];
var sub_bound_rectangles = [];
var sub_bound_indexes = [];
var search_bound_rectangle = null;

function LoadPoints1(){
	path = '/debug/msg?uid={{ account.user.user_id }}';
	var xhr = new XMLHttpRequest();
	xhr.open('POST', path, true);
	xhr.send();
}

var GetPath = function(skey_, from, to){
	skey = skey_;
	ruler1.setSysKey(skey);
	console.log("::GetPath.start");
	url = "/api/geo/get?skey="+skey+"&from="+from+"&to="+to;
	$.getJSON(url, function (data) {
		//$("#progress").html("Обрабатываем...");
		console.log("getJSON parce");
		if (data.answer && data.points.length > 0) {
			ParcePath(data);
		}
	});
	console.log("::GetPath.end");
}

//google.maps.LatLng.prototype.setZoom = function(z){this.zoom = z;}
//mLatLng_base = google.maps.LatLng.constructor;

function newClass(parent, prop) {
  // Dynamically create class constructor.
  var clazz = function() {
    // Stupid JS need exactly one "operator new" calling for parent
    // constructor just after class definition.
    if (clazz.preparing) return delete(clazz.preparing);
    // Call custom constructor.
    if (clazz.constr) {
      this.constructor = clazz; // we need it!
      clazz.constr.apply(this, arguments);
    }
  }
  clazz.prototype = {}; // no prototype by default
  if (parent) {
    parent.preparing = true;
    clazz.prototype = new parent;
    clazz.prototype.constructor = parent;
    clazz.constr = parent; // BY DEFAULT - parent constructor
  }
  if (prop) {
    var cname = "constructor";
    for (var k in prop) {
      if (k != cname) clazz.prototype[k] = prop[k];
    }
    if (prop[cname] && prop[cname] != Object)
      clazz.constr = prop[cname];
  }
  return clazz;
}

mLatLng = newClass(google.maps.LatLng, {
	constructor: function(la, lo, z) {
	    //document.writeln("Вызван конструктор Zaporojets().");
	    this.constructor.prototype.constructor.call(this, la, lo);
	    this.zoom = z;
	  },
});
/*
mLatLng = function(la, lo, z){
//	base.constructor.call(la, lo);
//	google.maps.LatLng.prototype.constructor(la, lo);
//	mLatLng_base(la, lo);
	this.constructor.prototype.constructor.call(this, la, lo);
	this.zoom = z;
};

mLatLng.prototype = new google.maps.LatLng.prototype.constructor();
*/

function dt_to_Date(d){
/*	var h = parseInt(d.slice(6, 8), 10);
	var dat = new Date(
			parseInt('20' + d[0]+d[1], 10),	// год
			parseInt(d[2]+d[3], 10) - 1,	// месяц
			parseInt(d[4]+d[5], 10),	// день
			parseInt(d[6]+d[7], 10),	// часы
			parseInt(d[8]+d[9], 10),	// минуты
			parseInt(d[10]+d[11], 10)	// секунды
	);
	console.log('d=' + d + ' h:' + h + '  new Date =', dat);
	return dat;
*/
	return new Date(
			parseInt('20' + d[0]+d[1], 10),	// год
			parseInt(d[2]+d[3], 10) - 1,	// месяц
			parseInt(d[4]+d[5], 10),	// день
			parseInt(d[6]+d[7], 10),	// часы
			parseInt(d[8]+d[9], 10),	// минуты
			parseInt(d[10]+d[11], 10)	// секунды
	);

}

/*
function t_to_hms(d){
	var minutes = (d - (d % 60)) / 60;
	var hours = (minutes - (minutes % 60)) / 60;
	minutes = minutes % 60;
	var seconds = d % 60;
	if(hours) return hours + ' ч ' + minutes + ' мин ' + seconds + ' сек';
	else if(minutes) return minutes + ' мин ' + seconds + ' сек';
	else return seconds + ' сек';
}
*/

var Image_Stop = new google.maps.MarkerImage(
	'/images/marker-stop.png',
	new google.maps.Size(16, 20),
	new google.maps.Point(0, 0),
	new google.maps.Point(7, 19)
)

var Image_Halt = new google.maps.MarkerImage(
	'/images/marker-halt.png',
	new google.maps.Size(16, 20),
	new google.maps.Point(0, 0),
	new google.maps.Point(7, 19)
)

var stop_infowindow;

var ParcePath = function(data){
	var profile = new Profile("GetPath");

	console.log("Loading a path...");

	profile.show();
	console.log("Create LatLng and calculate bounds...");
	flightPlanCoordinates = [];
	for(var i in data.points){
		var l = new google.maps.LatLng(data.points[i][1], data.points[i][2], false);
		l.date = data.points[i][0];
		l.angle = data.points[i][3];
		l.zoom = data.points[i][4];
		flightPlanCoordinates.push(l);
		/*
		if(i>0){
			if(data.points[i][0]<data.points[i-1][0]){
				console.log("========= ERROR in ", i);
			}
		}
		*/
	}

	flightPathBounds = new google.maps.LatLngBounds(
		new google.maps.LatLng(data.bounds.sw[0], data.bounds.sw[1]),
		new google.maps.LatLng(data.bounds.ne[0], data.bounds.ne[1])
	);
	/*	
	if(!main_bound_rectangle){
		main_bound_rectangle = new google.maps.Rectangle({
			bounds: flightPathBounds,
			map: map,
			fillColor: "#0000FF",
			fillOpacity: 0.1,
			strokeColor: "#0000FF",
			strokeOpacity: 1.0,
			strokeWeight: 4
		});
	} else {
		main_bound_rectangle.setBounds(flightPathBounds);
	}
	*/
	
	//var sw = flightPathBounds.getSouthWest();
	//var ne = flightPathBounds.getNorthEast();

	console.log("Bound in request: (" + data.bounds.sw[0] + "," + data.bounds.sw[1] + ")-(" + data.bounds.ne[0] + "," + data.bounds.ne[1] + ")" );
	//map.panToBounds(flightPathBounds);
	map.panTo(flightPlanCoordinates[0]);

	profile.show();
	console.log("Prepare sub bounds...");
	sub_bounds = [];
	sub_bound_indexes = [];
	
	// Init sub_bounds for entire area
	for(var i in data.subbounds){
		sub_bounds.push(new google.maps.LatLngBounds(
			new google.maps.LatLng(data.subbounds[i].sw[0], data.subbounds[i].sw[1]),
			new google.maps.LatLng(data.subbounds[i].ne[0], data.subbounds[i].ne[1])
		));
		sub_bound_indexes.push(data.subbounds[i].i);
	}

	if(show_bounds){
		for(var i in sub_bounds){
			if(sub_bound_rectangles.length <= i){
				sub_bound_rectangles.push(
					new google.maps.Rectangle({
						bounds: sub_bounds[i],
						map: map,
						clickable: false,
						fillColor: "#00FF00",
						fillOpacity: 0.1,
						strokeColor: "#00FF00",
						strokeOpacity: 1.0,
						strokeWeight: 1
					})
				);
			} else {
				sub_bound_rectangles[i].setBounds(sub_bounds[i]);
			}
		}
		if(sub_bound_rectangles.length > sub_bounds.length){
			for(var i=sub_bounds.length; i<sub_bound_rectangles.length; i++){
				sub_bound_rectangles[i].setBounds(null);
			}
		}
	}

	profile.show();

	console.log("Clear stop_markers...");
	for(var i in stop_markers){
		stop_markers[i].setMap(null);
	}
	stop_markers = [];
	console.log("Make stop_markers...");
	for(var i in data.stops){

		var dstop = dt_to_Date(data.points[data.stops[i].i][0]);
		var dstart = dt_to_Date(data.points[data.stops[i].s][0]);

		//var dt = (dt_to_Date(data.points[data.stops[i].s][0]) - dt_to_Date(data.points[data.stops[i].i][0])) / 1000;
		var dt = (dstart - dstop) / 1000;
		var tp = '';
		var icon;


		//console.log('src:' + data.points[data.stops[i].s][0] + ' , ' + data.points[data.stops[i].i][0]);
		//console.log('dt=', dt, ' ', d1, '(', d1.getTime(), '-', d2, '(', d2.getTime());

		if(dt > 5*60) {
			tp = 'стоянка ';
			icon = Image_Stop;
		} else {
			tp = 'остановка ';
			icon = Image_Halt;
		}
		var marker = new google.maps.Marker({
		        	position: new google.maps.LatLng(data.stops[i].p[0], data.stops[i].p[1]),
			        map: map,
				title:
					tp + td_to_hms(dt) +
					'\n' + dt_to_datetime(data.points[data.stops[i].i][0]) + '...' + dt_to_datetime(data.points[data.stops[i].s][0]),
					//'\n' + dstop + '...' + dstart,
				icon: icon,
			        draggable: false
				//zIndex: -1000
			});
		google.maps.event.addListener(marker, 'click', function(moev){
			console.log("Stop marker: click.");
			//console.log(this);
			//console.log(moev);

			if(1){
			//var latlng = new google.maps.LatLng(lat, lng);
			var position = this.position;
			geocoder.geocode({'latLng': this.position}, function(results, status) {
			      if (status == google.maps.GeocoderStatus.OK) {
				var address = geocode_to_addr(results);

			  	//console.log(results);

				if(stop_infowindow) stop_infowindow.close();
				stop_infowindow = new google.maps.InfoWindow({content:
					//'<div style="width: 220px; height: 220px; border: none;">'+
					address,
					//'</div>',
					position: position,
				});
				stop_infowindow.open(map);

			      } else {
			        alert("Geocoder failed due to: " + status);
			      }
			    });
			}

			/*var url = 'http://maps.google.com/maps/geo?q=48.50,35.49&output=json&oe=utf8&sensor=false&key=ABQIAAAADIf1TyW8EOrlksPTOSU_ahT2yXp_ZAY8_ufC3CFXhHIE1NvwkxQA1Z3_lxzOW0j5WczdNXZJcWiYrQ';
			$.getJSON(url, function (data) {
				if (data) {
					console.log("geocoding ok.");

				}
			});*/
		});
		stop_markers.push(marker);

	}
	console.log('Stop markers: ', data.stops.length);
	profile.show();

	DrawPlyline();
	PathRebuild();
}


var once = true;

var PathRebuild = function(){
	var profile = new Profile("PathRebuild");

	var mapzoom = map.getZoom();
	//if(showed_path.length != 0){
	//	flightPath.setPath(null);
	//}

	console.log("Select points for this zoom [" + mapzoom + "]");

	// Now we use STUPID optimization methon - simple skip points
	
	/*
	var projection = map.getProjection();
	var point = projection.fromLatLngToPoint(flightPlanCoordinates[0]);
	console.log("1st pont is (" + point.x + "," + point.y + ")");
	var point = projection.fromLatLngToPoint(flightPlanCoordinates[1]);
	console.log("1st pont is (" + point.x + "," + point.y + ")");
	*/

	//var step = 16-map.getZoom();
	//if(step < 1) step = 1;

	// temporraly disable draw optimization
	//step = 1;

	//console.log(" - purge old points");
	//showed_path = new google.maps.MVCArray();
	//var path = flightPath.getPath();
	//path.clear();
	showed_path = []
	//profile.show();

	//console.log(" - purge points on map");
	//if(flightPath[fpi]) flightPath[fpi].setPath(showed_path);
	//if(flightPath) flightPath.setPath(path);
	//profile.show();

	console.log(" - collect new points");
	for(var i=0; i<flightPlanCoordinates.length; i++){
		//if(zooms[i] <= mapzoom)
		var p = flightPlanCoordinates[i];

		//if(flightPlanCoordinates[i].zoom <= mapzoom)
		//	showed_path.push(flightPlanCoordinates[i]);
		if(p.zoom <= mapzoom){
			showed_path.push(p);
			//showed_path.insertAt(
			//path.push(p);
		}
	}
	profile.show();

	console.log(" - assign points to map");
//	if(once){
	//if(flightPath[fpi]) flightPath[fpi].setPath(showed_path);
	if(flightPath) flightPath.setPath(showed_path);
//		once = false;
//	}
	//if(flightPath) flightPath.setPath(path);
	//fpi = 1 - fpi;

	profile.show();

	//console.log

	$("#mark1").html("Points: " + showed_path.length + "/" + flightPlanCoordinates.length);
	//profile.show();
}

var UpdateMarker = function (moev){
	var start = new Date();

	if(showed_path.length == 0) return;

	var mapzoom = map.getZoom();
	var size = 0.003*Math.pow(2,13-mapzoom);
	if(size < 0.0001) size = 0.0001;
	var clat = Math.cos(moev.latLng.lat() * Math.PI / 180);
	if(clat < 0.0001) clat = 0.0001;

	var bound = new google.maps.LatLngBounds(
		new google.maps.LatLng(moev.latLng.lat() - size*clat, moev.latLng.lng() - size ),
		new google.maps.LatLng(moev.latLng.lat() + size*clat, moev.latLng.lng() + size )
	);

//	rulers[0].setPosition(new google.maps.LatLng(moev.latLng.lat()-0.5, moev.latLng.lng()-0.5));
	//rulers[0].setPosition(bound.getSouthWest());
	//rulers[1].setPosition(bound.getNorthEast());

	
	if(show_bounds){
		if(!search_bound_rectangle){
			search_bound_rectangle = new google.maps.Rectangle({
				bounds: bound,
				map: map,
				fillColor: "#00FFFF",
				fillOpacity: 0.1,
				strokeColor: "#00FFFF",
				strokeOpacity: 1.0,
				strokeWeight: 1
			});
		} else {
			search_bound_rectangle.setBounds(bound);
		}
	}

	// Highlight intersect bounds and search in bounded points
	var total_points = 0;
	var mind = 1000000000;
	var minp = 0;
	
	if(sub_bound_indexes.length != 0){
		for(var i in sub_bounds){
			if(bound.intersects(sub_bounds[i])){
				if(show_bounds){
					sub_bound_rectangles[i].setOptions({strokeWeight: 3, fillOpacity:0.3});
				}
				total_points += sub_bound_indexes[i].length;

				for(var j in sub_bound_indexes[i]){
					p = flightPlanCoordinates[sub_bound_indexes[i][j]];
					if(bound.contains(p)){
						d = distance(moev.latLng, p);
						if(d < mind) {
							mind = d;
							minp = sub_bound_indexes[i][j];
						}
					}
					//console.log("flightPath: d[" + i + "] = " + d);
				}

			} else {
				if(show_bounds){
					sub_bound_rectangles[i].setOptions({strokeWeight: 1, fillOpacity:0.1});
				}
			}
		}
	}

//	var projection = map.getProjection();
	//var point = projection.fromLatLngToPoint(moev.latLng);
	//$("#mark").css("left", point.x + "px");
	//$("#mark").css("top", point.y + "px");

	//console.log("flightPath: mousemove (" + moev.latLng.lat() + ";" + moev.latLng.lng() + ")");
/*
	for(var i in showed_path){
		p = showed_path[i];
		if(bound.contains(p)){
			d = distance(moev.latLng, p);
			if(d < mind) {
				mind = d;
				minp = i;
			}
		}
		//console.log("flightPath: d[" + i + "] = " + d);
	}
*/
	if(minp != prev_minp){
		ruler1.setPosition(flightPlanCoordinates[minp]);
		//ruler1.setTitle("Date: " + showed_path[minp].date);
		//$("#point_info").html("Pos: " + flightPlanCoordinates[minp]);
		//console.log("flightPath: minp set to = " + minp);
		prev_minp = minp;
	}
	var end = new Date();
	var time = end.getTime() - start.getTime();
	//console.log("time: " + time);
	$("#mark2").html("in s/bounds: " + total_points + " time: " + time);
}

var once_map_style = true;

function CreateMap()
{
	geocoder = new google.maps.Geocoder();
      var mapOptions = {
        center: new google.maps.LatLng(48.5000, 34.599),
        mapTypeId: google.maps.MapTypeId.ROADMAP,
	mapTypeControl: false,
	disableDoubleClickZoom: true,
	draggableCursor: "default",
        zoom: 10,
      };
      
      map = new google.maps.Map(document.getElementById("map"), mapOptions);

	google.maps.event.addListener(map, 'bounds_changed', function(){
		//console.log("Map: bounds_changed.");
	});
	google.maps.event.addListener(map, 'center_changed', function(){
		//console.log("Map: center_changed.");
	});
	google.maps.event.addListener(map, 'click', function(moev){
		//console.log("Map: click.");
	});
	google.maps.event.addListener(map, 'dblclick', function(moev){
		//console.log("Map: dblclick.");
	});
	google.maps.event.addListener(map, 'drag', function(){
		//console.log("Map: drag.");
	});
	google.maps.event.addListener(map, 'dragend', function(){
		//console.log("Map: dragend.");
	});
	google.maps.event.addListener(map, 'dragstart', function(){
		//console.log("Map: dragstart.");
	});
	if(0){
	google.maps.event.addListener(map, 'idle', function(){
		if(once_map_style){
			once_map_style = false;
			console.log("Map: idle.");
			//$('#map div:first > div:eq(4) > div > div').css('background-color', 'green');
			//$('#map div:first > div:eq(4) > div > div').button();
			var el = $('#map div:first > div:eq(4) > div:first');
			//$('#map div:first > div:eq(4) > div > div').button().next().button();
			el./*find('div').*/css('border-top-left-radius', '6px 6px');
			el.find('div').css('border-top-left-radius', '6px 6px');
			el./*find('div').*/css('border-bottom-left-radius', '6px 6px');
			el.find('div').css('border-bottom-left-radius', '6px 6px');
			el = el.next().next().next();
			el./*find('div').*/css('border-top-right-radius', '6px 6px');
			el.find('div').css('border-top-right-radius', '6px 6px');
			el./*find('div').*/css('border-bottom-right-radius', '6px 6px');
			el.find('div').css('border-bottom-right-radius', '6px 6px');
			//el.next().find('div').button();
			
		}
	});
	}
	google.maps.event.addListener(map, 'mousemove', UpdateMarker);
	/*
	google.maps.event.addListener(map, 'mousemove', function(moev){
		//console.log("Map: mousemove.");
	});
	*/
	google.maps.event.addListener(map, 'mouseout', function(moev){
		//console.log("Map: mouseout.");
	});
	google.maps.event.addListener(map, 'mouseover', function(moev){
		//console.log("Map: mouseover.");
	});
	google.maps.event.addListener(map, 'resize', function(){
		//console.log("Map: resize.");
	});
	google.maps.event.addListener(map, 'rightclick', function(moev){
		//console.log("Map: rightclick.");
	});
	google.maps.event.addListener(map, 'tilesloaded', function(){
		//console.log("Map: tilesloaded.");
	});
	google.maps.event.addListener(map, 'zoom_changed', function(){
		//console.log("Map: zoom_changed.");
		PathRebuild();
	});
	/*
	google.maps.event.addListener(map, 'domready', function(){
		console.log("Map: ready.");
		//PathRebuild();
	});
	*/

	$('#map div').ready(function(){
		console.log("Map: ready.");
		//console.log(map.controls);
		$('#map div').css('background-color', 'green');
	}); 


	/*
	var riler1_Image = new google.maps.MarkerImage(
		'/images/marker-select.png',
		new google.maps.Size(16, 16),
		new google.maps.Point(0, 0),
		new google.maps.Point(7, 7)
	)

	ruler1 = new google.maps.Marker({
	        position: map.getCenter(),
	        map: map,
		icon: riler1_Image,
	        draggable: false
	});
	*/

	ruler1 = new MyMarker(map);

	/*
	for(var i=0; i<4; i++){
		rulers.push(new google.maps.Marker({
		        position: map.getCenter() ,
		        map: map,
		        draggable: false
		}));

	}
	*/

	//GetLastPositions();

}

var last = null;

function GetLastPositions(acckey) {
	console.log('Get last positions...');
	url = "/api/geo/last?acckey=" + acckey;
	$.getJSON(url, function (data) {
		//$("#progress").html("Обрабатываем...");
		if (data.answer && data.answer == 'ok') {
			console.log('Show last positions...');
			//console.log()
			for(var i in data.geo){
				var p = data.geo[i];
				//console.log(' data['+i+']='+p.imei);

				var last_pos = new google.maps.Marker({
				        position: new google.maps.LatLng(p.data.point.lat, p.data.point.lon),
				        map: map,
					//icon: riler1_Image,
					title: p.desc,
				        draggable: false
				});

			}
			//ParcePath(data);
		}
	});
}

function distance(p1, p2) {
    var R = 6371; // km (change this constant to get miles)
    var dLat = (p2.lat()-p1.lat()) * Math.PI / 180;
    var dLon = (p2.lng()-p1.lng()) * Math.PI / 180;
    var a = Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(p1.lat() * Math.PI / 180 ) * Math.cos(p2.lat() * Math.PI / 180 ) *
        Math.sin(dLon/2) * Math.sin(dLon/2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    var d = R * c;
    //if (d>1) return Math.round(d)+"km";
    //else if (d<=1) return Math.round(d*1000)+"m";
    return d;
}


function DrawPlyline()
{
	//if(flightPath.length == 2) return;
	if(flightPath) return;
	/*flightPath.push(new google.maps.Polyline({
		//path: flightPlanCoordinates,
		//path: showed_path,
		strokeColor: "#FF0000",
		strokeOpacity: 1.0,
		strokeWeight: 3
	}));
	flightPath.push(new google.maps.Polyline({
		//path: flightPlanCoordinates,
		//path: showed_path,
		strokeColor: "#00FF00",
		strokeOpacity: 1.0,
		strokeWeight: 3
	}));
	flightPath[0].setMap(map);
	flightPath[1].setMap(map);*/

	flightPath = new google.maps.Polyline({
		//path: flightPlanCoordinates,
		//path: showed_path,
		strokeColor: "#FF0000",
		strokeOpacity: 1.0,
		strokeWeight: 3
	});
	flightPath.setMap(map);

	if(0){
	google.maps.event.addListener(flightPath, 'click', function(moev){
		console.log("flightPath: click.");
	});

	google.maps.event.addListener(flightPath, 'mouseover', function(moev){
		//console.log("flightPath: mouseover.");
	});

	google.maps.event.addListener(flightPath, 'mouseout', function(moev){
		//console.log("flightPath: mouseout.");
	});
	}
	//google.maps.event.addListener(flightPath, 'mousemove', UpdateMarker);
	console.log("Draw polyline.");
}

var ClearPath = function(skey){
	var profile = new Profile("Clear path");
	console.log("Clear path.");
	showed_path = []
	console.log(" - purge points on map");
	if(flightPath) flightPath.setPath(showed_path);
	console.log("Clear stop_markers...");
	for(var i in stop_markers){
		stop_markers[i].setMap(null);
	}
	stop_markers = [];
	profile.show();
}

var prev_sender=null;

function SetDay(skey, date){
	var from = date+'000000';
	var to = date+'235959';
	console.log("::SetDay.start date=" + date + " from:" + from + " to:" + to);
	GetPath(skey, from, to);
	//console.log(sender + '-' + prev_sender);
	//if(prev_sender) $('#'+prev_sender).css('background-color','');
	//if(prev_sender) $('#'+prev_sender).css({'background-color': '', '-webkit-box-shadow': ''});
	//prev_sender = sender;
	//$('#'+sender).css('background-color', 'lime');
	//$('#'+sender).css({'background-color': 'lime', 'border': '1px solid black'});
	//$('#'+sender).css({'background-color': 'lime', '-webkit-box-shadow': '0px 0px 3px #404040'});
}

var dbg_data = null;

monthNames = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'];

function DayList(skey, month){
	console.log("::DayList.start");
	url = "/api/geo/dates?skey=" + skey + "&month="+ month;
	$.getJSON(url, function (data) {
		//$("#progress").html("Обрабатываем...");
		console.log("::DayList: getJSON parce " + data.years);
		dbg_data = data;
		if (data.answer) {
			console.log(data);

			$("#datepicker").datepicker("refresh");

			$("#date_select table tbody a").each(function(index){
				var day = parseInt($(this).text(), 10);
				console.log(index + ' : ' + day);

				var parent = $(this).parent();

				if(data.days.indexOf(day) == -1){
					parent.addClass('ui-datepicker-unselectable');
					parent.addClass('ui-state-disabled');
					//parent.attr('onclick', '');
					parent.removeAttr('onclick');
					parent.empty();
					parent.append('<span class="ui-state-default" href="#">'+day+'</span>');
				}
				//if(index % 5) $(this).css('opacity', '0.2');
			});


			//item += '<a id="lmlnk_'+j+'_'+k+'" href="javascript:SetDay(\''+skey+'\',\''+(i%100)+j+d[k]+'\', \'lmlnk_'+j+'_'+k+'\');">' + d[k] + '</a> ';

			if(0){
			$("#daylist").accordion( "destroy" );
			var item = '';
			var last;
			for(var i in data.years){
				var m = data.years[i];
				item += '<h3><a href="#">' + i + '</a></h3>';
				console.log('year:' + i);
				item += '<div class="list_months">';
				for(var j in m){
					//item += '<h3><a href="#">' + j + '/' + i + '</a></h3><div>';
					item += '<h3><a href="#">' + monthNames[j-1] + '</a></h3><div>';
					//item += monthNames[j-1];
					var d = m[j];

					//item += '<ul class="list_days">';
					for(var k in d){
						item += '<a id="lmlnk_'+j+'_'+k+'" href="javascript:SetDay(\''+skey+'\',\''+(i%100)+j+d[k]+'\', \'lmlnk_'+j+'_'+k+'\');">' + d[k] + '</a> ';
						//item += '<a href="javascript:SetDay(\''+skey+'\',\''+(i%100)+j+d[k]+'\', this);">' + d[k] + '</a> ';
					}
					//item += '</ul>';
					item += '</div>';

					//item += '</li>';
				}
				item += '</div>';
				//item += '</li>';
				//$("#daylist").append('<li><a href="javascript:SetDay(\''+skey +'\',\''+d+'\');">'+d[4]+d[5]+'/'+d[2]+d[3]+'/20'+d[0]+d[1]+'</a></li>');
				//$("#daylist").append('<li><a href="javascript:SetDay(\''+skey +'\',\''+d+'\');">'+i+'</a></li>');
				//$("#daylist").append(item);
				/*$(".list_days").sortable();
				$(".list_days").disableSelection();
				$(".list_months").sortable();
				$(".list_months").disableSelection();*/
			}
			$("#daylist").html(item);
			$("#daylist").accordion({autoHeight: false, navigation: true, active: ':last'});
			//console.log(data.years);
			$(".list_months").accordion({autoHeight: false, navigation: true, active: ':last'});
			//$("button").button();
			//$("#daylist").css('display', '');
			$("#daylist").fadeIn();
			}
		}
	});
	console.log("::DayList.end");

}
