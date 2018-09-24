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
    log('getLoginStatus response: ');
    log(response);
    statusChangeCallback(response);
  });
}

function statusChangeCallback(response) {
  console.log('statusChangeCallback');
  if (response.status === 'connected') {
    accessToken = response.authResponse.accessToken;
    updateStoredToken(accessToken, function (response) {
      log('Logged in into facebook and stored token.');
      display_user_infos(accessToken);
    });
  } else {
    updateStoredToken(null, function (response) {
      log('Logged out of Facebook and deleted access token');
    });
    $('#notLoggedInMessage').show();
    $('#login_infos_container').hide();
  }
}

function updateStoredToken(fbAccessToken, callback) {
  $.ajax({
    type: 'POST',
    url: '/facebook/forms/setFacebookToken',
    data: {
      fbToken: fbAccessToken,
      csrfmiddlewaretoken: csrf_token,
    },
    success: function (response) {
      callback(response);
    },
  });
}

function display_user_infos(accessToken) {
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

}

window.fbAsyncInit = function () {
  FB.init({
    appId: facebookAppId,
    xfbml: true,
    version: facebookAppVersion,
    status: true,
  });
  checkLoginState();
};


