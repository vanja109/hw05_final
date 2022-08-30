from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_for_authorized_client(self):
        """Доступность url адресов для авторизованного пользователя"""
        auth_urls = [
            '/',
            '/group/test_slug/',
            '/profile/Author/',
            f'/posts/{self.post.id}/',
            '/create/',
            f'/posts/{self.post.id}/edit/'
        ]
        for url in auth_urls:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_for_guest_client(self):
        """Доступность url адресов для неавторизованного пользователя"""
        guest_urls = [
            '/',
            '/group/test_slug/',
            '/profile/Author/',
            f'/posts/{self.post.id}/',
        ]
        for url in guest_urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_for_unexisting_page(self):
        response = self.authorized_client.get('/task/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
