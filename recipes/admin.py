from django.contrib import admin
from .models import Recipe, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'available', 'price', 'user','created']
    list_filter = ['created']
    prepopulated_fields = {'slug': ('name',)}