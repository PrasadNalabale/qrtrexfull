# menu/documents.py
from django_elasticsearch_dsl import Document, Index
from django_elasticsearch_dsl.registries import registry
from .models import MenuItem

menu_item_index = Index('menu_items')

@registry.register_document
class MenuItemDocument(Document):
    class Index:
        name = 'menu_items'

    class Django:
        model = MenuItem
        fields = [
            'name',
            'description',
            'price',
            'category',
            'is_available',
        ]
