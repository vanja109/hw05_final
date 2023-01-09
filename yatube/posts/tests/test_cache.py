from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()

    def test_index_cache(self):
        Post.objects.create(
            author=User.objects.create_user(username='Author'),
            text='Тестовый пост',
        )
        post_count = Post.objects.count()
        response = self.guest_client.get('/')
        cached_response_content = response.content
        Post.objects.get().delete()
        self.assertEqual(Post.objects.count(), post_count - 1)
        response = self.guest_client.get('/')
        cache.clear()
        response = self.guest_client.get('/')
        self.assertNotEqual(cached_response_content, response.content)
