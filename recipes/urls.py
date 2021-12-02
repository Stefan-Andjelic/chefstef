from django.urls import path
from . import views


app_name = 'recipes'

urlpatterns = [
    path('ranking/r/', views.recipe_ranking, name='ranking'),
    path('like/', views.recipe_like, name='like'),
    path('detail/<int:id>/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
    path('<slug:category_slug>/', views.recipe_list, name='recipe_list_by_category'),
    path('', views.recipe_list, name='recipe_list'),
    path('<int:recipe_id>/share/', views.recipe_share, name='recipe_share'),
    path('', views.recipe_list, name='list'),
    
]
