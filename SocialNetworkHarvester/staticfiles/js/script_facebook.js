FB = null;

(function (d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s);
  js.id = id;
  js.src = 'https://connect.facebook.net/fr_CA/sdk.js#xfbml=1&version=' + facebookAppVersion;
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));

function checkLoginState() {
  FB.getLoginStatus(function (response) {
    statusChangeCallback(response);
  });
}

function statusChangeCallback(response) {
  if (response.status === 'connected') {
    accessToken = response.authResponse.accessToken;
    updateStoredToken(accessToken, function (response) {
      display_user_infos(accessToken);
    });
  } else if (fbAccessToken) {
    updateStoredToken(null, function (response) {
    });
    $('#notLoggedInMessage').show();
    $('#login_infos_container').hide();
  }
}

function updateStoredToken(accessToken, callback) {
  $.ajax({
    type: 'POST',
    url: '/facebook/forms/setFacebookToken',
    data: {
      fbToken: accessToken,
      csrfmiddlewaretoken: csrf_token,
    },
    success: function (response) {
      if (response.code !== 200) {
        displayNewErrors(['Un problème est survenu lors de votre identification avec Facebook.']);
      } else if (accessToken) {
        displayNewMessages(['Votre compte Facebook est enregistré. Vous pouvez maintenant commencer votre collecte.']);
      } else {
        displayNewMessages(['Vous êtes maintenant déconnecté de Facebook.']);
      }
      callback(response);
    },
  })
}

function display_user_infos(accessToken) {
  if (accessToken) {
    FB.api('/me?fields=id,name,picture.type(large)&access_token=' + accessToken, function (response) {
      if (response['error'] != null) {
        $('#tokenErrorMarker').show();
        $('#notLoggedInMessage').show();
        $('#login_infos_container').hide();
      } else {
        $('#userImg').attr('src', response.picture.data.url);
        $('#user_name').html(response.name);
        $('#notLoggedInMessage').hide();
        $('#login_infos_container').show();
        $('#tokenErrorMarker').hide();
      }
    });
  } else {
    $('#notLoggedInMessage').show();
    $('#login_infos_container').hide();
  }
}

window.fbAsyncInit = function () {
  FB.init({
    appId: facebookAppId,
    xfbml: true,
    version: facebookAppVersion,
    status: true,
  });
  if (!fbAccessToken) {
    checkLoginState();
  }
  display_user_infos(fbAccessToken);
};


