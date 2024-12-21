from bson import ObjectId
from pymongo.collection import Collection
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# Utility functions
def serialize_doc(doc):
    """Converts MongoDB document to JSON serializable format."""
    doc['_id'] = str(doc['_id'])
    return doc
