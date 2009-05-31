
(function($){
  function fetch_wiki(elems, options) {
    var titles = $(elems).map(function() { 
      return options.wiki_title(options.name($(this)));
    });
    var url = options.wiki_url;
    jQuery.getJSON(url, { 'titles': jQuery.makeArray(titles) }, 
      function(json) {

      $(elems).each(function() {
        var name = options.wiki_title(options.name($(this)));
        var content = json.result[name]
        if (content == undefined) return;
        $(this).qtip({
          content: content,
          position: {
              corner: {
                  target: 'leftTop',
                  tooltip: 'rightTop'
              }
          },
          style: {
            tip: 'rightTop',
            name: 'cream'
          }
        });
      });
    });
  }
  $.fn.wikiImagify = function(options) {
    var defaults = {
      name: function(e) { return 'a sample name'; },
      wiki_title: function(title) { return title; },
      google_query: function(title) { return title; },
      wiki_url: '/twit-miner/wiki/',
      pics_url: '/twit-miner/pics/'
    };
    var options = $.extend(defaults, options);

    var elems = $(this);
    var titles = $(this).map(function() {
      return options.google_query(options.name($(this)));
    });
    var url = options.pics_url;
    jQuery.getJSON(url, { 'queries': jQuery.makeArray(titles) }, 
      function(json) {

      $(elems).each(function() {
        var name = options.google_query(options.name($(this)));
        var img = json.result[name];
        $(this).append('<img src="' + img + '" />');
        var wiki_name = options.wiki_title(options.name($(this)));
        $(this).children('img').wrap(
            '<a href="http://en.wikipedia.org/wiki/' + 
            wiki_name + '"></a>'
        );
      });
    });
    return fetch_wiki($(this), options);
  };
})(jQuery);
