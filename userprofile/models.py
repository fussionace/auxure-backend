from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='img/profile_pictures', blank=True)
    shipping_address = models.TextField(blank=True)
    billing_address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    # wishlist = models.ManyToManyField('products.Product', blank=True, related_name='wishlists')
    # Add any additional fields you need for the user profile

    def __str__(self):
        return self.user.username
