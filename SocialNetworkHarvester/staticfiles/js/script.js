$.getScript('/static/js/jquery.actual.min.js');
$.getScript('/static/js/jquery-ui.js');
$.getScript('/static/js/popup_script.js');

$(document).ready(function () {

  checkNavigator();

  setupLayout();

  $('#login_button').click(function () {
    toggleLoginMenu();
  });

  $('#analysis_box').click(function () {
    var toolMenu = $('#SubLeftMenu');
    toolMenu.slideToggle(300);
  });
  $('.yetToCome').each(function () {
    if (!DEBUG) {
      $(this).hide();
    }
    $(this).append(
      '<div class=\'yetToComeBox\'>' +
      'À venir...' +
      '</div>');
    var yetToComeBox = $(this).children('.yetToComeBox');
    yetToComeBox.css('top', $(this).height() / 2 - yetToComeBox.height() / 2);
    yetToComeBox.css('left', $(this).width() / 2 - yetToComeBox.width() / 2);
  }).mouseover(function () {
    var yetToComeBox = $(this).children('.yetToComeBox');
    yetToComeBox.css('top', $(this).height() / 2 - yetToComeBox.height() / 2);
    yetToComeBox.css('left', $(this).width() / 2 - yetToComeBox.width() / 2);
  });

  $('.error_container, .message_container').each(function () {
    animateMessage($(this));
  });

  $('body').on('click', '.message_closer', function (event) {
    $(event.target).parent().animate({
      height: '0px',
    }, 150, function () {
      $(this).hide();
    });
  });

  initMasonryLayout();
  initSearchBar();
});

var hideSearchBarTimeout = null;
var hideSearchBarDelay = 3000;

function initSearchBar() {
  setFocusListener();
  //log(window.location.href.split(/\?/))
  //$('#searchInput').val(window.location.);
  $('#searchIcon')
    .mouseenter(function () {
      clearTimeout(hideSearchBarTimeout);
      $('#searchInput').removeClass('collapsed');
    })
    .mouseleave(function () {
      clearTimeout(hideSearchBarTimeout);
      if (!$('#searchInput').is(':focus')) {
        hideSearchBarTimeout = setTimeout(function () {
          $('#searchInput').addClass('collapsed');
        }, hideSearchBarDelay);
      }
    })
    .click(function () {
      if (window.prevFocus.attr('id') == 'searchInput' &&
        $('#searchInput').val() != '') {
        $('#searchForm').submit();
      } else {
        $('#searchInput').focus();
      }
    });

  $('#searchInput')
    .focusin(function () {
      clearTimeout(hideSearchBarTimeout);
      $('#searchInput').removeClass('collapsed');
    })
    .focusout(function () {
      clearTimeout(hideSearchBarTimeout);
      hideSearchBarTimeout = setTimeout(function () {
        $('#searchInput').addClass('collapsed');
      }, hideSearchBarDelay);
    })
    .mouseenter(function () {
      clearTimeout(hideSearchBarTimeout);
    })
    .mouseleave(function () {
      clearTimeout(hideSearchBarTimeout);
      if (!$('#searchInput').is(':focus')) {
        hideSearchBarTimeout = setTimeout(function () {
          $('#searchInput').addClass('collapsed');
        }, hideSearchBarDelay);
      }
    });

  $('#searchForm').submit(function (event) {
    event.preventDefault();
    var val = $('#searchInput').val();
    val = val.replace(/[;,.\^<>\/\\]/g, '');
    var url = '/search?query=' + val;
    event.preventDefault();
    window.location.href = url;
  });
}

function setFocusListener() {
  window.prevFocus = $();
  $(document).on('focusin', 'input', function () {
    window.prevFocus = $(this);
  });
}

