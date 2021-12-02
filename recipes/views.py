from django.core import paginator
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from .models import Recipe, Category
from cart.forms import CartAddRecipeForm
from .forms import EmailPostForm
import redis


# Connect to redis
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


def recipe_detail(request, id, slug):
    recipe = get_object_or_404(Recipe, id=id, slug=slug, available=True)
    cart_recipe_form = CartAddRecipeForm()
    # increment total recipe views by 1
    total_views = r.incr(f'recipe:{recipe.id}:views')
    # increment recipe ranking by 1
    r.zincrby('recipe_ranking', 1, recipe.id)
    return render(request, 'recipes/recipe/detail.html', 
                            {'section': 'recipes', 'recipe': recipe, 
                            'cart_recipe_form': cart_recipe_form,
                            'total_views': total_views})


@login_required
def recipe_ranking(request):
    # get recipe ranking dictionary
    recipe_ranking = r.zrange('recipe_ranking', 0, -1,
                             desc=True)[:5]
    recipe_ranking_ids = [int(id) for id in recipe_ranking]
    # get most viewed recipes
    most_viewed = list(Recipe.objects.filter(
                           id__in=recipe_ranking_ids))
    most_viewed.sort(key=lambda x: recipe_ranking_ids.index(x.id))
    return render(request,
                  'recipes/recipe/ranking.html',
                  {'section': 'most_popular',
                   'most_viewed': most_viewed})


@login_required
def recipe_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    recipes = Recipe.objects.all()
    paginator = Paginator(recipes, 8)
    page = request.GET.get('page')
    try:
        recipes = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        recipes = paginator.page(1)
    except EmptyPage:
        if request.is_ajax():
            # If the request is AJAX and the page is out of range
            # return an empty page
            return HttpResponse('')
        # If page is out of range deliver last page of results
        recipes = paginator.page(paginator.num_pages)

    if request.is_ajax():
        return render(request, 'recipes/recipe/list_ajax.html', {'section': 'images', 'recipes': recipes})

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        recipes = recipes.filter(category=category)
    return render(request,
                  'recipes/recipe/list.html',
                  {'category': category,
                   'categories': categories,
                   'recipes': recipes,
                   'section': 'recipe'})


def recipe_share(request, recipe_id):
    # Retrieve recipe by id
    recipe = get_object_or_404(Recipe, id=recipe_id, available=True)
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            recipe_url = request.build_absolute_uri(recipe.get_absolute_url())
            subject = f"{cd['name']} recommends you check out this fantastic recipe for {recipe.name}"
            message = f"Take a look at {recipe.name} at {recipe_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'stefanandjelic8@gmail.com', [cd['to']])
            sent = True
    else:   
        form = EmailPostForm()
    
    return render(request, 'recipes/recipe/share.html', {'recipe': recipe, 'form': form, 'sent': sent})


@login_required
@require_POST
def recipe_like(request):
    recipe_id = request.POST.get('id')
    action = request.POST.get('action')
    if recipe_id and action:
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            if action == 'like':
                recipe.users_like.add(request.user)
            else:
                recipe.users_like.remove(request.user)
            return JsonResponse({'status':'ok'})
        except:
            pass
    return JsonResponse({'status':'error'})