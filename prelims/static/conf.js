/* Global jQuery options */

/* setup bootstrap-editable for inline edits */
$.fn.editable.defaults.mode = 'inline';

$(document).ready(function() {
  /* Make default faculty selection blank */
  $(".schedule_faculty").prop('selectedIndex', -1);

  /* Setup AJAX form for adding new prelims */
  var add_prelim_form_options = {
    success:    add_prelim_form_success,
    clearForm:  true,
    dataType:   'json'
  };
  $(".add_prelim_form").ajaxForm(add_prelim_form_options);

  add_delete_form_hooks();
  add_title_edit_hooks();
  add_pdf_upload_hooks();
});

function add_delete_form_hooks() {
  var delete_unscheduled_prelim_form_options = {
    success:    delete_unscheduled_prelim_form_success,
    dataType:   'json'
  };
  $(".delete_unscheduled_prelim_form").ajaxForm(delete_unscheduled_prelim_form_options);
}

function add_prelim_form_success(data, statusText, xhr, $form) {
  var p = $("#event_"+data['event_id']+"_add_prelim_error_text");
  if (data['success']) {
    $("#event_"+data['event_id']+"_unscheduled_entries").append(data['html']);
    add_delete_form_hooks();
    add_title_edit_hooks();
    add_pdf_upload_hooks();
    p.html("<strong>Success:</strong> Added " + data['student'])
    p.parent().toggleClass('alert-danger', false);
    p.parent().toggleClass('alert-success', true);
  } else {
    p.html("<strong>Error:</strong> " + data['msg']);
    p.parent().toggleClass('alert-success', false);
    p.parent().toggleClass('alert-danger', true);
    console.log(data['msg']);
  }
  p.parent().show();
  p.parent().delay(10000).fadeOut(1000);
}

function delete_unscheduled_prelim_form_success(data) {
  $("#event_"+data['event_id']+"_unscheduled_"+data['student']).remove();
  console.log('delete unscheduled');
  console.log(data);
  console.log("#event_"+data['event_id']+"_unscheduled_"+data['student']);
}

function add_title_edit_hooks() {
  /* Setup editable fields for prelims */
  $('.prelim_title').editable({
    success: function(response, newValue) {
      if (response.status == 'error') return response.msg;
    },
    error: function(response, newValue) {
      if (response.status === 500) {
        return 'Temporary server error. Please try again later.';
      } else {
        return response.responseText;
      }
    }
  });
}

function add_pdf_upload_hooks() {
  /* Support for uploading for prelim pdfs */
  $('.upload_prelim_pdf').on('fileselect', function() {
    console.log("fileselect hook");
    var formData = new FormData($(this).closest('form')[0]);
    console.log(formData);
    $.ajax({
      url: 'update_prelim_pdf',
      type: 'POST',
      data: formData,
      cache: false,
      contentType: false,
      processData: false,
      success: function(data) {
        console.log('upload_prelim_pdf success callback');
        if (data['status'] == 'success') {
          var url = $('#' + data['event_id'] + '_' + data['prelim_id'] + '_paper_url');
          var msg = $('#' + data['event_id'] + '_' + data['prelim_id'] + '_paper_url_msg');
          console.log(url);
          console.log(msg);
          $(url).empty();
          var newlink = $("<a />", {
            href : data['url'],
            text : data['text']
          });
          $(url).append(newlink);
          $(msg).empty();
          var newp = $("<p />", {
            text : data['msg']
          });
          $(newp).css('color', 'green');
          $(msg).append(newp);
          $(msg).delay(2000).fadeOut('slow');
        } else {
          alert('File upload failed for an unknown reason. Sorry.');
        }
      }
    });
  });
}
