from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from core.models import PublishedModel
from .querysets import CategoryQuerySet, PostQuerySet


User = get_user_model()


class Category(PublishedModel):
    title = models.CharField(
        max_length=settings.MAX_CATEGORY_TITLE_LENGTH,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис '
            'и подчёркивание.'
        )
    )
    published = CategoryQuerySet.as_manager()

    class Meta(PublishedModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(
        max_length=settings.MAX_LOCATION_TITLE_LENGTH,
        verbose_name='Название места'
    )

    class Meta(PublishedModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    title = models.CharField(
        max_length=settings.MAX_POST_TITLE_LENGTH,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='category_posts',
        verbose_name='Категория'
    )
    published = PostQuerySet.as_manager()
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='posts_images/',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-pub_date']

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментарии',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments_author',
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    created_at = models.DateTimeField(
        'Дата и время создания',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']

        def __str__(self):
            return (
                f'Комментарий от {self.author.username}'
                'к посту {self.post.title}'
            )
