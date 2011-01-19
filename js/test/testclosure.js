goog.require('goog.dom');
goog.require('goog.dom.query');
goog.require('goog.events');
goog.require('goog.events.EventType');

function sayHi() {
	var $q = goog.dom.query;

	var newHeader = goog.dom.createDom('h1', {'style': 'background-color:#EEE'}, 'Hello world!');
	goog.dom.appendChild(document.body, newHeader);

	goog.array.forEach(goog.dom.query('h1 a'), function(el){
		goog.events.listen(el, goog.events.EventType.CLICK, function(event){
			console.log('Hi ', el);
		});

	});
}
