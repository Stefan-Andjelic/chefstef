from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from recipes.models import Recipe
from .cart import Cart
from .forms import CartAddRecipeForm


@require_POST
def cart_add(request, recipe_id):
    cart = Cart(request)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    form = CartAddRecipeForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(recipe=recipe, quantity=cd['quantity'], override_quantity=cd['override'])
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, recipe_id):
    cart = Cart(request)
    recipe = get_object_or_404(Recipe, id=recipe_id)
    cart.remove(recipe)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddRecipeForm(initial={
                            'quantity': item['quantity'],
                            'override': True})
    return render(request, 'cart/detail.html', {'cart': cart})