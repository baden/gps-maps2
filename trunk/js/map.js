
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
	/*
	if(sub_bound_rectangles.length==0){
		for(var i in sub_bounds){
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
		}
	} else {
		for(var i in sub_bounds){
			sub_bound_rectangles[i].setBounds(sub_bounds[i]);
		}
	}
	*/

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
	var size = 0.005*Math.pow(2,13-mapzoom);
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

	/*
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
	*/

	// Highlight intersect bounds and search in bounded points
	var total_points = 0;
	var mind = 1000000000;
	var minp = 0;
	
	if(sub_bound_indexes.length != 0){
		for(var i in sub_bounds){
			if(bound.intersects(sub_bounds[i])){
				//sub_bound_rectangles[i].setOptions({strokeWeight: 3, fillOpacity:0.3});
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
				//sub_bound_rectangles[i].setOptions({strokeWeight: 1, fillOpacity:0.1});
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


function CreateMap()
{
      var mapOptions = {
        center: new google.maps.LatLng(35.09024, 40.712891),
        mapTypeId: google.maps.MapTypeId.ROADMAP,
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
	google.maps.event.addListener(map, 'idle', function(){
		//console.log("Map: idle.");
	});
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
	profile.show();
}
