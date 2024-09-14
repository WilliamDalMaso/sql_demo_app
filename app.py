from flask import Flask, request, jsonify, send_from_directory
import sqlite3

# Initialize the Flask app and configure it to serve static files
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Disable caching (for development purposes)
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            checkin TEXT NOT NULL,
            checkout TEXT NOT NULL,
            car_model TEXT NOT NULL,
            car_size TEXT NOT NULL,
            license_plate TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Serve the frontend (index.html) at the root URL
@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

# Route to create a new reservation (POST)
@app.route('/reserve', methods=['POST'])
def reserve_spot():
    data = request.json  # Get data from the client
    try:
        conn = sqlite3.connect('parking.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO reservations (name, email, phone, checkin, checkout, car_model, car_size, license_plate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['name'], data['email'], data['phone'], data['checkin'], data['checkout'], data['car_model'], data['car_size'], data['license_plate']))

        conn.commit()
        return jsonify({'message': 'Reservation successful!'}), 201

    except sqlite3.IntegrityError:
        return jsonify({'error': 'A reservation with this email already exists.'}), 409

    finally:
        conn.close()

# Route to retrieve a reservation (GET)
@app.route('/retrieve/<email>', methods=['GET'])
def retrieve_reservation(email):
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM reservations WHERE email = ?', (email,))
    reservation = cursor.fetchone()

    conn.close()

    if reservation:
        result = {
            'name': reservation[1],
            'email': reservation[2],
            'phone': reservation[3],
            'checkin': reservation[4],
            'checkout': reservation[5],
            'car_model': reservation[6],
            'car_size': reservation[7],
            'license_plate': reservation[8]
        }
        return jsonify(result), 200
    else:
        return jsonify({'error': 'No reservation found for this email.'}), 404

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)