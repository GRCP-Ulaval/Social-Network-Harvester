"""SocialNetworkHarvester_v1p0 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from AspiraUser.views import (
    addRemoveItemById,
    removeSelectedItems,
    userLogin,
    userRegister,
    userLogout,
    editUserSettings,
    confAgreement,
    browserList,
    updatePW,
    requestResetPW,
    userDashboard,
    userLoginPage,
    userSettings,
    resetPWPage,
    search
)

urlpatterns = [
    url(r'^$', userDashboard),
    url(r'^login$', userLogin),
    url(r'^register', userRegister),
    url(r'^login_page$', userLoginPage),
    url(r'^logout$', userLogout),
    url(r'^settings$', userSettings),
    url(r'^edit_user_settings$', editUserSettings),
    url(r'^removeSelectedItems', removeSelectedItems),
    url(r'^confidentialityAgreement', confAgreement),
    url(r'^supported_browsers_list', browserList),
    url(r'^forms/updatePW', updatePW),
    url(r'^forms/resetPW$', requestResetPW),
    url(r'^forms/resetPW/(?P<token>[\w\.]+)', resetPWPage),
    url(r'^forms/manageHarvestList/(?P<addRemove>[\w\.]+)', addRemoveItemById),
    url(r'^search', search),
]
