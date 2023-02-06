from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.author = User.objects.create_user(username='Author')
        cls.post_author_client = Client()
        cls.post_author_client.force_login(cls.author)
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности страниц для всех пользователей."""
        templates_url_names = [
            '/',
            '/group/test-slug/',
            '/profile/HasNoName/',
            '/posts/1/',
        ]
        for address in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_post_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_post_edit_url_exists_at_desired_location_author(self):
        """Страница редактирования поста доступна автору."""
        response = self.post_author_client.get('/posts/1/edit')
        self.assertEqual(response.status_code, 200)

    def test_unexisting_page_url_return_404(self):
        """Запрос к несуществующей странице возвращает ошибку 404."""
        response = self.guest_client.get('unexisting_page')
        self.assertEqual(response.status_code, 404)

    def test_post_create_url_redirect_anonymous_on_auth_login(self):
        """Страница по адресу /create/ перенаправит анонимного
        пользователя на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, ('/auth/login/?next=/create/')) 

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.post_author_client.get(address)
                self.assertTemplateUsed(response, template)
