from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Enable CORS
CORS(app)

# Initialize migration
migrate = Migrate(app, db)

# Initialize database
db.init_app(app)

# Route to handle GET and POST requests for messages
@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        # Retrieve all messages ordered by created_at ascending
        messages = Message.query.order_by(Message.created_at).all()
        return jsonify([message.to_dict() for message in messages]), 200

    elif request.method == 'POST':
        # Create a new message with data from the request body
        data = request.get_json()
        body = data.get('body')
        username = data.get('username')

        if not body or not username:
            return jsonify({'error': 'Body and username are required'}), 400

        # Create new message and add to the database
        new_message = Message(body=body, username=username)
        db.session.add(new_message)
        db.session.commit()

        return jsonify(new_message.to_dict()), 201

# Route to handle PATCH and DELETE requests for a specific message by ID
@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.get(id)

    if not message:
        return jsonify({'error': 'Message not found'}), 404

    if request.method == 'PATCH':
        # Update the body of the message
        data = request.get_json()
        body = data.get('body')

        if not body:
            return jsonify({'error': 'Body is required to update the message'}), 400

        # Update the message's body and commit the changes
        message.body = body
        db.session.commit()

        # Return the updated message as JSON
        return jsonify(message.to_dict()), 200

    elif request.method == 'DELETE':
        # Delete the message from the database
        db.session.delete(message)
        db.session.commit()
        return jsonify({'message': f'Message with id {id} deleted successfully'}), 200

if __name__ == '__main__':
    app.run(port=5555)
