from flask import Flask, render_template, request, jsonify
import serial
import time

app = Flask(__name__)

# Global variable for the Arduino serial connection
arduino = None

def init_serial():
    global arduino
    print("Initializing serial connection...")
    arduino = serial.Serial('COM7', 9600, timeout=1)  # Ensure this COM port is correct for your setup
    time.sleep(2)  # Give time for the connection to stabilize

@app.teardown_appcontext
def close_serial(exception):
    global arduino
    if arduino and arduino.is_open:
        print("Closing serial connection...")
        arduino.close()

# Sample product data
products = {
    '8901491503020': {'Product ID': '8901491503020', 'Product Name': 'Lays Wafers', 'Product Description': 'Rs', 'Price': 20},
    '8901765119971': {'Product ID': '8901765119971', 'Product Name': 'Hauser Refill - Blue', 'Product Description': 'Rs', 'Price': 10},
    'X001FFR8PH': {'Product ID': 'X001FFR8PH', 'Product Name': 'Cold Coffee', 'Product Description': 'Rs', 'Price': 300},
}

# Sample cart data
cart = []

@app.route('/')
def index():
    return render_template('index.html', products=products, cart=cart)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    global arduino
    if arduino is None or not arduino.is_open:
        init_serial()

    scanned_code = request.form['scanned_code']
    if scanned_code in products:
        cart.append(products[scanned_code])
        print(f"Sending 'C' to Arduino for product {scanned_code}.")  # Debug print
        arduino.write(b'C')  # Send 'C' to Arduino
        time.sleep(1)  # Ensure data transmission time
        return jsonify({'cart': cart})
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/delete_from_cart', methods=['POST'])
def delete_from_cart():
    global arduino
    item_id = request.form['item_id']
    for item in cart:
        if item['Product ID'] == item_id:
            cart.remove(item)
            if arduino is None or not arduino.is_open:
                init_serial()
            print(f"Sending '0' to Arduino for item {item_id}.")  # Debug print
            arduino.write(b'0')  # Send '0' to Arduino
            time.sleep(1)  # Ensure data transmission time
            break
    return jsonify({'cart': cart})

@app.route('/buy', methods=['GET', 'POST'])
def buy():
    # Implement payment processing logic here
    return 'Payment processing...'

if __name__ == '__main__':
    app.run(debug=True)
