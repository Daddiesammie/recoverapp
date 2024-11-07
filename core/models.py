from django.db import models

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='site/')
    hero_image = models.ImageField(upload_to='site/', blank=True, null=True)
    about = models.TextField()
    privacy_policy = models.TextField()
    disclaimer = models.TextField()
    payment_policy = models.TextField(null=True)
    terms_and_conditions = models.TextField(null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)

    

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

class Testimonial(models.Model):
    image = models.ImageField(upload_to='testimonials/')
    description = models.TextField()
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['-created_at']

    def __str__(self):
        return f"Testimonial by {self.name}"