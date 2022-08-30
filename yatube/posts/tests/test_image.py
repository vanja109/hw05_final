import shutil
import tempfile


from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostImageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_slug',
            description='test_descrip',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.posts = Post.objects.create(
            author=cls.user,
            text='test_text1',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def func_assert_equal(self, post):
        self.assertEqual(post.text, self.posts.text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.posts.group)
        self.assertEqual(post.pub_date, self.posts.pub_date)
        self.assertEqual(post.image, self.posts.image)

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

    def test_add_image(self):
        """Проверка создания поста"""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test',
            'title': 'Test',
            'image': uploaded,
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
