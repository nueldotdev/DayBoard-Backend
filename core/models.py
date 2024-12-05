from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser
from django.conf import settings # For AUTH_USER_MODEL

# User model
class User(AbstractUser):
    first_name = models.CharField(max_length=25, blank=False, null=False)
    last_name = models.CharField(max_length=25, blank=True, null=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='profile_imgs/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    # Might use later

    # is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField(default=False)
    # is_superuser = models.BooleanField(default=False)
    
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Username is still required unless you customize it further.

    def __str__(self):
        return self.email


# Board models
class Board(models.Model):
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    name = models.CharField(max_length=25, blank=False, null=False)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    favorite = models.BooleanField(default=False)
    color = models.CharField(max_length=25, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Board.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class List(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    title = models.CharField(max_length=20, null=False, blank=False)
    # total_cards = models.IntegerField(max=10, )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Card(models.Model):
    title = models.CharField(max_length=30, blank=False, null=False)
    list = models.ForeignKey(List, on_delete=models.CASCADE)
    description = models.TextField(max_length=200, blank=True, null=True)
    image_url = models.CharField(blank=True, null=True, max_length=1000000)
    uploaded_img = models.ImageField(upload_to='card_images/', null=True, blank=True)
    due_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title