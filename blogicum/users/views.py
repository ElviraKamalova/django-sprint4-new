from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import ProfileEditForm
from blog.models import Post


User = get_user_model()


def profile_view(request, username):
    profile = get_object_or_404(User, username=username)

    if request.user == profile:
        page_obj = Post.objects.filter(author=profile).annotate(
            comment_count=Count('comments')
        ).select_related(
            'category', 'location', 'author'
        ).order_by('-pub_date')
    else:
        page_obj = Post.published.published().filter(
            author=profile
        ).select_related(
            'category', 'location', 'author'
        ).order_by('-pub_date')
    paginator = Paginator(page_obj, settings.POSTS_PER_PAGE_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'profile': profile, 'page_obj': page_obj}
    return render(request, 'blog/profile.html', context)


class ProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = ProfileEditForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )
