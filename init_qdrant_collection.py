from core.vector_db import qdrant_db

qdrant_db.delete_collection("image_descriptions")
qdrant_db.create_collection("image_descriptions")

print(qdrant_db.get_collections())
