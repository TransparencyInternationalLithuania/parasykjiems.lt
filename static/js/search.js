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

$(function() {
      var q = $(document.search.q);
      q.focus();
      q.css({width: '100%'});

      var results = $('#results');

      q.keyup(function() {
                  var terms = q.val();
                  if (terms != resultsTerms) {
                      if (resultsTimeout != null) {
                          clearTimeout(resultsTimeout);
                      }
                      resultsTimeout = setTimeout(
                          function() {
                              fetchResults(q.val());
                              clearTimeout(resultsTimeout);
                          },
                          600
                      );
                      results.addClass('updating');
                  }
              });
  });
