from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class LibraryCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name 
    
class Ebook(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    file = models.FileField(upload_to='ebooks/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
