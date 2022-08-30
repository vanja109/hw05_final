from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
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
            text='test_text1',
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test_slug'}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs=(
                    {'username': f'{self.user}'})): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': f'{self.posts.id}'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_form.html',
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': f'{self.posts.id}'}): 'posts/post_form.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def func_assert_equal(self, post):
        self.assertEqual(post.text, self.posts.text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.posts.group)
        self.assertEqual(post.pub_date, self.posts.pub_date)

    def test_index_context(self):
        """Соответветствие словаря context в index"""
        response = (self.authorized_client.get(reverse('posts:index')))
        post = response.context['page_obj'][0]
        self.func_assert_equal(post)

    def test_group_context(self):
        """Соответветствие словаря context в group_list"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', args=(self.group.slug,)))
        post = response.context['page_obj'][0]
        self.func_assert_equal(post)
        self.assertEqual(post.group.slug, self.group.slug)

    def test_profile_context(self):
        """Соответветствие словаря context в profile"""
        response = self.authorized_client.get(reverse(
            'posts:profile', args=(self.user,)))
        post = response.context['page_obj'][0]
        self.func_assert_equal(post)
        self.assertEqual(post.author, self.user)

    def test_post_detail_context(self):
        """Соответветствие словаря context в post_detail"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', args=(self.posts.id,)))
        post = response.context['posts_list']
        self.func_assert_equal(post)
        self.assertEqual(post.id, self.posts.id)

    def test_form_create_post_context(self):
        """Соответветствие словаря context в post_create"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_form_edit_post_context(self):
        """Соответветствие словаря context в post_edit"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', args=(self.posts.id,)))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
