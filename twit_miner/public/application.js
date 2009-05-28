
(function($){
  function fetch_wiki(elems, options) {
    var blub = elems;
    var titles = $(elems).map(function() { 
      return options.name($(this)) + ' (film)'; 
    });
    var url = '/wiki/';
    jQuery.getJSON(url, { 'titles': jQuery.makeArray(titles) }, 
      function(json) {

      $(blub).each(function() {
        var name = options.name($(this));
        name += ' (film)';
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
        $(this).children('img').wrap(
            '<a href="http://en.wikipedia.org/wiki/' + name + '"></a>'
        )
      });
    });
  }
  $.fn.wikiImagify = function(options) {
    var defaults = {
      name: function(e) { return 'a sample name' }
    };
    var options = $.extend(defaults, options);

    $(this).each(function() {
      var query = encodeURIComponent(options.name($(this)) + ' movie poster');
      var url =
        'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=';
      url += query + '&callback=?';
      var image = $(this);
      jQuery.getJSON(url, null, function(e) {
        if (e.responseStatus != 200) return;
        var result_url = e.responseData.results[0].tbUrl;
        $(image).append('<img src="' + result_url + '" />');
        //fetch_wiki($(image), options);
      });
    });
    return fetch_wiki($(this), options);
  };
})(jQuery);
