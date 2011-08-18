function encodeQuery(q) {
    return encodeURI(q.replace(/ /g, '+'));
}

function fetchResults(terms) {
    var results = $('#results');
    $.ajax({
               dataType: 'text',
               url: 'results/',
               data: { q: terms },
               success: function(newResults) {
                   results.html(newResults);
                   var url;
                   if (terms == '') {
                       url = '/';
                   } else {
                       url = '/?q=' + encodeQuery(terms);
                   }
                   history.replaceState(null, '', url);
                   results.removeClass('updating');
                   resultsTerms = terms;
                   resultsTimeout = null;
               }
           });
}

var resultsTimeout = null;
var resultsTerms = '';

function startUpdate(delay, terms) {
    if (resultsTimeout != null) {
        clearTimeout(resultsTimeout);
    }
    resultsTimeout = setTimeout(
        function() {
            fetchResults(terms);
            clearTimeout(resultsTimeout);
        },
        600
    );
    $('#results').addClass('updating');
}

$(function() {
      var q = $(document.search.q);
      q.focus();
      q.css({width: '100%'});

      q.keyup(
          function(e) {
              // Key pressed, so maybe we should update the
              // search results.
              var terms = q.val();
              if (terms != resultsTerms) {
                  startUpdate(600, terms);
              }
          });

      $('body').keypress(
          function(e) {
              if (e.which == 13) {
                  // Enter key pressed. If there is exactly one search
                  // result, follow it.
                  var resultItems = $('#result-list li');
                  if (resultItems.size() == 1) {
                      var href = resultItems.children('a').attr('href');
                      window.location.href = href;
                  } else {
                      // Otherwise, start AJAX update immediately to
                      // imitate submittin the search form.
                      startUpdate(1, q.val());
                  }
                  return false;
              } else {
                  return true;
              }
          }
      );

  }
 );
