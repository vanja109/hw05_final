from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_descrip',
        )
        cls.posts = Post.objects.create(
            author=cls.user,
            text='test_text',
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка создания поста"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Test',
            'title': 'Test',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': f'{self.user}'}))
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        """Проверка изменения поста"""
        form_data = {
            'text': 'Test',
            'title': 'Test',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.posts.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.posts.id}'}
            )
        )
        self.assertTrue(
            Post.objects.filter(
                text='Test'
            ).exists()
        )