function setupLayout() {
  var menu = $('#side_menu');
  var OVERLAYING_TRESHOLD = 1200;

  if ($(window).width() <= OVERLAYING_TRESHOLD) {
    menu.hide();
  }
  setContentPaneWidth();

  $('#menu_select').click(function () {
    var overlaying = false;
    if (menu.css('display') != 'none') {
      menu.hide();
    } else {
      if ($(window).width() <= OVERLAYING_TRESHOLD) {
        overlaying = true;
        menu.bind('clickoutside', function () {
          hide_menu();
        });
        $('.left_menu_item:not(#analysis_box)').click(function () {
          hide_menu();
        });
        $('.sub_left_menu_item').click(function () {
          hide_menu();
        });
      }
      menu.show();

    }
    setContentPaneWidth(overlaying);
  });

  $(window).resize(function () {
    if ($(window).width() <= OVERLAYING_TRESHOLD) {
      menu.hide();
    } else if ($(window).width() >= OVERLAYING_TRESHOLD + 300) {
      menu.show();
    }
    setContentPaneWidth(false);
  });

  var head_banner_hide = null;
  $(window).scroll(function () {
    positionSideMenu();
  });

  function positionSideMenu() {
    var top = 43 - $(window).scrollTop();
    if (top < 0) {
      top = 0;
      $('#head_banner').css('position', 'fixed');
      $('#head_banner').hide();
      clearTimeout(head_banner_hide);
    }
    else {
      $('#head_banner').css('position', 'absolute');
      $('#head_banner').show();
    }
    menu.css('top', top + 'px');
  }

  $(window).on('mousemove', function (event) {
    clearTimeout(head_banner_hide);
    if (event.clientY <= 43) {
      $('#head_banner').show();
      menu.css('top', '43px');
    } else if ($(window).scrollTop() > 43) {
      head_banner_hide = setTimeout(function () {
        $('#head_banner').hide();
        menu.css('top', Math.max(43 - $(window).scrollTop(), 0) + 'px');
      }, 1000);
    }
  });
}

function checkNavigator() {
  //log("Detected browser: "+navigator.userAgent)
  if (navigator.userAgent.match('Version/5.1.7 Safari/')) {
    alert('Certaines fonction d\'Aspira ne sont pas supportées par Safari 5.1.7! Veuillez mettre votre navigateur à jour ou utiliser un autre navigateur.');
    window.location = '/supported_browsers_list';
  }
}

function animateMessage(messageObj, hideTimeout) {
  if (hideTimeout == null) {
    hideTimeout = 4000;
  }
  messageObj.css('display', 'inline-block');
  messageObj.animate({
    height: '16px',
  }, 300);
  if (hideTimeout > 0) {
    setTimeout(function () {
      $('.autoClose').each(function () {
        messageObj.fadeOut(600);
      });
    }, hideTimeout);
  }
}

function displayNewMessages(messages, hideTimeout) {
  var container = $('#messages_container_container');
  container.html('');
  if (typeof messages != 'array') {
    messages = [messages];
  }
  messages.forEach(function (item) {
    var messageObj = '' +
      '<div class="message_container_wrapper">' +
      '   <div class="message_container autoClose">' +
      '       <span class="message_content">' + item + '</span>' +
      '       <span class="message_closer">X</span> ' +
      '   </div>' +
      '</div>';
    container.append(messageObj);
  });
  container.find('.message_container').each(function () {
    animateMessage($(this), hideTimeout);
  });
}

