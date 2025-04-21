from django.shortcuts import render, redirect
from .models import BlogPost
from .forms import BlogGeneratorForm
from django.contrib.auth.decorators import login_required
from .utils import (
    generate_blog_content,
    generate_image,
    check_plagiarism,
    remove_plagiarism,
    gemini_paraphrase,
)
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings


def index(request):
    form = BlogGeneratorForm()
    return render(request, "generate_blog.html", {"form": form})

@csrf_exempt
def generate_blog(request):
    if request.method == "POST":
        form = BlogGeneratorForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            keywords = form.cleaned_data["keywords"]
            content = generate_blog_content(title, keywords)
            image_url = generate_image(title)

            if content:
                return render(
                    request,
                    "blog_detail.html",
                    {
                        "blog_post": {
                            "title": title,
                            "keywords": keywords,
                            "content": content,
                            "image_url": image_url,
                        },
                        "is_draft": True,
                    },
                )
            else:
                form.add_error(
                    None, "Generated content is not unique. Please try again."
                )
    else:
        form = BlogGeneratorForm()

    return render(request, "generate_blog.html", {"form": form})


def blog_detail(request):
    return


@login_required
@csrf_exempt
def save_draft(request):
    if request.method == "POST":
        title = request.POST.get("title")
        keywords = request.POST.get("keywords")
        content = request.POST.get("content")
        image_url = request.POST.get("image_url")
        user = request.user

        existing_draft = BlogPost.objects.filter(content=content, user=user).first()

        if existing_draft:
            return JsonResponse({"message": "You have already saved this draft."})
        else:
            blog_post = BlogPost.objects.create(
                title=title,
                keywords=keywords,
                content=content,
                image_url=image_url,
                user=user,
            )
            return JsonResponse({"message": "Saved draft successfully !"})

    return JsonResponse({"message": "Invalid request method."})

@csrf_exempt
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "username": username, "message": "Login successfully !"})
        else:
            return JsonResponse({"message": "Invalid credentials"}, status=400)
    return render(request, "login.html")


def login_form(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "message": "The username or password you entered is incorrect."})
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"success": False, "message": "Username is already taken."})

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"success": False, "message": "Invalid email address."})
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email is already registered."})

        if password != confirm_password:
            return JsonResponse({"success": False, "message": "Passwords do not match."})

        user = User.objects.create_user(username, email, password)
        login(request, user)
        return JsonResponse({"success": True, "message": "Register successfully !"})
    return render(request, "register.html")

def register_form(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if User.objects.filter(username=username).exists():
            return JsonResponse({"success": False, "message": "Username is already taken."})

        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"success": False, "message": "Invalid email address."})
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Email is already registered."})

        if password != confirm_password:
            return JsonResponse({"success": False, "message": "Passwords do not match."})

        user = User.objects.create_user(username, email, password)
        login(request, user)
        return JsonResponse({"success": True, "message": "User registered successfully."})

    return render(request, "register.html")


@login_required
def my_drafts(request):
    user = request.user
    drafts = BlogPost.objects.filter(user=user)  # Retrieve drafts for the current user
    return render(request, "my_drafts.html", {"drafts": drafts})


@login_required
def view_draft(request, pk):
    user = request.user
    draft = BlogPost.objects.get(pk=pk, user=user)
    return render(request, "view_draft.html", {"draft": draft})


@login_required
@require_POST
@csrf_exempt
def delete_draft(request, pk):
    user = request.user
    draft = get_object_or_404(BlogPost, pk=pk, user=user)
    draft.delete()
    return JsonResponse({"status": "success"})


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No user found with this email address.'})

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Create password reset link
        reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"

        # Send email with reset link
        send_mail(
            'Password Reset Request',
            f'Click the following link to reset your password: {reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return JsonResponse({'success': True, 'message': 'Password reset link has been sent to your email.'})

    return render(request, 'forgot_password.html')

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password != confirm_password:
                return JsonResponse({'success': False, 'message': 'Passwords do not match.'})

            user.set_password(new_password)
            user.save()
            return JsonResponse({'success': True, 'message': 'Password has been reset successfully.'})

        return render(request, 'reset_password.html')
    else:
        return JsonResponse({'success': False, 'message': 'Invalid password reset link.'})
