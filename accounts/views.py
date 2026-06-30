from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from badges.models import UserBadge

from .forms import RegisterForm, LoginForm, ProfileUpdateForm, ChangePasswordForm
from .models import Follow, ReputationHistory


def try_email_login(request):
    """Authenticate when a user enters an email instead of a username."""
    email = request.POST.get('username', '')
    password = request.POST.get('password', '')

    if '@' not in email:
        return None

    account = User.objects.filter(email=email).first()
    if not account:
        return None

    return authenticate(
        request,
        username=account.username,
        password=password,
    )


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                login(request, user)
            messages.success(request, f'Welcome to Stack Overflow, {user.username}!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            remember_me = form.cleaned_data.get('remember_me')
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            user = try_email_login(request)
            if user:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect(request.GET.get('next', 'home'))

            messages.error(request, 'Invalid credentials. Please try again.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out.')
    return redirect('home')


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    active_tab = request.GET.get('tab', 'overview')
    valid_tabs = {'overview', 'reputation', 'questions', 'answers', 'badges'}
    if active_tab not in valid_tabs:
        active_tab = 'overview'

    questions_qs = (
        profile_user.questions.filter(is_deleted=False)
        .prefetch_related('tags')
        .order_by('-created_at')
    )
    answers_qs = (
        profile_user.answers.filter(is_deleted=False)
        .select_related('question')
        .order_by('-created_at')
    )
    questions = questions_qs if active_tab == 'questions' else questions_qs[:5]
    answers = answers_qs if active_tab == 'answers' else answers_qs[:5]
    user_badges = UserBadge.objects.filter(user=profile_user).select_related('badge')
    rep_history_qs = ReputationHistory.objects.filter(user=profile_user)
    rep_history = rep_history_qs[:100] if active_tab == 'reputation' else rep_history_qs[:10]
    follower_count = profile_user.follower_relationships.count()
    following_count = profile_user.following_relationships.count()

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(
            follower=request.user,
            following=profile_user,
        ).exists()
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'questions': questions,
        'answers': answers,
        'user_badges': user_badges,
        'rep_history': rep_history,
        'follower_count': follower_count,
        'following_count': following_count,
        'is_following': is_following,
        'active_tab': active_tab,
        'question_count': questions_qs.count(),
        'answer_count': answers_qs.count(),
        'badge_count': user_badges.count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def toggle_follow_view(request, username):
    target = get_object_or_404(User, username=username, is_active=True)
    if target == request.user:
        messages.error(request, 'You cannot follow yourself.')
        return redirect('profile', username=username)

    if request.method == 'POST':
        follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if not created:
            follow.delete()
            messages.info(request, f'You unfollowed {target.username}.')
        else:
            messages.success(request, f'You are now following {target.username}.')
    return redirect('profile', username=username)


def followers_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    users = User.objects.filter(
        following_relationships__following=profile_user
    )
    users = users.select_related('profile').order_by('username')
    context = {
        'profile_user': profile_user,
        'users': users,
        'connection_type': 'Followers',
    }
    return render(request, 'accounts/connections.html', context)


def following_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    users = User.objects.filter(
        follower_relationships__follower=profile_user
    )
    users = users.select_related('profile').order_by('username')
    context = {
        'profile_user': profile_user,
        'users': users,
        'connection_type': 'Following',
    }
    return render(request, 'accounts/connections.html', context)


@login_required
def edit_profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save()
            profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile', username=request.user.username)
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        }
        form = ProfileUpdateForm(instance=profile, initial=initial_data)
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['old_password']):
                form.add_error('old_password', 'Current password is incorrect.')
            else:
                request.user.set_password(form.cleaned_data['new_password1'])
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed successfully!')
                return redirect('profile', username=request.user.username)
    else:
        form = ChangePasswordForm()
    return render(request, 'accounts/change_password.html', {'form': form})


def users_list_view(request):
    sort_by = request.GET.get('sort', 'reputation')
    users = User.objects.filter(is_active=True).select_related('profile')
    if sort_by == 'reputation':
        users = users.order_by('-profile__reputation')
    elif sort_by == 'newest':
        users = users.order_by('-date_joined')
    elif sort_by == 'name':
        users = users.order_by('username')

    search = request.GET.get('q', '')
    if search:
        users = users.filter(username__icontains=search)

    paginator = Paginator(users, 24)
    page = paginator.get_page(request.GET.get('page', 1))
    context = {
        'page': page,
        'sort': sort_by,
        'search': search,
    }
    return render(request, 'accounts/users.html', context)


@login_required
def toggle_dark_mode(request):
    profile = request.user.profile
    profile.dark_mode = not profile.dark_mode
    profile.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))
