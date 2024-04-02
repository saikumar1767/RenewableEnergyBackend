from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from datetime import datetime, timezone
import pandas as pd
from datetime import datetime

# The absolute path to the directory containing this script
current_directory = os.path.dirname(os.path.realpath(__file__))

# The absolute path to the Secret_Key.txt file
secret_key_file_path = os.path.join(current_directory, "Secret_Key.txt")

with open(secret_key_file_path, "r") as file:
    # Read the content of the file
    text_content = file.read().strip()

secret_key = text_content

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'users.db')  # Using SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key  # Secret key for JWT token generation
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
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))

def create_tables():
    with app.app_context():
        db.create_all()
        df = pd.read_csv('energyData.csv')
        # Iterate over rows and insert into database
        for _, row in df.iterrows():
            timestamp_str = row['timestamp']
            modified_timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
            energy_data = EnergyData(username=row['username'], energy_source=row['energy_source'], consumption=row['consumption'], generation=row['generation'], timestamp=modified_timestamp)
            db.session.add(energy_data)

        # Commit the changes
        db.session.commit()

if __name__ == '__main__':
    create_tables()