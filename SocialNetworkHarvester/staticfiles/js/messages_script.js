function animateMessage(messageObj, hideTimeout) {
  if (hideTimeout == null) {
    hideTimeout = 4000;
  }
  messageObj.css('display', 'inline-block');
  messageObj.animate({
    height: 'auto',
  }, 300);
  if (hideTimeout > 0) {
    setTimeout(function () {
      $('.autoClose').each(function () {
        messageObj.fadeOut(1500);
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
  messages[0].map(function (item) {
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
  log(errors);
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
      '               class="dark_blue_link" >ici</a>' +
      '           pour afficher toute les erreurs.' +
      '       </span>' +
      '       <span class="message_closer">X</span>' +
      '   </div>' +
      '</div>';
    container.append(messageObj);

    var html = '';
    errors[0].map(function (error) {
      html += '<div class="error_container" style="display:block;position:relative;">' +
        '<div class="message_content">' + error + '</div></div>';
    });
    $('#multipleErrorsPopup #content').html(html);
  } else {
    errors[0].map(function (item) {
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
