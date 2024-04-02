from flask import Flask, request, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask
from flask_cors import CORS

# The absolute path to the directory containing this script
current_directory = os.path.dirname(os.path.realpath(__file__))

# The absolute path to the Secret_Key.txt file
secret_key_file_path = os.path.join(current_directory, "app/Secret_Key.txt")

with open(secret_key_file_path, "r") as file:
    # Read the content of the file
    text_content = file.read().strip()

secret_key = text_content

app = Flask(__name__)
db_path = os.path.join(app.root_path, 'app/users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path  # Using SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key  # Secret key for JWT token generation
CORS(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class EnergyData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), db.ForeignKey('user.username'), nullable=False)
    energy_source = db.Column(db.String(50), nullable=False)
    consumption = db.Column(db.Float, nullable=False)
    generation = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# Function to generate JWT token
def generate_jwt_token(username):
     # Getting the current time in UTC
    current_time_utc = datetime.now(timezone.utc)

    # Defining token expiration time (1 day from the current time)
    expiration_time = current_time_utc + timedelta(days=1)

    # Create payload for the JWT token
    payload = {
        'username': username,
        'exp': expiration_time
    }

    # Encoding the payload to generate the JWT token
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token  # No need to decode as token is already a string

# Decorator definition for authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Missing authorization token'}), 401
        try:
            # Decode the JWT token and extract user information
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.username = payload['username']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check if username or email already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return jsonify({"message": "Username or email already exists"}), 400

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create and save the new user
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"message": "User registered successfully"}), 201
    
    except:
        return jsonify({"message": "Internal Server Error"}), 500


# Endpoint for user login
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        # Check if user exists
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # You can generate JWT token here
            token = generate_jwt_token(user.username)
            return jsonify({"token": token, "user": user.username }), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except:
        return jsonify({"message": "Internal Server Error"}), 500


@app.route('/energy/user', methods=['GET'])
@login_required
def get_energy_data():
    try:
        # Fetch energy data for the logged-in user
        energy_data = EnergyData.query.filter_by(username=g.username).all()
        # Serialize the data
        data = [{'id': entry.id, 'username': entry.username, 'energy_source': entry.energy_source, 'consumption': entry.consumption, 'generation': entry.generation, 'timestamp': entry.timestamp} for entry in energy_data]
        return data, 200
    except:
        return jsonify({"message": "Internal Server Error"}), 500


@app.route('/energy/filter', methods=['GET'])
@login_required
def filter_energy_data():
    try:
        # Get query parameters
        start_datetime = request.args.get('start_datetime')
        end_datetime = request.args.get('end_datetime')
        energy_source = request.args.get('energy_source')
        energy_data = []

        if start_datetime is None or end_datetime is None:
            # Fetch energy data for the logged-in user based on filters
            energy_data = EnergyData.query.filter(EnergyData.username == g.username)

        else:
            # Parse dates
            start_dateT = datetime.strptime(start_datetime, "%Y-%m-%dT%H:%M:%S")
            end_dateT = datetime.strptime(end_datetime, "%Y-%m-%dT%H:%M:%S")

            # Fetch energy data for the logged-in user based on filters
            energy_data = EnergyData.query.filter(EnergyData.timestamp >= start_dateT, EnergyData.timestamp <= end_dateT, EnergyData.username == g.username)

        if energy_source != "all":
            energy_data = energy_data.filter_by(energy_source=energy_source)

        energy_data = energy_data.all()

        # Serialize the data
        data = [{'username': entry.username, 'timestamp': entry.timestamp, 'energy_source': entry.energy_source, 'consumption': entry.consumption, 'generation': entry.generation} for entry in energy_data]
        return jsonify(data), 200
    except:
        return jsonify({"message": "Internal Server Error"}), 500


@app.route('/')
def home_page():
    return "Server is Up and running!"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int("5000"), debug=True)