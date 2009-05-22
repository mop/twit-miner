
(function($){
  function fetch_wiki(img, options) {
    var title = options.name;
    var query = encodeURIComponent(title + ' (film)');
    var url = '/wiki/' + query;
    jQuery.getJSON(url, null, function(e) {
      $(img).qtip({
        content: e.result,
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
      $(img).children('img').wrap(
          '<a href="http://en.wikipedia.org/wiki/' + query + '"></a>'
      )
    });
  }
  $.fn.wikiImagify = function(options) {
    var defaults = {
      name: 'a sample name'
    };
    var options = $.extend(defaults, options);

    return $(this).each(function() {
      var query = encodeURIComponent(options.name + ' movie poster');
      var url =
        'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=';
      url += query + '&callback=?';
      var image = $(this);
      jQuery.getJSON(url, null, function(e) {
        if (e.responseStatus != 200) return;
        var result_url = e.responseData.results[0].tbUrl;
        $(image).append('<img src="' + result_url + '" />');
        fetch_wiki($(image), options);
      });
    });
  };
})(jQuery);
