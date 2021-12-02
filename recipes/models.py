from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    MEAL_CHOICES = (
    ('Breakfast', 'Breakfast'),
    ('Lunch', 'Lunch'),
    ('Dinner', 'Dinner'),
    ('Dessert', 'Dessert'),
    ('Snack', 'Snack'),
)
    name = models.CharField(max_length=10, choices=MEAL_CHOICES)
    slug = models.SlugField(max_length=100, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'meal'
        verbose_name_plural = 'meals'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipes:recipe_list_by_category', args=[self.slug])


class Recipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='recipes_created', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='recipes', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    available = models.BooleanField(default=True)
    # url = models.URLField()
    image = models.ImageField(upload_to='recipes/%Y/%m/%d/', blank=False)
    ingredients = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='recipes_liked', blank=True)

    class Meta:
        ordering = ('name',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('recipes:recipe_detail', args=[self.id, self.slug])



