from django.urls import path
from content_creator import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('generate-blog/', views.generate_blog, name='generate_blog'),
    path('blog/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('save_draft/', views.save_draft, name='save_draft'),
    path("login/", views.login_view, name="login"),
    path("login_form/", views.login_form, name="login_form"),
    path("register_form/", views.register_form, name="register_form"),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path("my_drafts/", views.my_drafts, name="my_drafts"),
    path("my_drafts/<pk>/", views.view_draft, name="view_draft"),
    path('delete_draft/<int:pk>/', views.delete_draft, name='delete_draft'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', views.reset_password, name='reset_password'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)