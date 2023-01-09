from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POST_COUNT = 13
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_descrip',
        )
        cls.posts = Post.objects.bulk_create([Post(
            pk=pk,
            author=cls.user,
            text='test_text',
            group=cls.group) for pk in range(cls.POST_COUNT)
        ])
        cls.first_post = cls.posts[0]

    def test_paginator_index_first(self):
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                         settings.POSTS_NUM)

    def test_paginator_index_second(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
