from decimal import Decimal
from django.conf import settings
from recipes.models import Recipe


class Cart(object):
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, recipe, quantity=1, override_quantity=False):
        """
        Add a recipe to the cart or update its quantity.
        """
        recipe_id = str(recipe.id)
        if recipe_id not in self.cart:
            self.cart[recipe_id] = {'quantity': 0,
                                     'price': str(recipe.price)}
        if override_quantity:
            self.cart[recipe_id]['quantity'] = quantity
        else:
            self.cart[recipe_id]['quantity'] += quantity
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, recipe):
        """
        Remove a recipe from the cart.
        """
        recipe_id = str(recipe.id)
        if recipe_id in self.cart:
            del self.cart[recipe_id]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the recipes
        from the database.
        """
        recipe_ids = self.cart.keys()
        # get the recipe objects and add them to the cart
        recipes = Recipe.objects.filter(id__in=recipe_ids)
        cart = self.cart.copy()
        for recipe in recipes:
            cart[str(recipe.id)]['recipe'] = recipe
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()