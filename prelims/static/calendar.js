var mouseDown = 0;
var paintOn = false;
var paintOff = false;

function cal_is_busy(ctx) {
  return $(ctx).hasClass('busy_time_slot');
}

function cal_is_free(ctx) {
  return $(ctx).hasClass('time_slot') && !$(ctx).hasClass('busy_time_slot');
}

function doPaint(ctx) {
  if ($(ctx).hasClass("disable_time_slot")) return;
  if ($(ctx).hasClass("lock_time_slot")) return;

  if (!$(ctx).hasClass("ts_changed")) {
    ctx.was_busy = $(ctx).hasClass('busy_time_slot');
    $(ctx).addClass("ts_changed");
    console.log(ctx);
  }

  if (paintOn) {
    $(ctx).addClass("busy_time_slot");
  } else if (paintOff) {
    $(ctx).removeClass("busy_time_slot");
  }
}

$("body").on("mousedown", function() {
  ++mouseDown;
});

$("td").on("mousedown", function() {
  if (!mouseDown) {
    if (cal_is_busy(this)) {
      paintOff = true;
    } else if (cal_is_free(this)) {
      paintOn = true;
    }
    doPaint(this);
  }
});

$("body").on("mouseup", function() {
  --mouseDown;
  if (!mouseDown) {
    paintOn = false;
    paintOff = false;
  }
});

$("td").on("mouseover", function() {
  doPaint(this);
});
