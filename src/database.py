"""Database connection and query utilities."""

import pandas as pd
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st

from src.config import config


class DatabaseConnection:
    """Manages PostgreSQL database connections and queries."""
    
    def __init__(self):
        self._engine: Optional[Engine] = None
    
    @property
    def engine(self) -> Engine:
        """Get or create the database engine."""
        if self._engine is None:
            connection_string = config.database.get_connection_string()
            self._engine = create_engine(connection_string, pool_pre_ping=True)
        return self._engine
    
    def test_connection(self) -> tuple[bool, str]:
        """
        Test the database connection.
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            return True, "Connection successful"
        except SQLAlchemyError as e:
            return False, f"Connection failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def get_tables(self) -> List[str]:
        """Get list of all tables in the database."""
        try:
            query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return [row[0] for row in result]
        except SQLAlchemyError as e:
            st.error(f"Error fetching tables: {str(e)}")
            return []
    
    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        Get column information for a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            DataFrame with column information
        """
        try:
            query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = :table_name
                ORDER BY ordinal_position;
            """
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {"table_name": table_name})
                columns = ["Column", "Type", "Nullable", "Default"]
                data = [list(row) for row in result]
                return pd.DataFrame(data, columns=columns)
        except SQLAlchemyError as e:
            st.error(f"Error fetching table info: {str(e)}")
            return pd.DataFrame()
    
    def query_signups(
        self,
        table_name: str = "user_signups",
        limit: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Query user signup data from the database.
        
        Args:
            table_name: Name of the signups table
            limit: Maximum number of rows to return
            filters: Dictionary of column:value pairs to filter by
            
        Returns:
            DataFrame with signup data
        """
        try:
            query = f"SELECT * FROM {table_name}"
            params = {}
            
            # Add filters if provided
            if filters:
                conditions = []
                for i, (col, val) in enumerate(filters.items()):
                    param_name = f"param_{i}"
                    conditions.append(f"{col} = :{param_name}")
                    params[param_name] = val
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
            
            # Add limit if provided
            if limit:
                query += f" LIMIT {limit}"
            
            return pd.read_sql(text(query), self.engine, params=params)
        except SQLAlchemyError as e:
            st.error(f"Error querying signups: {str(e)}")
            return pd.DataFrame()
    
    def execute_custom_query(self, query: str) -> pd.DataFrame:
        """
        Execute a custom SQL query.
        
        Args:
            query: SQL query string
            
        Returns:
            DataFrame with query results
        """
        try:
            return pd.read_sql(text(query), self.engine)
        except SQLAlchemyError as e:
            st.error(f"Error executing query: {str(e)}")
            return pd.DataFrame()
    
    def get_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table."""
        try:
            query = f"SELECT COUNT(*) FROM {table_name}"
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return result.fetchone()[0]
        except SQLAlchemyError as e:
            st.error(f"Error counting rows: {str(e)}")
            return 0


# Global database connection instance
@st.cache_resource
def get_database_connection() -> DatabaseConnection:
    """Get a cached database connection instance."""
    return DatabaseConnection()

