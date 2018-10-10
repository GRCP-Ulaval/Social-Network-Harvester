from django.conf.urls import url

from .views.forms import formBase
from .views.pages import *

urlpatterns = [
    url(r'^$', facebookBase),
    url(r'^user/(?P<FBUserId>[\w\.]+)$', fbUserView),
    url(r'^page/(?P<FBPageId>\w+)$', fbPageView),
    url(r'^post/(?P<FBPostId>[\w\.]+)$', fbPostView),
    url(r'^comment/(?P<fbCommentId>\w+)$', fbCommentView),

    url(r'^apilogin/?$', APILoginPage),
    url(r'forms/(?P<formName>[\w\.]+)', formBase),

    # ajax
]
