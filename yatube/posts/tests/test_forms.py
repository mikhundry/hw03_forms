from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post
from django.contrib.auth import get_user_model

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.form = PostForm()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group,
            }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=self.group,
                author=self.user,
            ).exists()
        )

    def test_edit_post(self):
        """Проверка редактирования"""
        old_text = self.post
        self.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-group',
            description='Тестовое описание2',
        )
        form_data = {
            'text': 'Текст записанный в форму',
            'group': self.group2,
            }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': old_text}),
            data=form_data,
            follow=True,
            )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error_name1 = 'Данные поста не совпадают'
        self.assertTrue(Post.objects.filter(
                        group=self.group2.id,
                        author=self.user,
                        pub_date=self.post.pub_date
                        ).exists(), error_name1)
        error_name1 = 'Пользователь не может изменить содержание поста'
        self.assertNotEqual(old_text.text, form_data['text'], error_name1)
        error_name2 = 'Пользователь не может изменить группу поста'
        self.assertNotEqual(old_text.group, form_data['group'], error_name2)