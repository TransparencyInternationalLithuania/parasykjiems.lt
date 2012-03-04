$(function() {
  function makeLinesClickable() {
    $('.threads tr a').each(function(i, a) {
      var $a = $(a);
      $a.parent().parent().click(function(e) {
        window.location = $a.attr('href');
      });
    });
  };
  makeLinesClickable();

  var $q = $('.filter input[name=q]');
  function resetq() {
    if ($q.val() == '') {
      $q.val(window.EMPTY_FILTER);
      $q.addClass('empty');
    }
  }
  resetq();
  $q.blur(resetq);
  $q.focus(function(e) {
    if ($q.val() == window.EMPTY_FILTER) {
      $q.val('');
      $q.removeClass('empty');
    }
  });

  function setRSS(q) {
    var url = 'rss.xml?q=' + q;
    $('.rss-button a').attr('href', url);
    $('link[rel="alternate"]').attr('href', url);
  }

  var typeahead = new Typeahead($q, '#content', '/threads/?bare', function() {
    makeLinesClickable();
    setRSS(this.encodeQuery(this.resultsTerms));
  }, false);
});
