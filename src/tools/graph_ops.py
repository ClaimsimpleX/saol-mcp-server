import logging
import os
from neo4j import GraphDatabase
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_driver = None

def init_neo4j() -> bool:
    """
    Initializes the Neo4j driver using environment variables.
    Returns True if successful, False otherwise.
    """
    global _driver
    if _driver:
        return True

    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    if not uri or not user or not password:
        logger.warning("Neo4j environment variables (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD) are missing.")
        return False

    try:
        _driver = GraphDatabase.driver(uri, auth=(user, password))
        _driver.verify_connectivity()
        logger.info("Neo4j driver initialized and connected.")
        return True
    except Exception as e:
        logger.warning(f"Failed to initialize Neo4j driver: {e}. Tools depending on Neo4j will fail.")
        return False

def cypher_query(query: str, params: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    """
    Executes a Cypher query against the Neo4j database.
    
    Args:
        query (str): The Cypher query string.
        params (Dict[str, Any]): Parameters for the query.
        
    Returns:
        List[Dict[str, Any]]: List of records returned by the query.
    """
    if not _driver and not init_neo4j():
        return [{"error": "Neo4j not initialized"}]

    try:
        with _driver.session() as session:
            result = session.run(query, params)
            records = [record.data() for record in result]
            logger.info(f"Executed Cypher query. Returned {len(records)} records.")
            return records
    except Exception as e:
        logger.error(f"Error executing Cypher query: {e}")
        return [{"error": str(e)}]
