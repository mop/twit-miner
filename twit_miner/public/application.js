
(function($){
  function fetch_wiki(elems, options) {
    var titles = $(elems).map(function() { 
      return options.wiki_title(options.name($(this)));
    });
    var url = '/wiki/';
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
      google_query: function(title) { return title; }
    };
    var options = $.extend(defaults, options);

    $(this).each(function() {
      var query = encodeURIComponent(
        options.google_query(options.name($(this)))
      );
      var url =
        'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=';
      url += query + '&callback=?';
      var image = $(this);
      jQuery.getJSON(url, null, function(e) {
        if (e.responseStatus != 200) return;
        var result_url = e.responseData.results[0].tbUrl;
        $(image).append('<img src="' + result_url + '" />');
        //fetch_wiki($(image), options);
        var name = options.wiki_title(options.name($(image)));
        $(image).children('img').wrap(
            '<a href="http://en.wikipedia.org/wiki/' + name + '"></a>'
        )
      });
    });
    return fetch_wiki($(this), options);
  };
})(jQuery);
