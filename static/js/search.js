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
               }
           });
}

var resultsTimeout = null;

$(function() {
      var q = $(document.search.q);
      q.focus();
      q.css({width: '100%'});

      q.keyup(function() {
                  if (resultsTimeout) {
                      clearTimeout(resultsTimeout);
                  }
                  resultsTimeout = setTimeout(function() {
                                                  fetchResults(q.val());
                                                  clearTimeout(resultsTimeout);
                                              }, 600);
              });
  });
