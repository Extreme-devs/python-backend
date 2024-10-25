from typing_extensions import override
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from qdrant_client.http.models import Filter, Range
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import VectorParams, Distance
import os
from rich.progress import Progress
from rich import print
import time

from .langchain_init import openAIEmbeddings
from .debug import *
from .logs import logs, logging
from .config import settings

load_dotenv()


class VectorDB(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def insert(
        self,
        collection_name: str,
        embedding: str,
        document: str,
        metadata: dict,
        index=None,
    ):
        pass

    @abstractmethod
    def bulk_insert(
        self,
        collection_name: str,
        embeddings: list,
        documents: list,
        metadatas: list,
        indexes=None,
    ):
        pass

    def batch_insert(self, documents: list):
        print(f"ToDo: Implement batch insert")
        pass

    """
    Documnets must have embeddings, documents and metadatas
    
    indexes is opional
    """

    @abstractmethod
    def search(self, collection_name: str, query: str, limit: int):
        pass

    @abstractmethod
    def delete_by_id(self, collection_name: str, id: str):
        pass

    @abstractmethod
    def bulk_delete(self, collection_name: str, id: list):
        pass

    @abstractmethod
    def get_by_id(self, collection_name: str, id: str):
        pass

    @abstractmethod
    def bulk_get_by_id(self, collection_name: str, id: list):
        pass

    @abstractmethod
    def get_collection(self, collection_name: str):
        pass

    @abstractmethod
    def get_collections(self):
        pass

    @abstractmethod
    def create_collection(self, collection_name: str):
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def get_collection_size(self, collection_name: str):
        pass

    @abstractmethod
    def head_collection(self, collection_name: str):
        pass


class VectorDBwithCollection:
    def __init__(self, collection_name: str, vector_db: VectorDB):
        self.vector_db = vector_db
        self.collection_name = collection_name

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            attr = getattr(self.vector_db, name)
            if callable(attr):
                if "collection_name" in attr.__code__.co_varnames:
                    return attr(self.collection_name, *args, **kwargs)
                else:
                    return attr(*args, **kwargs)
            return attr

        return wrapper


class QdrantDB(VectorDB):
    def __init__(self, host: str, api_key: str):
        super().__init__()
        self.client = QdrantClient(host, api_key=api_key, timeout=60)

    @override
    def create_collection(self, collection_name: str):
        info_message(f"Creating collection: {collection_name}")
        try:
            self.client.get_collection(collection_name)
            error_message(f"Collection named: {collection_name} already exists")
        except Exception as e:
            if "Not found" in str(e):
                self.client.create_collection(
                    collection_name,
                    vectors_config={
                        "content": VectorParams(size=3072, distance=Distance.COSINE),
                    },
                )
                success_message(f"Collection named: {collection_name} created")
            else:
                print(f"Error: {e}")

    @override
    def get_collection(self, collection_name: str):
        try:
            collection = self.client.get_collection(collection_name)
            return collection
        except Exception as e:
            if "Not found" in str(e):
                error_message(f"Collection named: {collection_name} not found")
            else:
                error_message(f"Error: {e}")
        return None

    @override
    def delete_collection(self, collection_name: str):
        info_message(f"Deleting collection: {collection_name}")
        col = self.get_collection(collection_name)
        if col is None:
            return
        try:
            self.client.delete_collection(collection_name)
            success_message(f"Collection named: {collection_name} deleted")
        except Exception as e:
            error_message(f"Error: {e}")

    @override
    def delete_by_id(self, collection_name: str, id: str):
        info_message(
            f"Deleting document with id: {id} from collection: {collection_name}"
        )
        try:
            self.client.delete(collection_name, [id])
            success_message(f"Deleted document with id: {id}")
        except Exception as e:
            error_message(f"Error: {e}")

    @override
    def bulk_delete(self, collection_name: str, id: list):
        info_message(
            f"Deleting documents with id: {id} from collection: {collection_name}"
        )
        try:
            self.client.delete(collection_name, id)
            success_message(f"Deleted documents with id: {id}")
        except Exception as e:
            error_message(f"Error: {e}")

    @logging
    def search(self, collection_name, query, limit=50, filter=None):
        info_message(f"Searching in collection: {collection_name} for query: {query}")
        try:
            embedding = openAIEmbeddings.embed_query(query)
            query_filter = None
            if filter is not None:
                must = []
                for key, value in filter.items():
                    must.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(
                                value=value,
                            ),
                        )
                    )
                query_filter = models.Filter(must=must)
                # query_filter = filter
            results = self.client.search(
                collection_name=collection_name,
                query_vector=("content", embedding),
                limit=limit,
                with_payload=True,
                with_vectors=False,
                query_filter=query_filter,
            )
            success_message(f"Found {len(results)} results")
            return results
        except Exception as e:
            error_message(f"Error: {e}")
            return []

    @override
    def insert(
        self,
        collection_name: str,
        embedding: str,
        payload: dict,
        index=None,
    ):
        try:
            if index is None:
                index = self.get_collection_size(collection_name)
            self.client.upsert(
                collection_name,
                points=[
                    {"id": index, "vector": {"content": embedding}, "payload": payload}
                ],
            )
            success_message(f"Uploaded document with id: {index}")
        except Exception as e:
            error_message(f"Error: {e}")

    @override
    def bulk_insert(
        self,
        collection_name: str,
        embeddings: list,
        metadatas: list,
        indexes=None,
    ):
        # info_message(f"Uploading {len(embeddings)} documents to {collection_name}")
        N = len(embeddings)
        if indexes is None:
            tmp = self.get_collection_size(collection_name)
            indexes = [tmp + i for i in range(N)]
        points = []
        for i in range(len(embeddings)):
            metadata = metadatas[i]
            points.append(
                {
                    "id": indexes[i],
                    "vector": {"content": embeddings[i]},
                    "payload": metadata,
                }
            )
        self.client.upsert(collection_name, points=points)
        # success_message(f"Uploaded {len(embeddings)} documents to {collection_name}", newline=True)

    @override
    def batch_insert(self, collection_name, documents: list, batch_size=100):
        N = len(documents)
        with Progress() as progress:
            task1 = progress.add_task("[yellow]Uploading to Qdrant", total=N)
            for i in range(0, N, batch_size):
                batch = documents[i : i + batch_size]
                for _ in range(25):
                    try:
                        progress.update(
                            task1,
                            description=f"[yellow]Uploading batch [bold]{i//batch_size + 1}/{N//batch_size + 1}[/bold], [bold]{i}[/bold] to [bold]{min(i+batch_size, N) - 1}[/bold]",
                        )
                        embeddings = [doc["embedding"] for doc in batch]
                        metadatas = [doc["metadata"] for doc in batch]
                        self.bulk_insert(
                            collection_name=collection_name,
                            embeddings=embeddings,
                            metadatas=metadatas,
                        )
                        break
                    except Exception as e:
                        error_message(f"Error: {e}")
                        error_message(
                            f"Error in batch {i//batch_size + 1}, retrying ... "
                        )
                        time.sleep(10)
                progress.update(task1, advance=len(batch))

    @override
    def get_by_id(self, collection_name: str, id: str):
        try:
            result = self.client.retrieve(collection_name=collection_name, ids=[id])
            return result
        except Exception as e:
            error_message(f"Error: {e}")
            return None

    @override
    def bulk_get_by_id(self, collection_name: str, ids: list):
        try:
            result = self.client.retrieve(collection_name=collection_name, ids=ids)
            return result
        except Exception as e:
            error_message(f"Error: {e}")
            return None

    @override
    def get_collections(self):
        try:
            collections = self.client.get_collections()
            return collections
        except Exception as e:
            error_message(f"Error: {e}")
            return []

    @override
    def get_collection_size(self, collection_name: str):
        point_count = self.client.count(collection_name)
        return point_count.count

    @override
    def get_range(self, l, r, user_id, collection_name: str):
        print("Getting range")
        time_filter = Filter(
            must=[
                models.FieldCondition(
                    key="created_at",
                    range=models.Range(
                        gt=None,
                        gte=l,
                        lt=None,
                        lte=r,
                    ),
                ),
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(
                        value=user_id,
                    ),
                ),
            ]
        )
        response = self.client.scroll(
            collection_name=collection_name, scroll_filter=time_filter, limit=10
        )
        return response

    @override
    def head_collection(self, collection_name: str, limit=5):
        try:
            result = self.client.scroll(collection_name, limit=limit)
            return result
        except Exception as e:
            error_message(f"Error: {e}")
            return


qdrant_db = QdrantDB(
    host=settings.QDRANT_HOST,
    api_key=settings.QDRANT_API_KEY,
)
