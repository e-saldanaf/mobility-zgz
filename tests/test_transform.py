import pandas as pd
import pytest
from src.transform import BiziTransformer

def test_clean_data_success():
    raw_data = [
        {
            "id": "1",
            "title": "Station 1",
            "bicisDisponibles": "10",
            "anclajesDisponibles": "5",
            "lastUpdated": "2024-05-16T12:00:00Z",
            "geometry": {"coordinates": [-0.88, 41.65]}
        },
        {
            "id": "2",
            "title": "Station 2",
            "bicisDisponibles": "0",
            "anclajesDisponibles": "15",
            "lastUpdated": "2024-05-16T12:05:00Z",
            "geometry": {"coordinates": [-0.89, 41.66]}
        }
    ]
    
    df = BiziTransformer.clean_data(raw_data)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ['id', 'title', 'bikes', 'slots', 'api_updated_at', 'lon', 'lat', 'created_at', 'modified_at']
    assert df.iloc[0]['id'] == 1
    assert df.iloc[0]['bikes'] == 10
    assert df.iloc[1]['slots'] == 15
    assert df.iloc[0]['lon'] == -0.88
    assert df.iloc[0]['lat'] == 41.65

def test_clean_data_empty():
    df = BiziTransformer.clean_data([])
    assert df.empty

def test_clean_data_missing_fields():
    raw_data = [
        {
            "id": "3",
            "title": "Station 3"
            # Missing other fields
        }
    ]
    df = BiziTransformer.clean_data(raw_data)
    assert len(df) == 1
    assert df.iloc[0]['bikes'] == 0
    assert df.iloc[0]['slots'] == 0
    assert df.iloc[0]['lon'] == 0
    assert df.iloc[0]['lat'] == 0
