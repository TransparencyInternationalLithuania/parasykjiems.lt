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

  var typeahead = new Typeahead($q, '#content', '/threads/?bare', makeLinesClickable);
});
