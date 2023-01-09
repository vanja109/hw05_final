from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import CommentForm

from ..models import Comment, Group, Post

User = get_user_model()


class CommentTests(TestCase):
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
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_for_authorized_client(self):
        """Доступность комментариев для авторизованного пользователя"""
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/comment/')
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_comment_for_guest_client(self):
        """Недоступность комментариев для неавторизованного пользователя"""
        response = self.guest_client.get(f'/posts/{self.post.id}/comment/')
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/')

    def test_create_comment(self):
        """Проверка создания комментария"""
        com_count = Comment.objects.count()
        form_data = {
            'text': 'Test',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
        ))
        self.assertEqual(Comment.objects.count(), com_count + 1)
