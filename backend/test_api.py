import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from httpx import AsyncClient
import json

from main import app
from temporal_client import TemporalClient
from llm_service import LLMService

# Test client
client = TestClient(app)

class TestMainEndpoints:
    """Test cases for main API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint serves HTML"""
        with patch("builtins.open", mock_open_html()):
            response = client.get("/")
            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]
    
    def test_root_endpoint_file_not_found(self):
        """Test root endpoint when frontend file is missing"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            response = client.get("/")
            assert response.status_code == 200
            assert "Frontend not found" in response.text

class TestReverseEndpoint:
    """Test cases for the reverse string endpoint"""
    
    @patch.object(TemporalClient, 'execute_reverse_workflow')
    def test_reverse_success(self, mock_execute):
        """Test successful string reversal"""
        # Mock successful workflow execution
        mock_execute.return_value = asyncio.create_future()
        mock_execute.return_value.set_result({
            "workflow_id": "test-workflow-123",
            "reversed_text": "olleh",
            "original_text": "hello",
            "processing_time_ms": 150,
            "success": True,
            "error": None
        })
        
        response = client.post(
            "/api/reverse",
            json={"text": "hello"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"] == "olleh"
        assert data["workflow_id"] == "test-workflow-123"
        assert data["error"] is None
    
    def test_reverse_empty_text(self):
        """Test reverse endpoint with empty text"""
        response = client.post(
            "/api/reverse",
            json={"text": ""}
        )
        
        assert response.status_code == 400
        assert "Text cannot be empty" in response.json()["detail"]
    
    def test_reverse_whitespace_only(self):
        """Test reverse endpoint with whitespace-only text"""
        response = client.post(
            "/api/reverse",
            json={"text": "   "}
        )
        
        assert response.status_code == 400
        assert "Text cannot be empty" in response.json()["detail"]
    
    @patch.object(TemporalClient, 'execute_reverse_workflow')
    def test_reverse_workflow_error(self, mock_execute):
        """Test reverse endpoint when workflow fails"""
        # Mock workflow failure
        mock_execute.return_value = asyncio.create_future()
        mock_execute.return_value.set_exception(Exception("Temporal connection failed"))
        
        response = client.post(
            "/api/reverse",
            json={"text": "hello"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["result"] == ""
        assert "Temporal connection failed" in data["error"]
    
    def test_reverse_invalid_json(self):
        """Test reverse endpoint with invalid JSON"""
        response = client.post(
            "/api/reverse",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_reverse_missing_text_field(self):
        """Test reverse endpoint with missing text field"""
        response = client.post(
            "/api/reverse",
            json={"not_text": "hello"}
        )
        
        assert response.status_code == 422

class TestLLMEndpoint:
    """Test cases for the LLM processing endpoint"""
    
    @patch.object(LLMService, 'process_text')
    def test_llm_summarize_success(self, mock_process):
        """Test successful LLM summarization"""
        mock_process.return_value = asyncio.create_future()
        mock_process.return_value.set_result("This is a summary of the text.")
        
        response = client.post(
            "/api/llm",
            json={"text": "This is a long text that needs to be summarized.", "operation": "summarize"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"] == "This is a summary of the text."
        assert data["error"] is None
    
    @patch.object(LLMService, 'process_text')
    def test_llm_rephrase_success(self, mock_process):
        """Test successful LLM rephrasing"""
        mock_process.return_value = asyncio.create_future()
        mock_process.return_value.set_result("Here is the rephrased text.")
        
        response = client.post(
            "/api/llm",
            json={"text": "Original text to rephrase", "operation": "rephrase"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["result"] == "Here is the rephrased text."
    
    @patch.object(LLMService, 'process_text')
    def test_llm_analyze_success(self, mock_process):
        """Test successful LLM analysis"""
        mock_process.return_value = asyncio.create_future()
        mock_process.return_value.set_result("Analysis: Positive sentiment with themes of success.")
        
        response = client.post(
            "/api/llm",
            json={"text": "I am very happy with the results!", "operation": "analyze"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Analysis:" in data["result"]
    
    def test_llm_default_operation(self):
        """Test LLM endpoint with default operation (summarize)"""
        with patch.object(LLMService, 'process_text') as mock_process:
            mock_process.return_value = asyncio.create_future()
            mock_process.return_value.set_result("Default summary.")
            
            response = client.post(
                "/api/llm",
                json={"text": "Text without operation specified"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            mock_process.assert_called_once_with("Text without operation specified", "summarize")
    
    def test_llm_empty_text(self):
        """Test LLM endpoint with empty text"""
        response = client.post(
            "/api/llm",
            json={"text": "", "operation": "summarize"}
        )
        
        assert response.status_code == 400
        assert "Text cannot be empty" in response.json()["detail"]
    
    @patch.object(LLMService, 'process_text')
    def test_llm_service_error(self, mock_process):
        """Test LLM endpoint when service fails"""
        mock_process.return_value = asyncio.create_future()
        mock_process.return_value.set_exception(ValueError("OpenAI API error"))
        
        response = client.post(
            "/api/llm",
            json={"text": "test text", "operation": "summarize"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["result"] == ""
        assert "OpenAI API error" in data["error"]

class TestHealthEndpoint:
    """Test cases for the health check endpoint"""
    
    @patch.object(TemporalClient, 'health_check')
    @patch.object(LLMService, 'health_check')
    def test_health_all_services_healthy(self, mock_llm_health, mock_temporal_health):
        """Test health endpoint when all services are healthy"""
        mock_temporal_health.return_value = asyncio.create_future()
        mock_temporal_health.return_value.set_result(True)
        mock_llm_health.return_value = asyncio.create_future()
        mock_llm_health.return_value.set_result(True)
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["services"]["temporal"] == "healthy"
        assert data["services"]["llm"] == "healthy"
    
    @patch.object(TemporalClient, 'health_check')
    @patch.object(LLMService, 'health_check')
    def test_health_temporal_unhealthy(self, mock_llm_health, mock_temporal_health):
        """Test health endpoint when Temporal is unhealthy"""
        mock_temporal_health.return_value = asyncio.create_future()
        mock_temporal_health.return_value.set_result(False)
        mock_llm_health.return_value = asyncio.create_future()
        mock_llm_health.return_value.set_result(True)
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["services"]["temporal"] == "unhealthy"
        assert data["services"]["llm"] == "healthy"
    
    @patch.object(TemporalClient, 'health_check')
    @patch.object(LLMService, 'health_check')
    def test_health_llm_unhealthy(self, mock_llm_health, mock_temporal_health):
        """Test health endpoint when LLM service is unhealthy"""
        mock_temporal_health.return_value = asyncio.create_future()
        mock_temporal_health.return_value.set_result(True)
        mock_llm_health.return_value = asyncio.create_future()
        mock_llm_health.return_value.set_result(False)
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["services"]["temporal"] == "healthy"
        assert data["services"]["llm"] == "unhealthy"
    
    @patch.object(TemporalClient, 'health_check')
    @patch.object(LLMService, 'health_check')
    def test_health_all_services_unhealthy(self, mock_llm_health, mock_temporal_health):
        """Test health endpoint when all services are unhealthy"""
        mock_temporal_health.return_value = asyncio.create_future()
        mock_temporal_health.return_value.set_result(False)
        mock_llm_health.return_value = asyncio.create_future()
        mock_llm_health.return_value.set_result(False)
        
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["services"]["temporal"] == "unhealthy"
        assert data["services"]["llm"] == "unhealthy"

class TestErrorHandling:
    """Test cases for error handling and edge cases"""
    
    def test_method_not_allowed(self):
        """Test unsupported HTTP methods"""
        response = client.delete("/api/reverse")
        assert response.status_code == 405
    
    def test_not_found(self):
        """Test non-existent endpoints"""
        response = client.get("/api/nonexistent")
        assert response.status_code == 404
    
    def test_large_payload(self):
        """Test handling of large request payloads"""
        large_text = "a" * 50000  # 50KB text
        response = client.post(
            "/api/reverse",
            json={"text": large_text}
        )
        # Should either process or reject gracefully
        assert response.status_code in [200, 400, 413, 422]

class TestCORSHandling:
    """Test CORS middleware functionality"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/api/health")
        assert response.status_code == 200
        # Note: TestClient doesn't fully simulate CORS, but we can test the middleware is configured

