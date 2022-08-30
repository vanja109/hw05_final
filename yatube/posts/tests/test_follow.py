from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Post

User = get_user_model()

class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follow_user = User.objects.create_user(username='Follower')
        cls.unfollow_user = User.objects.create_user(username='UNFollower')
        cls.following = User.objects.create_user(username='following')
        cls.post = Post.objects.create(
            author=cls.following,
            text='Тестовая пост',
        )

    def setUp(self):
        follow_user = FollowTests.follow_user
        self.follow_user_cl = Client()
        self.follow_user_cl.force_login(follow_user)
        unfollow_user = FollowTests.unfollow_user
        self.unfollow_user_cl = Client()
        self.unfollow_user_cl.force_login(unfollow_user)
        following = FollowTests.following
        self.following_cl = Client()
        self.following_cl.force_login(following)

    def test_follow(self):
        self.follow_user_cl.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.following}
            )
        )
        self.assertEqual(Follow.objects.count(), 1)

    def test_unfollow(self):
        self.follow_user_cl.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': FollowTests.following}
            )
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_follow_page(self):
        self.follow_user_cl.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.following}
            )
        )
        self.assertEqual(Follow.objects.count(), 1)
        form_data = {'text': 'follow_test'}
        self.following_cl.post(
            reverse('posts:post_create'), data = form_data, follow=True
        )
        response = self.follow_user_cl.get(reverse('posts:follow_index'))
        self.assertContains(response, 'follow_test')
        response = self.unfollow_user_cl.get(reverse('posts:follow_index'))
        self.assertNotContains(response, 'follow_test')
