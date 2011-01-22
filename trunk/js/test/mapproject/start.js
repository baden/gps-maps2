goog.provide('mapproject.start');

goog.require('goog.dom');
goog.require('goog.dom.query');
goog.require('goog.events');
goog.require('goog.events.EventType');


goog.require('goog.ui.Button');
goog.require('goog.ui.CustomButton');


mapproject.start = function() {

	goog.ui.MenuButton = function(content, opt_menu, opt_renderer, opt_domHelper) {
	  goog.ui.Button.call(this, content, opt_renderer ||
	      goog.ui.MenuButtonRenderer.getInstance(), opt_domHelper);
	
	  // Menu buttons support the OPENED state.
	  this.setSupportedState(goog.ui.Component.State.OPENED, true);
	
	  if (opt_menu) {
	    this.setMenu(opt_menu);
	  }
	  this.timer_ = new goog.Timer(500);  // 0.5 sec
	};
	goog.inherits(goog.ui.MenuButton, goog.ui.Button);

	//console.log('call sayHi');

	var $q = goog.dom.query;

	var newHeader = goog.dom.createDom('h1', {'style': 'background-color:#EEE'}, 'Hello world!');
	goog.dom.appendChild(document.body, newHeader);

	for(var i=0; i<10; i++){
		//var b1 = new goog.ui.Button('Hello!');
		var b1 = new goog.ui.CustomButton('Button');
		//goog.dom.appendChild(document.body, b1);
		b1.render(goog.dom.getElement('b1'));
		//goog.events.listen(b1, EVENTS, logEvent);
	}

	goog.array.forEach(goog.dom.query('h1 a'), function(el){
		goog.events.listen(el, goog.events.EventType.CLICK, function(event){
			//console.log('Hi ', el);
		});

	});
}

goog.exportSymbol('mapproject.start', mapproject.start);
//window['mapproject'] = mapproject;

function Foo1(name){
	//var doc = window['document'];
	//return doc.getElementByName(name);
	return [goog.dom.getElement(name), 'Русский текст'];
}
window['Foo1'] = Foo1;
//goog.exportSymbol('Foo1', Foo1);
