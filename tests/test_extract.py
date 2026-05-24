import pytest
from src.extract import BiziExtractor

def test_fetch_data_success(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "result": [
            {"id": "1", "title": "Station 1"},
            {"id": "2", "title": "Station 2"}
        ]
    }
    mocker.patch("requests.get", return_value=mock_response)
    
    extractor = BiziExtractor("http://fake-api.com")
    data = extractor.fetch_data()
    
    assert len(data) == 2
    assert data[0]["title"] == "Station 1"

def test_fetch_data_list_response(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": "1", "title": "Station 1"},
        {"id": "2", "title": "Station 2"}
    ]
    mocker.patch("requests.get", return_value=mock_response)
    
    extractor = BiziExtractor("http://fake-api.com")
    data = extractor.fetch_data()
    
    assert len(data) == 2

def test_fetch_data_empty_fallback(mocker):
    # First call returns empty string, second call (fallback) returns data
    mock_response_empty = mocker.Mock()
    mock_response_empty.status_code = 200
    mock_response_empty.text = ""
    
    mock_response_data = mocker.Mock()
    mock_response_data.status_code = 200
    mock_response_data.json.return_value = {"result": [{"id": "1"}]}
    
    mocker.patch("requests.get", side_effect=[mock_response_empty, mock_response_data])
    
    extractor = BiziExtractor("https://fake-api.com")
    data = extractor.fetch_data()
    
    assert len(data) == 1
    assert data[0]["id"] == "1"

def test_fetch_data_failure(mocker):
    mocker.patch("requests.get", side_effect=Exception("API Down"))
    
    extractor = BiziExtractor("http://fake-api.com")
    with pytest.raises(Exception):
        extractor.fetch_data()
