# Money-Transaction-System-using-Python-Flask
A simple yet elegant money transaction system that lets authorised users to check their mini statements, withdraw money, transfer money to someones account etc. 

HOW TO RUN THE PROJECT
----------------------

The Project is based on python-flask.

Install the below mentioned libraries before running the server:
----------------------------------------------------------------
We are using python3 for this project.

1. pip3 install flask
2. pip3 install flask_pymongo
3. pip3 install flask_cors
4. pip3 install bson
5. pip3 install datetime
6. pip3 install time
7. pip3 install os


Running the Server:
-------------------

In the Terminal/Command Prompt run the command - 

-> Navigate into the working directory money_transaction 

-> python3 server.py

--------------------

The Server will start running on the port 5000 (Make sure there are no active process running on port 5000. If so, Kill any such process)

Now, Open any web browser and Navigate to the url:
--------------------------------------------------

http://localhost:5000/login/

A login page will appear:

Username : nikhil
Password : nikhil

I have created a database of 100 users you can log in from any of the user provided in the dump of the database.

Database Dump taken : 14th May, 2019
