from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Ebook, Category
from .forms import EbookForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import LibraryCategory

@login_required
def library_view(request):
    # Fetch all e-books
    ebooks = Ebook.objects.all()

    # Superuser or teacher can add books
    if request.user.is_superuser or request.user.is_teacher:
        if request.method == 'POST':
            # Code to add a new e-book
            pass

    context = {
        'ebooks': ebooks,
    }

    return render(request, 'library/library.html', context)

@user_passes_test(lambda u: u.is_superuser)
def manage_library_view(request):
    # Admin management for e-books (add, edit, delete)
    # Logic for managing e-books
    pass

def ebook_list(request, category_id=None):
    """
    Displays a list of e-books. Optionally, filters by category if category_id is provided.
    """
    if category_id:
        ebooks = Ebook.objects.filter(category_id=category_id)
    else:
        ebooks = Ebook.objects.all()
    
    categories = Category.objects.all()
    return render(request, 'ebook_list.html', {'ebooks': ebooks, 'categories': categories})

def upload_ebook(request):
    """
    Handles the uploading of e-books.
    """
    if request.method == 'POST':
        form = EbookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('ebook_list')
    else:
        form = EbookForm()
    
    return render(request, 'upload_ebook.html', {'form': form})

def library_categories_view(request):
    categories = LibraryCategory.objects.all()
    return render(request, 'library/categories.html', {'categories': categories})