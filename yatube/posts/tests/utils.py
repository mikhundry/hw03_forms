def paginator_test(self, response):
    first_object = response.context['page_obj'][0]
    post_text_0 = first_object.text
    post_author_0 = first_object.author
    self.assertEqual(post_text_0, 'Тестовый пост')
    self.assertEqual(post_author_0, self.user)