function displayNewErrors(errors, hideTimeout) {
  var container = $('#messages_container_container');
  container.html('');
  if (typeof errors != 'array') {
    errors = [errors];
  }
  if (errors.length > 5) {
    var messageObj = '' +
      '<div class="message_container_wrapper">' +
      '   <div class="error_container autoClose">' +
      '       <span class="message_content">' +
      '           Erreurs multiples! cliquez ' +
      '           <a onclick="displayCenterPopup(\'multipleErrorsPopup\')"' +
      '               style="text-decoration: underline; color:blue; cursor:pointer">ici</a>' +
      '           pour afficher toute les erreurs.' +
      '       </span>' +
      '       <span class="message_closer">X</span>' +
      '   </div>' +
      '</div>';
    container.append(messageObj);

    var html = '';
    errors.forEach(function (error) {
      html += '<div class="error_container" style="display:block;position:relative;height:auto;">' +
        '<div class="message_content">' + error + '</div></div>';
    });
    $('#multipleErrorsPopup #content').html(html);
  } else {
    errors.forEach(function (item) {
      var messageObj = '' +
        '<div class="message_container_wrapper">' +
        '   <div class="error_container autoClose">' +
        '       <span class="message_content">' + item + '</span>' +
        '       <span class="message_closer">X</span> ' +
        '   </div>' +
        '</div>';
      container.append(messageObj);
    });
  }
  container.find('.error_container').each(function () {
    animateMessage($(this), hideTimeout);
  });
}

function setContentPaneWidth(overlaying) {
  var side_menu = $('#side_menu');
  var cont = $('#content_container');

  if (overlaying) {
    side_menu.css('box-shadow', '0px 5px 5px 5px #CCC');
  } else {
    side_menu.css('box-shadow', 'none');
  }

  if (side_menu.css('display') == 'none' || overlaying) {
    cont.width('100%');
    cont.css('margin-left', 'auto');
    cont.css('margin-right', 'auto');
  } else if (!overlaying) {
    cont.width($(window).width() - side_menu.width() - 30);
    cont.css('margin-left', side_menu.width() + 10);
    cont.css('margin-right', '0px');
  }
}

function hide_menu() {
  var menu = $('#side_menu');
  if (menu.attr('state') == '1') {
    menu.hide();
    menu.attr('state', '0');
    menu.unbind('clickoutside');
    $('.left_menu_item:not(#analysis_box)').unbind('click');
    $('.sub_left_menu_item').unbind('click');
  } else {
    menu.attr('state', '1');
  }
}

function log(str) {
  console.log(str);
}

function toggleLoginMenu() {
  var loginSection = $('#login_section');
  loginSection.unbind('clickoutside');
  loginSection.slideToggle(300, function () {
    if (loginSection.is(':visible')) {
      loginSection.bind('clickoutside', function () {
        toggleLoginMenu();
      });
    } else {
      loginSection.unbind('clickoutside');
    }
  });

  /*if (login.css('width') <= '0'){
      login.animate({width:'400px;'},300);
      login.bind("clickoutside", function(){toggleLoginMenu();});
      //login.show()
  } else {
      if (login.attr('state') == '1'){
          login.animate({width:'0px'},300);
          login.attr('state', '0');
          login.unbind("clickoutside");
          //login.hide()
      } else {
          login.attr('state', '1');
      }
  }*/
}

  function makeUrl(node, getParams) {
    /* Create an url from a source and a dict of GET params
     */
    var url = node;
    if (getParams != null) {
      if (url.search('\\?') < 0) {
        url += '?';
      } else {
        url += '&';
      }
      for (var key in getParams) {
        if (getParams.hasOwnProperty(key)) {
          url += key + '=' + getParams[key] + '&';
        }
      }
    }
    if (url.search('&') > 0) {
      url = url.substring(0, url.length - 1); // removes the last '&'
    }
    return url;
  }

  function tableToolLink(node, text, extention) {
    if (typeof extention === null) {
      extention = '';
    }
    ;
    return '<a href="' + node + '" class="dark_blue_link" ' + extention + '>' + text + '</a>';
  }


