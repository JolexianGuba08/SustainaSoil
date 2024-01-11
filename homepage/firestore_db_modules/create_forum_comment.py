from homepage.firestore_db_modules.firestore_database_client import firestore_db
from datetime import datetime
from google.cloud.firestore_v1 import FieldFilter
from google.cloud import firestore


# create a comment to a post in the forum
def create_comment_forum(comment_id, content, post_id, user_id):
    db = firestore_db()

    comment_set = {
        'comment_id': comment_id,
        'content': content,
        'post_id': post_id,
        'user_id': user_id,
        'date_added': firestore.SERVER_TIMESTAMP,
    }

    # Create a reference to the collection
    collection_ref = db.collection('forum_comments')

    # Add a document to the collection
    doc_ref = collection_ref.document()
    doc_ref.set(comment_set)

    # For debugging purposes only! removed later for deployment
    print(f'Forum Comment added successfully with ID: {doc_ref.id}')


# get all the comments and query them by post id
def get_all_comments(post_id):
    db = firestore_db()

    # Create a reference to the collection
    collection_ref = db.collection('forum_comments')

    # Create a query against the collection
    query_ref = collection_ref.where(filter=FieldFilter('post_id', '==', post_id))

    # Retrieve all documents
    docs = query_ref.stream()

    comments = []

    for doc in docs:
        comments.append(doc.to_dict())

    return comments
