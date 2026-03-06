from flask import Flask, request
from flask_restful import Resource, Api
from flasgger import Swagger
from bson.objectid import ObjectId
from core.database import collection

app = Flask(__name__)
api = Api(app)

# Ініціалізація Flasgger
swagger = Swagger(app, template={
    "info": {
        "title": "Library REST API",
        "description": "API for library management with Flask-RESTful, Flasgger, and MongoDB",
        "version": "1.0.0"
    }
})


# Допоміжна функція для конвертації MongoDB документа у JSON-формат
def serialize_book(book):
    book["id"] = str(book["_id"])
    del book["_id"]
    return book


class BookListResource(Resource):
    def get(self):
        """
        Get all books in the library with Limit-Offset pagination
        ---
        tags:
          - Books
        parameters:
          - in: query
            name: limit
            type: integer
            required: false
            default: 10
            description: Number of records to return
          - in: query
            name: offset
            type: integer
            required: false
            default: 0
            description: Number of records to skip
        responses:
          200:
            description: A list of books
        """
        limit = int(request.args.get('limit', 10))
        offset = int(request.args.get('offset', 0))

        # Синхронний запит до MongoDB з пагінацією
        cursor = collection.find().skip(offset).limit(limit)
        books = [serialize_book(book) for book in cursor]

        return books, 200

    def post(self):
        """
        Add a new book to the library
        ---
        tags:
          - Books
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - title
                - author
                - year
              properties:
                title:
                  type: string
                  example: "MongoDB: The Definitive Guide"
                author:
                  type: string
                  example: "Shannon Bradshaw"
                year:
                  type: integer
                  example: 2019
                status:
                  type: string
                  example: "available in the library"
        responses:
          201:
            description: The created book
        """
        data = request.get_json()

        # Додаємо статус за замовчуванням, якщо його немає
        if "status" not in data:
            data["status"] = "available in the library"

        result = collection.insert_one(data)
        data["id"] = str(result.inserted_id)
        del data["_id"]  # Прибираємо внутрішній _id для клієнта

        return data, 201


class BookResource(Resource):
    def get(self, book_id):
        """
        Get a specific book by ID
        ---
        tags:
          - Books
        parameters:
          - in: path
            name: book_id
            required: true
            type: string
            description: The MongoDB ObjectId of the book
        responses:
          200:
            description: Book details
          404:
            description: Book not found
        """
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return {"message": "Invalid ID format"}, 400

        book = collection.find_one({"_id": obj_id})
        if book:
            return serialize_book(book), 200
        return {"message": "Book not found"}, 404

    def delete(self, book_id):
        """
        Delete a book by ID
        ---
        tags:
          - Books
        parameters:
          - in: path
            name: book_id
            required: true
            type: string
            description: The MongoDB ObjectId of the book to delete
        responses:
          204:
            description: Book successfully deleted
          404:
            description: Book not found
        """
        try:
            obj_id = ObjectId(book_id)
        except Exception:
            return {"message": "Invalid ID format"}, 400

        result = collection.delete_one({"_id": obj_id})
        if result.deleted_count > 0:
            return '', 204
        return {"message": "Book not found"}, 404


# Реєстрація ресурсів [cite: 370]
api.add_resource(BookListResource, '/books')
api.add_resource(BookResource, '/books/<string:book_id>')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
