from homepage.firestore_db_modules.firestore_database_client import firestore_db
from datetime import datetime
from google.cloud.firestore_v1 import FieldFilter
from google.cloud import firestore


# create a post
def create_post_forum(post_id, user_id, attachment, is_attachment, content):
    db = firestore_db()

    post_set = {
        'post_id': post_id,
        'user_id': user_id,
        'attachment': attachment,
        'is_attachment': is_attachment,
        'content': content,
        'date_added': firestore.SERVER_TIMESTAMP,
        'likes': 0
    }

    # Create a reference to the collection
    collection_ref = db.collection('forum_posts')

    # Add a document to the collection
    doc_ref = collection_ref.document()
    doc_ref.set(post_set)

    # For debugging purposes only! removed later for deployment
    print(f'Forum Post added successfully with ID: {doc_ref.id}')


# get all the posts and order them by date added
def get_all_posts():
    db = firestore_db()

    # Create a reference to the collection
    collection_ref = db.collection('forum_posts')

    # Create a query against the collection
    query_ref = collection_ref.order_by('date_added', direction=firestore.Query.DESCENDING)

    # retrieve all documents
    docs = query_ref.stream()

    posts = []

    for doc in docs:
        posts.append(doc.to_dict())

    return posts
