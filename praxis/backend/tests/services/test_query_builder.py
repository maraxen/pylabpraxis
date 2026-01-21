
import pytest
from sqlalchemy import select, JSON
from sqlmodel import SQLModel, Field
from typing import Optional

from praxis.backend.models.domain.filters import SearchFilters
from praxis.backend.services.utils.query_builder import apply_plr_category_filter, apply_search_filters

class MockModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = "test"
    plr_category: str = "none"
    properties_json: dict = Field(default_factory=dict, sa_type=JSON)

def test_apply_plr_category_filter():
    """Test that plr_category filter is correctly applied to the query."""
    filters = SearchFilters(plr_category="plate")
    statement = select(MockModel)
    
    modified_statement = apply_plr_category_filter(statement, filters, MockModel)
    
    stmt_str = str(modified_statement.compile())
    assert "mockmodel.plr_category = :plr_category_1" in stmt_str

def test_apply_plr_category_filter_no_attr():
    """Test that plr_category filter is NOT applied if model lacks the attribute."""
    class NoAttrModel(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str = "test"

    filters = SearchFilters(plr_category="plate")
    statement = select(NoAttrModel)
    
    modified_statement = apply_plr_category_filter(statement, filters, NoAttrModel)
    
    stmt_str = str(modified_statement.compile())
    assert "plr_category" not in stmt_str

def test_apply_search_filters_integrates_plr_category():
    """Test that apply_search_filters calls apply_plr_category_filter."""
    filters = SearchFilters(plr_category="tip_rack")
    statement = select(MockModel)
    
    modified_statement = apply_search_filters(statement, MockModel, filters)
    
    stmt_str = str(modified_statement.compile())
    assert "mockmodel.plr_category = :plr_category_1" in stmt_str

def test_apply_plr_category_filter_from_search_filters():
    """Test that plr_category is picked up from search_filters if not at top level."""
    filters = SearchFilters(search_filters={"plr_category": "plate"})
    statement = select(MockModel)
    
    modified_statement = apply_plr_category_filter(statement, filters, MockModel)
    
    stmt_str = str(modified_statement.compile())
    assert "mockmodel.plr_category = :plr_category_1" in stmt_str
