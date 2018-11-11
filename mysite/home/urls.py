from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import handler400, handler403, handler404, handler500

urlpatterns = [
    path('', views.index, name="index"),
    path('signin/', auth_views.login, {"template_name": "home/signin.html"}, name="signin"),
    path('signout/', auth_views.logout, {"next_page": "/"}, name="logout"),
    path('register/', views.register, name="register"),
    path('u/<user_name>/', views.profile, name="profile"),
    path('u/', views.profile, name="profile_self"),
    path('changeemail/', views.changeemail, name="change_email"),
    path('verify_email/send', views.send_verification),
    path('verify_email/<activation_code>/', views.activate_email),
    path('post/submit/', views.submit_post, name="post_submit"),
    path('post/<postid>/', views.fetchpost, name="fetchpost"),
    path('getposts/', views.getPosts, name="getPosts")
]
'''
handler400 = 'home.views.bad_request'
handler403 = 'home.views.permission_denied'
handler404 = 'home.views.page_not_found'
handler500 = 'home.views.server_error'
'''
