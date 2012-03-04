$(function() {
  var $q = $(document.search.q);
  $q.focus();

  var typeahead = new Typeahead($q, '#results', '/?results');

  // Hide search button
  $("form input[type=submit]").hide();
  $q.css({
    width: '100%'
  });

  $('body').keypress(function(e) {
    if (e.which == 13) {
      // Enter key pressed. If there is exactly one search
      // result, follow it.
      var resultItems = $('#result-list li');
      if (typeahead.resultsTimeout == null && resultItems.size() == 1) {
        var href = resultItems.children('a').attr('href');
        window.location.href = href;
      } else {
        // Otherwise, start AJAX update immediately to
        // imitate submitting the search form.
        typeahead.startUpdate(1, $q.val());
      }
      return false;
    } else {
      return true;
    }
  });

});
