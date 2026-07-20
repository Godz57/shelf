from django.contrib import admin
from django.test import TestCase

from catalog.models import Author, Book, Category, ReadingListItem


class AdminRegistrationTests(TestCase):
    def test_models_registered(self):
        for model in (Author, Category, Book, ReadingListItem):
            self.assertTrue(admin.site.is_registered(model))
