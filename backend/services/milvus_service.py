import logging
from typing import List, Dict, Optional
from pymilvus import connections, Collection, utility
from core.config import get_settings
from services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class MilvusService:
    """Milvus Vector Database Service (Offline)"""
    
    def __init__(self):
        self.settings = get_settings()
        self.embedding_service = EmbeddingService()
        self.collection_name = self.settings.COLLECTION_NAME
        self.connection_alias = "default"
        
        # Connect to Milvus
        self._connect()
    
    def _connect(self):
        """Connect to Milvus"""
        try:
            connections.connect(
                alias=self.connection_alias,
                host=self.settings.MILVUS_HOST,
                port=self.settings.MILVUS_PORT
            )
            logger.info(f"✅ Connected to Milvus at {self.settings.MILVUS_HOST}:{self.settings.MILVUS_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    def get_collection(self) -> Collection:
        """Get or create collection"""
        try:
            if utility.has_collection(self.collection_name):
                collection = Collection(self.collection_name)
                collection.load()
                return collection
            else:
                logger.warning(f"Collection '{self.collection_name}' not found")
                return None
        except Exception as e:
            logger.error(f"Error getting collection: {e}")
            raise
    
    async def search(
        self,
        query_text: str,
        limit: int = 5,
        output_fields: Optional[List[str]] = None
    ) -> List[Dict]:
        """Search for similar documents"""
        try:
            # Get collection
            collection = self.get_collection()
            if not collection:
                logger.warning("No collection available for search")
                return []
            
            # Generate query embedding
            query_embedding = await self.embedding_service.create_single_embedding(query_text)
            
            # Default output fields
            if output_fields is None:
                output_fields = ["text", "source", "page"]
            
            # Search
            search_params = {
                "metric_type": "COSINE",
                "params": {"nprobe": 10}
            }
            
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                output_fields=output_fields
            )
            
            # Format results
            formatted_results = []
            for hits in results:
                for hit in hits:
                    result = {
                        "id": hit.id,
                        "score": hit.score,
                        "distance": hit.distance
                    }
                    # Add output fields
                    for field in output_fields:
                        result[field] = hit.entity.get(field)
                    
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def insert(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> List[int]:
        """Insert documents into Milvus"""
        try:
            collection = self.get_collection()
            if not collection:
                raise ValueError("Collection not available")
            
            # Generate embeddings
            embeddings = await self.embedding_service.create_embeddings(texts)
            
            # Prepare data
            entities = [
                embeddings,  # embedding field
                texts,       # text field
            ]
            
            # Add metadata fields if provided
            if metadatas:
                for key in metadatas[0].keys():
                    values = [m.get(key) for m in metadatas]
                    entities.append(values)
            
            # Insert
            insert_result = collection.insert(entities)
            collection.flush()
            
            logger.info(f"Inserted {len(texts)} documents")
            return insert_result.primary_keys
            
        except Exception as e:
            logger.error(f"Insert error: {e}")
            raise
    
    def delete(self, ids: List[int]) -> bool:
        """Delete documents by IDs"""
        try:
            collection = self.get_collection()
            if not collection:
                return False
            
            expr = f"id in {ids}"
            collection.delete(expr)
            collection.flush()
            
            logger.info(f"Deleted {len(ids)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False
    
    def check_connection(self) -> bool:
        """Check if Milvus is connected"""
        try:
            return connections.has_connection(self.connection_alias)
        except:
            return False
    
    def disconnect(self):
        """Disconnect from Milvus"""
        try:
            connections.disconnect(self.connection_alias)
            logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")