from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Ebook, Category
from .forms import EbookForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import LibraryCategory

@login_required
def library_view(request):
    # Fetch all e-books
    ebooks = Ebook.objects.all()

    context = {
        'ebooks': ebooks,
        'request': request,  
    }

    return render(request, 'library/library.html', context)


@user_passes_test(lambda u: u.is_superuser)
def manage_library_view(request):
    if request.method == 'POST':
        form = EbookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_library') 
    else:
        form = EbookForm() 

    ebooks = Ebook.objects.all()
    
    return render(request, 'library/manage_library.html', {
        'form': form,
        'ebooks': ebooks,
    })

def ebook_list(request, category_id=None):
    """
    Displays a list of e-books. Optionally, filters by category if category_id is provided.
    """
    if category_id:
        ebooks = Ebook.objects.filter(category_id=category_id)
    else:
        ebooks = Ebook.objects.all()
    
    categories = Category.objects.all() 
    return render(request, 'library/ebook_list.html', {'ebooks': ebooks, 'categories': categories})
def download_ebook(request, ebook_id):
    ebook = get_object_or_404(Ebook, id=ebook_id)

    # Serve the file as a download
    response = HttpResponse(ebook.file, content_type='application/pdf') 
    response['Content-Disposition'] = f'attachment; filename="{ebook.title}.pdf"'  
    return response


@user_passes_test(lambda u: u.is_superuser)
def edit_ebook(request, ebook_id):
    ebook = get_object_or_404(Ebook, id=ebook_id)
    if request.method == 'POST':
        form = EbookForm(request.POST, request.FILES, instance=ebook)
        if form.is_valid():
            form.save()
            return redirect('library') 
    else:
        form = EbookForm(instance=ebook)
    return render(request, 'library/edit_ebook.html', {'form': form, 'ebook': ebook})


@user_passes_test(lambda u: u.is_superuser)
def delete_ebook(request, ebook_id):
    ebook = get_object_or_404(Ebook, id=ebook_id)
    ebook.delete()
    return redirect('library')    

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
    
    return render(request, 'library/upload_ebook.html', {'form': form})


def library_categories_view(request):
    categories = LibraryCategory.objects.all()
    return render(request, 'library/categories.html', {'categories': categories})