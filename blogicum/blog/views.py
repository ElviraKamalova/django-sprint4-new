from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django.urls import reverse, reverse_lazy

from .models import Category, Post, Comment
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.published.for_index_page().select_related(
        'author', 'category', 'location'
    ).order_by('-pub_date')
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, 'blog/index.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.published.published(),
        slug=category_slug,
    )
    post_list = category.category_posts.published().select_related(
        'author', 'location'
    ).order_by('-pub_date')
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        queryset = Post.objects.select_related(
            'author',
            'category',
            'location'
        ).annotate(
            comment_count=Count('comments')
        )
        post = super().get_object(queryset=queryset)
        is_published = Post.published.published().filter(pk=post.pk).exists()
        is_author = self.request.user == post.author

        if not is_published and not is_author:
            raise Http404('Страница не найдена.')
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return redirect('blog:post_detail', pk=post.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            raise Http404('Вы не можете удалить чужую публикацию!')
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.get_object())
        return context

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_invalid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        context = {
            'post': post,
            'form': form,
            'comments': post.comments.select_related(
                'author'
            ).order_by('created_at'),
        }
        return render(self.request, 'blog/detail.html', context)

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.post = post
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


class CommentEditView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        post_obj = get_object_or_404(Post, pk=self.kwargs['post_id'])
        comment = super().get_object(queryset)
        if comment.post != post_obj:
            raise Http404(
                'Этот комментарий'
                'не принадлежит данной публикации.'
            )
        if comment.author != self.request.user:
            raise Http404(
                'Вы не можете изменять'
                'чужие комментарии!'
            )
        return comment

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        post_obj = get_object_or_404(Post, pk=self.kwargs['post_id'])
        comment = super().get_object(queryset)
        if comment.post != post_obj:
            raise Http404('Этот комментарий не принадлежит данной публикации.')
        if comment.author != self.request.user:
            raise Http404('Вы не можете удалить чужую публикацию!')
        return comment

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
        )
