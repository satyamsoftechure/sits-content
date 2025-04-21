from django.contrib import admin
from .models import BlogPost, CustomUser
from .forms import BlogGeneratorForm

admin.site.register(BlogPost)

admin.site.register(CustomUser)