"""
Unit tests for database connectors
"""
import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestSQLServerConnector:
    """Test SQL Server connector functionality"""
    
    def test_connection_string_format(self):
        """Test that connection string is properly formatted"""
        from src.connectors.sql_server import SQLServerConnector
        
        connector = SQLServerConnector()
        
        # Mock environment variables
        with patch.dict('os.environ', {
            'SQL_SERVER_HOST': 'localhost',
            'SQL_SERVER_PORT': '1433',
            'SQL_SERVER_USER': 'sa',
            'SQL_SERVER_PASSWORD': 'TestPass123!'
        }):
            conn_str = connector._get_connection_string()
            
            assert 'localhost' in conn_str
            assert '1433' in conn_str
            assert 'sa' in conn_str
            assert 'TestPass123!' in conn_str
    
    @patch('src.connectors.sql_server.create_engine')
    def test_get_engine_creation(self, mock_create_engine):
        """Test that engine is created properly"""
        from src.connectors.sql_server import SQLServerConnector
        
        connector = SQLServerConnector()
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        engine = connector.get_engine()
        
        assert engine == mock_engine
        mock_create_engine.assert_called_once()
    
    def test_execute_query_error_handling(self):
        """Test error handling in query execution"""
        from src.connectors.sql_server import SQLServerConnector
        
        connector = SQLServerConnector()
        
        # Mock a failing connection
        with patch.object(connector, 'get_engine') as mock_engine:
            mock_engine.side_effect = Exception("Connection failed")
            
            result = connector.execute_query("SELECT 1")
            
            # Should return None on error
            assert result is None