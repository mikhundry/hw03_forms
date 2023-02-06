from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

from .utils import paginator_test

User = get_user_model()


class PostViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse(
                'posts:group_list', kwargs={'slug': 'test-slug'}
                )): 'posts/group_list.html',
            (reverse(
                'posts:profile', kwargs={'username': 'HasNoName'}
                )): 'posts/profile.html',
            (reverse(
                'posts:post_detail', kwargs={'post_id': '1'}
                )): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            (reverse(
                'posts:post_edit', kwargs={'post_id': '1'}
                )): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        paginator_test(self, response)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
                ))
        self.assertEqual(response.context['group'].title, 'Тестовая группа')
        self.assertEqual(response.context['group'].slug, 'test-slug')
        self.assertEqual(
            response.context['group'].description, 'Тестовое описание'
            )
        paginator_test(self, response)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
                'posts:profile', kwargs={'username': self.user}
                ))
        paginator_test(self, response)
        self.assertEqual(response.context['user'].username, 'HasNoName')
        self.assertEqual(response.context['post'][0].author, self.post.author)
        self.assertEqual(
            list(response.context['post']),
            list(self.user.posts.all())
            )

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
                ))
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['post'].pk, self.post.pk)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}
            ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['post_id'], self.post.pk)

    def test_post_added_correctly(self):
        """Пост при создании добавлен корректно"""
        index = self.authorized_client.get(
            reverse('posts:index')
            ).context['page_obj']
        group_list = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'})
            ).context['page_obj']
        profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': f'{self.user.username}'
                })
            ).context['page_obj']
        self.assertIn(self.post, index)
        self.assertIn(self.post, group_list)
        self.assertIn(self.post, profile)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Author')
        cls.group = Group.objects.create(
            title='test_group',
            description='test_decription',
            slug='test_slug',
        )
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                author=cls.author,
                text=f'test_post {i}',
                group=cls.group,
            ))
        Post.objects.bulk_create(cls.posts)
    
    def setUp(self) -> None:
        self.user = User.objects.create(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
