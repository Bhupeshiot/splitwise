from flask import Flask, request, jsonify, Response
from enum import Enum

# from test
from test import User, SplitService
app = Flask(__name__)

split_service = SplitService()

class UserRegistration:
    users = []
    @classmethod
    def create_user(cls):
        data = request.json  # Assuming the data is sent in JSON format

        # Extracting values with specific names
        user_id = data.get('user_id')
        name = data.get('name')
        email = data.get('email')
        mobile_number = data.get('mobile_number')

        # Creating a new user
        new_user = User(user_id, name, email, mobile_number)
        cls.users.append(new_user)

        return jsonify({"message": "User created successfully", "user": {"user_id": new_user.user_id, "name": new_user.name}})

    @classmethod
    def get_users(cls):
        users_data = [{"user_id": user.user_id, "name": user.name, "email": user.email, "mobile_number": user.mobile_number} for user in cls.users]
        return jsonify({"users": users_data})

# Route for user registration
@app.route('/register_user', methods=['POST'])
def register_user():
    return UserRegistration.create_user()

# Route for getting all users
@app.route('/get_users', methods=['GET'])
def get_users():
    return UserRegistration.get_users()

@app.route('/add_expense', methods=['POST'])
def add_expense():
    global split_service  # Use the global variable

    data = request.json
    amount_paid = data.get('amount_paid')
    user_owed = data.get('user_owed')
    num_users = data.get('num_users')
    users = data.get('users')
    split_type = data.get('split_type')
    split_amount = data.get('split_amount')
    split_service.expense(amount_paid, user_owed, num_users, users, split_type, split_amount)
    return jsonify({"message": "Expense added successfully"})

# @app.route('/show_balances', methods=['GET'])
# def show_balances():
#     # user_id = request.args.get('user_id')
#     user_id = request.args.get('user_id')
#     return jsonify(split_service.show(user_id))

#     # Call the method that prints user info
#     # result = split_service.show(user_id)

#     # Create a custom response
#     # response = Response(status=200)
#     # response.headers['Content-Type'] = 'text/plain'
#     # response.data = f'User info printed for user_id: {user_id}' if user_id else 'User info printed for all users'

#     # return jsonify(result)


# # API to get expenses for a user
# @app.route('/get_expenses', methods=['GET'])
# def get_expenses():
#     user_id = request.args.get('user_id')
#     return jsonify(split_service.expense(user_id))

# # API to get balances


# @app.route('/balances', methods=['GET'])
# def get_balances():
#     user_id = request.args.get('user_id')
#     return jsonify(split_service.calculate_transactions(user_id))


#     # return split_service.show()
#     # return jsonify({"message": "Balances displayed"})

@app.route('/show', methods=['GET'])
def show_balances():
    user_id = request.args.get('user_id', None)

    users_in_debt = split_service.calculate_transactions(user_id=user_id)

    if not users_in_debt:
        return jsonify({"message": "No balances"}), 200

    result = {}
    for user_in_debt, users_owed in users_in_debt.items():
        result[user_in_debt] = [{"user_owed": user_owed, "amount_owed": amount_owed} for user_owed, amount_owed in users_owed]

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)
