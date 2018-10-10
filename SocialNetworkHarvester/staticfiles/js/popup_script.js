$(document).ready(function () {
  $('#centerPopupCloser').click(function () {
    closeCenterPopup();
    lastPopupId = null;
  });
  $('body').on('mouseover', '#centerPopupHelper', function (event) {
    $('#centerPopupHelpText').position({
      my: 'right-10 bottom-10',
      of: event,
      collision: 'fit',
      within: $('#centerPopupOutter'),
    });
    $('#centerPopupHelpText').css('display', 'block');
  });
  $('body').on('mouseout', '#centerPopupHelper', function () {
    $('#centerPopupHelpText').removeAttr('style');
  });

  var inner = $('#centerPopupInner');
  addWheelListener($('#centerPopupOutter')[0], function (event) {
    event.preventDefault();
    event.stopPropagation();
    if (inner.height() > $(window).height()) {
      var val = parseInt(inner.css('marginTop'), 10);
      val -= event.deltaY * 10;
      var maxOffset = 30;
      if (val > maxOffset) {
        val = maxOffset;
      }
      var min = inner.height() - $('#centerPopupOutter').height();
      if (val < -min - maxOffset) {
        val = -min - maxOffset;
      }
      inner.css('marginTop', val);
    }
  });
});

var lastPopupId = null;

function closeCenterPopup() {
  var outterPopup = $('#centerPopupOutter');
  var innerPopup = $('#centerPopupInner');
  if (outterPopup.css('display') == 'block') {
    innerPopup.css('overflow', 'hidden')
      .animate({
        height: 0,
      }, 150, function () {
        innerPopup.removeAttr('style');
        outterPopup.removeAttr('style');
        outterPopup.hide();
        innerPopup.unbind('clickoutside');
      });
  }
}

function displayCenterPopup(containerId, afterFunction) {
  var container = $('#' + containerId);
  var innerPopup = $('#centerPopupInner');
  if (containerId != lastPopupId) {
    //log('new popup')
    lastPopupId = containerId;
    $('#centerPopupTitle').html(container.children('#title').html());
    $('#centerPopupHelpText').html(container.children('#help').html());
    //log(container.children('#content').html())
    $('#centerPopupContent').html(container.children('#content').html());
  }
  var scriptTag = container.children('#functions');
  eval(scriptTag.text());
  var innerHeight = innerPopup.actual('height');
  innerPopup.css({
    overflow: 'hidden',
    height: 0,
  });
  $('#centerPopupOutter').show();
  innerPopup.animate({
    height: innerHeight,
  }, 150, function () {
    innerPopup.removeAttr('style');
    innerPopup.bind('clickoutside', function (event) {
      if (event.target.id == 'centerPopupOutter' ||
        event.target.id == 'centerPopupOutterTD') {
        closeCenterPopup();
      }
    });
    if (afterFunction != null) {
      afterFunction();
    }
  });
}

function getPopupContainer() {
  return $('#centerPopupOutter table tr td #centerPopupInner #centerPopupContent');
}
