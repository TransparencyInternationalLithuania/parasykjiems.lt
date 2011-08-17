$(function() {
      // Focus search box.
      var q = document.search.q;
      q.focus();
      
      // Setup autocomplete.
      $(q).autocomplete({source: "autocomplete"})
});
