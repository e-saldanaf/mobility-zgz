import pandas as pd
import pytest
from src.load import BiziLoader
from sqlalchemy import Engine


def test_upsert_data_empty(mocker):
    # Mock create_engine to avoid actual connection
    mocker.patch("src.load.create_engine")
    loader = BiziLoader("sqlite:///:memory:")
    df = pd.DataFrame()
    loader.upsert_data(df, "test_table")
    # Should return early without calling anything on engine


def test_upsert_data_calls_execute(mocker):
    # CAMBIO AQUÍ: Usamos MagicMock sin el restrictivo spec=Engine
    mock_engine = mocker.MagicMock()
    mock_conn = mock_engine.begin.return_value.__enter__.return_value
    mocker.patch("src.load.create_engine", return_value=mock_engine)

    loader = BiziLoader("postgresql://user:pass@host/db")
    df = pd.DataFrame([{"id": 1, "title": "S1"}])

    # We need to mock df.to_sql because it will try to use the connection
    mocker.patch("pandas.DataFrame.to_sql")

    loader.upsert_data(df, "bizi_stations")

    assert mock_conn.execute.call_count >= 1
    # Check if CREATE TEMP TABLE was called
    args, _ = mock_conn.execute.call_args_list[0]
    assert "CREATE TEMP TABLE" in str(args[0])