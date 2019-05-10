$(document).ready(function(){
  $(document).on("click", ".paidButton", (function() {
    var id = $(this).prop('value');
    var row = $(this).closest('tr');
    $.post('/paid/', { killID: id, approved: true}, function(){
      row.fadeOut('fast', function() {
        row.remove();
      });
    });
    return false; // prevent default
  }));

  $(document).on("click", ".denyButton", (function() {
    var id = $(this).prop('value');
    var row = $(this).closest('tr');
    $.post('/paid/', { killID: id, approved: false }, function(){
      row.fadeOut('fast', function() {
        row.remove();
      });
    });
    return false; // prevent default
  }));

});
