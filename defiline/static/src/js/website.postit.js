/*$(document).ready(function () {
	'use strict';
	$("div[id='postit-div']").each(function () {
	    var website = openerp.website,
	        qweb = openerp.qweb;
	 
	    qweb.add_template('/defiline/static/src/xml/website.postit.xml');
        
	    var self = this;
        openerp.jsonRpc('/get_postits','call', {
        	'session_lang': openerp.website.get_context().lang})
        .then(function(data) {
        	var self = this;
	        var postits = [];
	        $.each(data, function (e, postit) {
	            var obj = JSON.parse(postit);
	            postits.push(qweb.render("website.postit", {'postit': obj}));
	        });
	
	        if (!_.isEmpty(postits)) {
	        	$(postits).appendTo($("div[id='postit-wrapper']"));
	        }
        });
	});
});*/