class TestAsyncEndpoints:
    """Test async functionality of endpoints"""
    
    @pytest.mark.asyncio
    async def test_async_client_reverse(self):
        """Test reverse endpoint with async client"""
        with patch.object(TemporalClient, 'execute_reverse_workflow') as mock_execute:
            mock_execute.return_value = {
                "workflow_id": "async-test-123",
                "reversed_text": "cnysa",
                "original_text": "async",
                "processing_time_ms": 100,
                "success": True,
                "error": None
            }
            
            async with AsyncClient(app=app, base_url="http://test") as ac:
                response = await ac.post(
                    "/api/reverse",
                    json={"text": "async"}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["result"] == "cnysa"

# Helper functions
def mock_open_html():
    """Mock file open for HTML content"""
    from unittest.mock import mock_open
    html_content = """
    <!DOCTYPE html>
    <html>
        <head><title>Test</title></head>
        <body><h1>Test App</h1></body>
    </html>
    """
    return mock_open(read_data=html_content)

# Test data fixtures
@pytest.fixture
def sample_requests():
    """Fixture providing sample request data"""
    return {
        "valid_reverse": {"text": "hello world"},
        "valid_llm": {"text": "Process this text", "operation": "summarize"},
        "empty_text": {"text": ""},
        "whitespace_text": {"text": "   "},
        "long_text": {"text": "a" * 1000},
        "unicode_text": {"text": "Hello 世界! 🌍"},
        "special_chars": {"text": "Hello, World! @#$%^&*()"},
    }

@pytest.fixture
def mock_responses():
    """Fixture providing mock response data"""
    return {
        "successful_workflow": {
            "workflow_id": "test-123",
            "reversed_text": "dlrow olleh",
            "original_text": "hello world",
            "processing_time_ms": 200,
            "success": True,
            "error": None
        },
        "failed_workflow": {
            "workflow_id": "test-456",
            "reversed_text": "",
            "original_text": "hello world",
            "processing_time_ms": 0,
            "success": False,
            "error": "Connection timeout"
        },
        "llm_summary": "This is a concise summary of the input text.",
        "llm_rephrase": "Here is the text rewritten in a different way.",
        "llm_analysis": "Sentiment: Neutral. Themes: Technology, Communication."
    }

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 