from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import paginator


def index(request):
    post_list = Post.objects.all()
    page_obj = paginator(post_list, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator(post_list, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = paginator(post_list, request)
    context = {
        'page_obj': page_obj,
        'username': username,
        'author': author,
        'post': post_list
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
        'post_id': post_id
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            temp_form = form.save(commit=False)
            temp_form.author = request.user
            temp_form.save()
            return redirect('posts:profile', temp_form.author)

        return render(request, 'posts/create_post.html', {'form': form})

    form = PostForm()
    context = {
        'form': form,
    }
    return render(request, 'posts/create_post.html', context)


def post_edit(request, post_id):
    edit_post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    template = 'posts/create_post.html'

    if request.user != edit_post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(request.POST or None, instance=edit_post)

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'form': form,
        'is_edit': is_edit,
        'post_id': post_id
    }
    return render(request, template, context)
