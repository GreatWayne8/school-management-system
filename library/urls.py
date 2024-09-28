from django.urls import path
from .views import library_view, ebook_list, upload_ebook, manage_library_view,library_categories_view

urlpatterns = [
    path('library/', library_view, name='library'),
    path('library/manage/', manage_library_view, name='manage_library'),
    path('library/categories/', library_categories_view, name='library_categories'),
    path('library/category/<int:category_id>/', ebook_list, name='ebook_list_by_category'),
    path('ebooks/', ebook_list, name='ebook_list'),
    path('upload/', upload_ebook, name='upload_ebook'),
]
