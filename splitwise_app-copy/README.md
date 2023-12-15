# Expense Management System

## Table of Contents
- [Introduction](#introduction)
- [Architecture](#architecture)
- [API Contracts](#api-contracts)
- [Class Structure](#class-structure)
- [Usage](#usage)


## Introduction

This Expense Management System is designed to help users manage and track expenses among multiple participants. It supports various expense types such as EQUAL, EXACT, and PERCENT, with validations for the number of participants and expense amounts.

## Architecture

### System Components

The system consists of the following components:

1. **User Management:** Handles user information including userId, name, email, and mobile number.

2. **Expense Management:** Manages expenses, including types (EQUAL, EXACT, PERCENT), participants, and amount. It also calculates balances and simplifies expenses.

3. **Notification Service:** Sends email notifications for expense participation and weekly reminders.

### Architecture Diagram


## API Contracts

### Add Expense
Mentioning various API endpoints for creating users, add_expense and for show balances api
1. **Crate user Endpoint :** -->>register_user api
    **First Endpoint:** /register_user
    
    Method: POST
    
    Request:json
    {
    "user_id": "u1",
    "name": "Bhupesh",
    "email":"bhupeshpal123@gmail.com",
    "mobile_number":"123456789"
    }

    **Second Endpoint:** /get_users
    Method: GET

    Response:json

    {
    "users": [
        {
            "email": "bhupeshpal123@gmail.com",
            "mobile_number": "123456789",
            "name": "Bhupesh",
            "user_id": "u1"
        }
    ]
    }

2. **Add expense Endpoint**: /add_expense

    Method: POST

    Request:json
    
    {
    "amount_paid": 1000,
    "user_owed": "u1",
    "num_users": 4,
    "users": ["u1", "u2", "u3", "u4"],
    "split_type": "EQUAL",
    "split_amount": null
    }

3. **Show Balances Endpoint**: /show

    Method: GET

    Request:json
    {
    "user_id": "u1"
    }
   
4. **Simplify Expense**:/show

    