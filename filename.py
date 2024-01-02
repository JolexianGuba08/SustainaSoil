import uuid


def generate_filename(user_id):
    # Generate a random UUID (Universally Unique Identifier)
    unique_id = uuid.uuid4().hex

    # Combine the random UUID with the user ID
    filename = f"{user_id}_{unique_id}"

    return filename


print(generate_filename(1234))
