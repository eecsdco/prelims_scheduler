/* General support routines */

$(".valid-if-any-text").on("change", function() {
    //var valid_div = $(this).parent(".has-success, .has-error");
    var valid_div = $(this).closest('div.has-error, div.has-success')
    console.log('valid_div');
    console.log(valid_div);
    if (this.value.length == 0) {
      console.log('valid-if-any-text -> error');
      valid_div.toggleClass('has-success', false);
      valid_div.toggleClass('has-error', true);
    } else {
      console.log('valid-if-any-text -> success');
      valid_div.toggleClass('has-error', false);
      valid_div.toggleClass('has-success', true);
    }
    console.log(valid_div);
});

/* TODO: This is available-centric and should be more generic */
/* TODO: Also, this is a really crappy way of implementing this */
$(".cal_watch_check").change(function() {
  console.log(".cal_watch_check onchange for " + this.value);
  /* TODO: This doesn't filter by event_id, but should */

  var fn_to_apply;
  if ($(this).is(":checked")) {
    fn_to_apply = function(val) { return val + 1; }
  } else {
    fn_to_apply = function(val) { return val - 1; }
  }

  $(".fac_free_"+this.value).each(function(index) {
    if (!("free_cnt" in this)) {
      this.free_cnt = 0;
    }
    if (!("unmarked_cnt" in this)) {
      this.unmarked_cnt = 0;
    }
    this.free_cnt = fn_to_apply(this.free_cnt);
    if ((this.free_cnt > 0) && (this.unmarked_cnt == 0)) {
      $(this).addClass("free_time_slot");
    } else {
      $(this).removeClass("free_time_slot");
    }
  });

  $(".fac_unmarked_"+this.value).each(function(index) {
    if (!("free_cnt" in this)) {
      this.free_cnt = 0;
    }
    if (!("unmarked_cnt" in this)) {
      this.unmarked_cnt = 0;
    }
    this.unmarked_cnt = fn_to_apply(this.unmarked_cnt);
    if ((this.free_cnt > 0) && (this.unmarked_cnt == 0)) {
      $(this).addClass("free_time_slot");
    } else {
      $(this).removeClass("free_time_slot");
    }
  })
});

$(document).on('change', '.btn-file :file', function() {
  console.log('on change btn file');
  var input = $(this);
  var numFiles = input.get(0).files ? input.get(0).files.length : 1;
  var label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
  console.log(input);
  console.log(numFiles);
  console.log(label);
  input.trigger('fileselect', [numFiles, label]);
});
