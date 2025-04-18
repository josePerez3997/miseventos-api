import pytest
from fastapi import HTTPException
from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate, CategoryUpdate

class TestCategoryService:
    
    def test_get_all_categories(self, db_session, test_category):
        """Test para obtener todas las categorías"""
        category_service = CategoryService(db=db_session)
        
        categories = category_service.get_all_categories()
        
        assert categories is not None
        assert len(categories) > 0
        assert any(cat.id == test_category.id for cat in categories)
    
    def test_search_categories(self, db_session, test_category):
        """Test para buscar categorías por nombre"""
        category_service = CategoryService(db=db_session)
        
        # Buscar usando parte del nombre
        search_term = test_category.name[:5]
        categories = category_service.search_categories(name=search_term)
        
        assert categories is not None
        assert len(categories) > 0
        assert categories[0].id == test_category.id
        
        # Buscar algo que no existe
        categories = category_service.search_categories(name="NonexistentCategory")
        assert len(categories) == 0
    
    def test_create_category_duplicate(self, db_session, test_category):
        """Test para crear categoría con nombre duplicado"""
        category_service = CategoryService(db=db_session)
        
        category_data = CategoryCreate(
            name=test_category.name,  # Mismo nombre que test_category
            description="This is a duplicate category",
            color="#FF5733"
        )
        
        with pytest.raises(HTTPException) as excinfo:
            category_service.create_category(category_in=category_data)
        
        assert excinfo.value.status_code == 400
        assert "already exists" in str(excinfo.value.detail).lower()
    
    def test_get_category_stats(self, db_session, test_category, test_event):
        """Test para obtener estadísticas de categorías"""
        category_service = CategoryService(db=db_session)
        
        # Asociar el evento a la categoría de prueba
        test_event.categories = [test_category]
        db_session.add(test_event)
        db_session.commit()
        
        stats = category_service.get_category_stats()
        
        assert stats is not None
        assert len(stats) > 0
        
        # Buscar la categoría de prueba en las estadísticas
        test_cat_stats = next((s for s in stats if s["id"] == test_category.id), None)
        assert test_cat_stats is not None
        assert test_cat_stats["event_count"] > 0