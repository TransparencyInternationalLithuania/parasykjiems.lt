function Typeahead(q, results, url, resultsCallback, useHash, queryParam) {
  this.q = $(q);
  this.results = $(results);
  this.url = url;
  this.resultsCallback = resultsCallback || function(){};
  this.useHash = useHash;
  this.queryParam = queryParam || 'q';

  this.useHistory = this.browserSupportsHistory();
  this.resultsTimeout = null;
  this.resultsTerms = this.trim(this.q.val());

  if (this.useHash && (window.location.hash != "") || !this.useHistory) {
    var terms = decodeQuery(window.location.hash.slice(1));
    this.q.val(terms);
    this.startUpdate(1, terms);
  }

  var self = this;
  if (this.useHash || this.useHistory) {
    this.q.keyup(function() {
      self.startUpdate(1, self.q.val());
    });
  }
}

Typeahead.prototype = {
  browserSupportsHistory: function() {
    return !!(window.history && history.replaceState);
  },

  encodeQuery: function(q) {
    return encodeURI(q.replace(/ /g, '+'));
  },

  decodeQuery: function(q) {
    return decodeURI(q).replace(/\+/g, ' ');
  },

  setLocationTerms: function(terms) {
    if (this.useHistory) {
      var url;
      url = '?' + this.queryParam + '=' + this.encodeQuery(terms);
      history.replaceState(null, '', url);
    } else {
      if (terms == '') {
        window.location.replace('');
      } else {
        window.location.replace('#' + this.encodeQuery(terms));
      }
    }
  },

  fetchResults: function(terms) {
    var self = this;
    var data = {};
    data[this.queryParam] = terms;
    $.ajax({
      dataType: 'text',
      url: this.url,
      data: data,
      success: function(newResults) {
        self.results.html(newResults);
        self.results.fadeTo(0, 1);
        self.setLocationTerms(terms);
        self.resultsTerms = terms;
        self.resultsTimeout = null;
        self.resultsCallback();
      }
    });
  },

  trim: function(str) {
    return str.replace(/^\s+|\s+$/g, '');
  },

  startUpdate: function(delay, terms) {
    terms = this.trim(terms);
    if (terms == this.resultsTerms) return;
    if (this.resultsTimeout != null) {
      clearTimeout(this.resultsTimeout);
    }
    var self = this;
    this.resultsTimeout = setTimeout(function() {
      self.fetchResults(terms);
      self.resultsTimeout = null;
    }, 600);

    this.results.fadeTo(0, 0.5);
  },
};
