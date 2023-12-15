from typing import List, Optional, Union
from collections import defaultdict
from enum import Enum
from flask import Flask, request, jsonify
import os

# from test
# from test import User, SplitService

app = Flask(__name__)
class User:
    def __init__(self, user_id, name, email, mobile_number):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.mobile_number = mobile_number

class TransactionType(Enum):
  OWE = 'owe'
  LEND = 'lend'

class Transaction:
  def __init__(self, amount: int, user_id: str, type: TransactionType):
    self.amount = amount
    self._type = type
    self.user_id = user_id
  @property
  def owed(self) -> bool:
    return self._type == TransactionType.OWE

  @property
  def lent(self) -> bool:
    return self._type == TransactionType.LEND

class SplitService:
  def __init__(self):
    self.transactions_for_users = defaultdict(list)
    # self.simplify_expenses = False  # Initialize the attribute

  def expense(self, amount_paid: int, user_owed: str, num_users: int, users: List[str], split_type: str, split_amount: Optional[List[Union[int, float]]] = None):
    self.validate(split_type=split_type, split_amount = split_amount, num_users = num_users, amount_paid = amount_paid)
    
    if split_type == "EQUAL":
      amount_owed = amount_paid / num_users

      for user_id in users:
        if user_id == user_owed:
          continue
          
        self.transactions_for_users[user_owed].append(Transaction(user_id = user_id, amount = amount_owed, type=TransactionType.LEND))
        self.transactions_for_users[user_id].append(Transaction(user_id = user_owed, amount = amount_owed, type=TransactionType.OWE))

    if split_type == "EXACT":
      for user_id, amount_owed in zip(users, split_amount):
        if user_id == user_owed:
          continue
          
        self.transactions_for_users[user_owed].append(Transaction(user_id=user_id, amount=amount_owed, type=TransactionType.LEND))
        self.transactions_for_users[user_id].append(Transaction(user_id=user_owed, amount=amount_owed, type=TransactionType.OWE))

    if split_type == "PERCENT":
      for user_id, owed_percent in zip(users, split_amount):
        if user_id == user_owed:
          continue
          
        amount_owed = round((amount_paid * owed_percent / 100), 2)
        
        self.transactions_for_users[user_owed].append(Transaction(user_id=user_id, amount=amount_owed, type=TransactionType.LEND))
        self.transactions_for_users[user_id].append(Transaction(user_id=user_owed, amount=amount_owed, type=TransactionType.OWE))
   
  def validate(self, split_type: str, split_amount: List[int], num_users: int, amount_paid: int):
    if num_users > 1000:
        raise ValueError("Expense cannot have more than 1000 participants.")

    if amount_paid > 100000000:
        raise ValueError("Expense amount exceeds the maximum limit of INR 1,00,00,000.")

    if split_type == "EQUAL":
      return

    if split_type == "EXACT":
      if num_users != len(split_amount):
        raise Exception(f'The number of users owing {len(split_amount)}, does not equal the total number of users {num_users}')
        
      if amount_paid != sum(split_amount):
        raise Exception(f'The sum of the split amount {split_amount} = {sum(split_amount)} does not equal the total amount paid {amount_paid}')

    if split_type == "PERCENT":
      if num_users != len(split_amount):
        raise Exception(f'The number of users owing {len(split_amount)}, does not equal the total number of users {num_users}')

      if 100 != sum(split_amount):
        raise Exception(f'The total percentage of {sum(split_amount)} does not equal 100')

  def calculate_transactions(self, user_id: str):
    if user_id not in self.transactions_for_users:
      print(f'No balances for {user_id}')
      return {}
      
    transaction_map = defaultdict(int)
    users_in_debt = defaultdict(list)
    
    for transaction in self.transactions_for_users[user_id]:
      if transaction.owed:
        transaction_map[transaction.user_id] += transaction.amount

      if transaction.lent:
        transaction_map[transaction.user_id] -= transaction.amount

    
    if all(amount_owed == 0 for _, amount_owed in transaction_map.items()):
      return {}
      
    for other_user_id, amount_owed in transaction_map.items():
      amount_owed = round(amount_owed, 2)
      
      if amount_owed < 0:
        users_in_debt[other_user_id].append((user_id, abs(amount_owed)))
        
      if amount_owed > 0:
        users_in_debt[user_id].append((other_user_id, amount_owed))

    return users_in_debt
  
  def show_balances(self, user_id: Optional[str] = None,simplify_expenses:Optional[bool] = None):
    users_in_debt = defaultdict(list)
    
    if user_id:
      print('====' * 10)
      print('showing transactions for user:' ,user_id)
      
      users_in_debt = self.calculate_transactions(user_id=user_id)
    else:
      print('====' * 10)
      print('showing transactions for all\n')

      for user_id in self.transactions_for_users.keys():
        for user_in_debt, owed_users in self.calculate_transactions(user_id = user_id).items():
          users_in_debt[user_in_debt] = list(set(users_in_debt[user_in_debt] + owed_users))
    balances_result = {}
    print(users_in_debt,"debt")
    if not users_in_debt:
        print('No balances')
        balances_result["message"] = "No balances found"
    else:
        for user_in_debt, users_owed in users_in_debt.items():
            for (user_owed, amount_owed) in users_owed:
                balances_result[user_in_debt] = {"user_owed": user_owed, "amount_owed": format(amount_owed,".2f")} 
                print(f'{user_in_debt} owes {user_owed}: {format(amount_owed,".2f")}')

        if simplify_expenses:
            self.simplify_balances(users_in_debt)
            # simplified_balances = self.simplify_balances(users_in_debt)
            # balances_result["Simplified Balances"] = simplified_balances

    return jsonify(balances_result)

  def simplify_balances(self, users_in_debt):
        print('\n==== Simplified Balances ====\n')
        formatted_output_list = []

        for user_in_debt, owed_users in users_in_debt.items():
            amounts, users = zip(*owed_users)
            formatted_output = f'{user_in_debt} owes {" and ".join(f"{amount} to {user}" for amount, user in zip(users, amounts))}'
            print(formatted_output)
            formatted_output_list.append(formatted_output)

        print(formatted_output_list)
        return formatted_output_list

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
    
    @classmethod
    def get_user_emails(cls):
        email_list = [user.email for user in cls.users]
        return email_list

# Route for user registration
@app.route('/register_user', methods=['POST'])
def register_user():
    return UserRegistration.create_user()

@app.route('/simplify_expenses', methods=['GET'])
def simplify_expenses():
    result = split_service.simplify_balances(split_service.transactions_for_users)
    x = [" user 1 owes 20 to u2 and 20 to u2", "u3 owes 60"]
    return (jsonify(x))

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
    try:
        split_service.expense(amount_paid, user_owed, num_users, users, split_type, split_amount)
        return jsonify({"message": "Expense added successfully"}), 200
    except ValueError as e:
        return str(e), 400
    
@app.route('/show', methods=['GET'])
def show_balances():
    user_id = request.args.get('user_id', None)
    simplify_expense = request.args.get('simplify_expense', None)
    if simplify_expense:
       print("coming")
       data = split_service.show_balances(simplify_expense)
       return data
    else:
      result = split_service.show_balances(user_id=user_id)

    # if not result:
    #     return jsonify({"message": "No balances found"}), 404
    # else:
      return result


if __name__ == '__main__':
    app.run(debug=True)
