import pytest
from fastapi import HTTPException
from app.services.category_service import CategoryService
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.models.category import Category
from app.models.event import Event

class TestCategoryServiceExtended:
    
    def test_update_category_nonexistent(self, db_session):
        """Test para actualizar una categoría inexistente"""
        category_service = CategoryService(db=db_session)
        
        update_data = CategoryUpdate(
            name="Updated Nonexistent Category"
        )
        
        result = category_service.update_category(
            category_id=99999,  # ID que no existe
            category_in=update_data
        )
        
        assert result is None
    
    def test_update_category_duplicate_name(self, db_session, test_category):
        """Test para actualizar una categoría con nombre duplicado"""
        category_service = CategoryService(db=db_session)
        
        # Crear otra categoría primero
        another_category = Category(
            name="Another Category",
            description="This is another category for testing",
            color="#FF5733"
        )
        db_session.add(another_category)
        db_session.commit()
        db_session.refresh(another_category)
        
        # Intentar actualizar con nombre ya existente
        update_data = CategoryUpdate(
            name=test_category.name  # Nombre que ya existe
        )
        
        with pytest.raises(HTTPException) as excinfo:
            category_service.update_category(
                category_id=another_category.id,
                category_in=update_data
            )
        
        assert excinfo.value.status_code == 400
        assert "already exists" in str(excinfo.value.detail)
    
    def test_delete_category_with_events(self, db_session, test_category, test_event):
        """Test para eliminar una categoría asociada a eventos"""
        category_service = CategoryService(db=db_session)
        
        # Asociar la categoría al evento
        test_event.categories = [test_category]
        db_session.add(test_event)
        db_session.commit()
        
        # Intentar eliminar la categoría
        with pytest.raises(HTTPException) as excinfo:
            category_service.delete_category(category_id=test_category.id)
        
        assert excinfo.value.status_code == 400
        assert "cannot delete" in str(excinfo.value.detail).lower()