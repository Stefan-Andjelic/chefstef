from django import forms


RECIPE_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 2)]

class CartAddRecipeForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=RECIPE_QUANTITY_CHOICES, coerce=int)
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)