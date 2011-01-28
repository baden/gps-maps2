(function(){

if('loader' in window) return;

function Loader(){
	this.list = {}
	this.version = '0.0';
	console.log('Loader init');
}

Loader.prototype.requre = function(filename){
	console.log('Loader requre:', filename);

	if(filename in this.list) {
		console.log('Loader requre: skip');
		return;
	}

	this.list[filename] = {};

	if (filename.search('.js') != -1){ //if filename is a external JavaScript file
		var fileref=document.createElement('script');
		fileref.setAttribute('type', 'text/javascript');
		fileref.setAttribute('src', filename + '?version=' + this.version);
		console.log('Loader requre: javascript');
	} else if (filename.search('.css') != -1){ //if filename is an external CSS file
		var fileref=document.createElement('link');
		fileref.setAttribute('rel', 'stylesheet');
		fileref.setAttribute('type', 'text/css');
		fileref.setAttribute('href', filename + '?version=' + this.version);
		console.log('Loader requre: stylesheet');
	} else {
		console.log('Loader requre: unknown type');
	}
	if (typeof fileref!='undefined') document.getElementsByTagName('head')[0].appendChild(fileref);
}

Loader.prototype.setVersion = function(version){ this.version = version; }


window['loader'] = new Loader();

})();
