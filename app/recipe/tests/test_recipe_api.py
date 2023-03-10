"""
Test for recipe API
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test  import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer, 
    RecipeDetailSerializer
)

RECIPES_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """ Create and return a recipe detail URL. """
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Sample recipe title',
        'time_minutes': 22,
        'price': Decimal(5.25),
        'description': 'Sample description',
        'link': 'http://www.example.com/recipe.pdf',
    }
    defaults.update(params)
    recipe = Recipe.objects.create(user = user, **defaults)
    return recipe

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()
    
    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
    """TEst authenticated API clients."""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email = "user@example.com",
            password = 'testpass123'
        )
        self.client.force_authenticate(self.user)
    
    def test_retrive_recipe(self):
        """test retrieving a list of recipe"""
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializers = RecipeSerializer(recipes, many=True)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializers.data)

    def test_recipe_list_limited_to_user(self):
        """test list of recipe is limited to authenticated user."""
        other_user = create_user(
            email = "other@example.com",
            password = "password123",
        )
        create_recipe(user = other_user)
        create_recipe(user = self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user = self.user)
        serializers = RecipeSerializer(recipes, many = True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializers.data)
    
    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user = self.user)
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe"""
        payload = { 
            'title': 'sample', 
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_partial_udpate(self):
        """Test partial update of recipe"""
        original_link = 'http://www.example.com/recipe.pdf'
        recipe = create_recipe(
            user = self.user,
            title = "sample",
            link = original_link,
        )
        payload = {'title': 'New recipe title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update recipe"""
        recipe = create_recipe(
            user = self.user,
            title = 'Sample recipe title',
            link = 'http://www.example.com/recipe.pdf',
            description = 'Sample Recipe description',
        )

        payload = {
            'title': 'New Recipe title',
            'link': 'http://www.example2.com/recipe.pdf',
            'description': "new recipe description",
            'time_minutes': 10,
            'price': Decimal(2.55),
        }

        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)