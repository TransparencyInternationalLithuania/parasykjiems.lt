function browserSupportsHistory() {
    return !!(window.history && history.replaceState);
}

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

function trim(str) {
    return str.replace(/^\s+|\s+$/g, '');
}

function startUpdate(delay, terms) {
    terms = trim(terms);
    if (terms == resultsTerms) return;
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

      if (browserSupportsHistory()) {
          // Hide search button
          $("form submit").hide();
          q.css({width: '100%'});

          resultsTerms = trim(q.val());

          q.keyup(
              function(e) {
                  // Key pressed, so maybe we should update the
                  // search results.
                  var terms = q.val();
                  startUpdate(600, terms);
              });

          $('body').keypress(
              function(e) {
                  if (e.which == 13) {
                      // Enter key pressed. If there is exactly one search
                      // result, follow it.
                      var resultItems = $('#result-list li');
                      if (resultsTimeout == null && resultItems.size() == 1) {
                          var href = resultItems.children('a').attr('href');
                          window.location.href = href;
                      } else {
                          // Otherwise, start AJAX update immediately to
                          // imitate submitting the search form.
                          startUpdate(1, q.val());
                      }
                      return false;
                  } else {
                      return true;
                  }
              }
          );
      }

  }
 );
