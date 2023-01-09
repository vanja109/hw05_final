from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

User = get_user_model()


def paginator(request, posts_list):
    paginator = Paginator(posts_list, settings.POSTS_NUM)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(timeout=20, key_prefix='index_page')
def index(request):
    posts_list = Post.objects.select_related('group', 'author')
    context = {
        'page_obj': paginator(request, posts_list),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.select_related('author')
    context = {
        'group': group,
        'page_obj': paginator(request, posts_list),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_list = author.posts.select_related('group')
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    )
    follow_btn = (
        request.user.is_authenticated
        and request.user != author
    )
    context = {
        'author': author,
        'page_obj': paginator(request, posts_list),
        'following': following,
        'follow_btn': follow_btn,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    queryset = Post.objects.select_related('group', 'author')
    posts_list = get_object_or_404(queryset, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = posts_list.comments.all()
    context = {
        'posts_list': posts_list,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/post_form.html', {'form': form})


@login_required
def post_edit(request, post_id):
    queryset = Post.objects.select_related()
    post = get_object_or_404(queryset, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.pk)
    return render(request, 'posts/post_form.html', context)


@login_required
def add_comment(request, post_id):
    queryset = Post.objects.select_related()
    post = get_object_or_404(queryset, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': paginator(request, post_list),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