//######################################################################################################
  /*
   * jQuery outside events - v1.1 - 3/16/2010
   * http://benalman.com/projects/jquery-outside-events-plugin/
   *
   * Copyright (c) 2010 "Cowboy" Ben Alman
   * Dual licensed under the MIT and GPL licenses.
   * http://benalman.com/about/license/
   */
  (function ($, c, b) {
    $.map('click dblclick mousemove mousedown mouseup mouseover mouseout change select submit keydown keypress keyup'.split(' '), function (d) {
      a(d);
    });
    a('focusin', 'focus' + b);
    a('focusout', 'blur' + b);
    $.addOutsideEvent = a;

    function a(g, e) {
      e = e || g + b;
      var d = $(), h = g + '.' + e + '-special-event';
      $.event.special[e] = {
        setup: function () {
          d = d.add(this);
          if (d.length === 1) {
            $(c).bind(h, f);
          }
        }, teardown: function () {
          d = d.not(this);
          if (d.length === 0) {
            $(c).unbind(h);
          }
        }, add: function (i) {
          var j = i.handler;
          i.handler = function (l, k) {
            l.target = k;
            j.apply(this, arguments);
          };
        },
      };

      function f(i) {
        $(d).each(function () {
          var j = $(this);
          if (this !== i.target && !j.has(i.target).length) {
            j.triggerHandler(e, [i.target]);
          }
        });
      }
    }
  })(jQuery, document, 'outside');
//######################################################################################################

// WHEEL EVENT CONTROLLER
  (function (window, document) {
    var prefix = '', _addEventListener, support;
    if (window.addEventListener) {
      _addEventListener = 'addEventListener';
    }
    else {
      _addEventListener = 'attachEvent';
      prefix = 'on';
    }
    support = 'onwheel' in document.createElement('div') ? 'wheel' : document.onmousewheel !== undefined ? 'mousewheel' :
      'DOMMouseScroll';
    window.addWheelListener = function (elem, callback, useCapture) {
      _addWheelListener(elem, support, callback, useCapture);
      if (support == 'DOMMouseScroll') {
        _addWheelListener(elem, 'MozMousePixelScroll', callback, useCapture);
      }
    };

    function _addWheelListener(elem, eventName, callback, useCapture) {
      elem[_addEventListener]
      (prefix + eventName, support == 'wheel' ? callback : function (originalEvent) {
        !originalEvent && (originalEvent = window.event);
        var event = {
          originalEvent: originalEvent,
          target: originalEvent.target || originalEvent.srcElement,
          type: 'wheel',
          deltaMode: originalEvent.type == 'MozMousePixelScroll' ? 0 : 1,
          deltaX: 0,
          deltaZ: 0,
          preventDefault: function () {
            originalEvent.preventDefault ? originalEvent.preventDefault() : originalEvent.returnValue = false;
          },
        };
        if (support == 'mousewheel') {
          event.deltaY = -1 / 40 * originalEvent.wheelDelta;
          originalEvent.wheelDeltaX && (event.deltaX = -1 / 40 * originalEvent.wheelDeltaX);
        } else {
          event.deltaY = originalEvent.detail;
        }
        return callback(event);
      }, useCapture || false);
    }
  })
  (window, document);


  function truncate_text(text, maxChars, elipsis) {
    if (text == null) {
      return '';
    }
    if (maxChars == null || maxChars < 10) {
      maxChars = 100;
    }
    if (elipsis == null) {
      elipsis = false;
    }
    if (text.length >= maxChars && elipsis) {
      maxChars -= 6; // We add 6 characters if ellipsis is true (" [...]"). Insures character limit is met
    } else {
      elipsis = false;
    }
    var truncatedText = text.substring(0, Math.min(maxChars, text.length));
    if (elipsis) {
      truncatedText = '<div title="' + text + '">' + truncatedText + ' <i>[...]</i></div>';
    }
    return truncatedText;
  }

  function initMasonryLayout() {
    $.getScript('/static/js/masonry.pkgd.min.js', function () {
      $('.grid').masonry({
        itemSelector: '.grid-item',
        columnWidth: '.grid-sizer',
        fitWidth: true,
        transitionDuration: '200ms',
      });
    });
  }

  debounced_functions = {};

  function debounce(fct, timeout) {
    if (debounced_functions[fct]) {
      clearTimeout(debounced_functions[fct]);
    }
    debounced_functions[fct] = setTimeout(fct, timeout);
  };


