from flask import Flask, render_template, redirect, jsonify, request, abort, Response, url_for, session, _request_ctx_stack
from flask_api import status
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from collections import defaultdict
from hashlib import sha256
from datetime import datetime
from random import randint

import requests
import json
import time
import re
import os
import ast
import csv

from WT_II_PY_BlockChain import *
# from WT_II_PY_QR_extract import *

application = Flask(__name__)
application.config['SECRET_KEY'] = "myBank api"
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myBank.db'

headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
session_options = {'autocommit':False, 'autoflush':False}
db = SQLAlchemy(application)

from configuration import *

db.create_all()

blockchain = Blockchain()
blockchain.generate_block_zero()

peers = set()
Payment_Portal_Gateway = "http://127.0.0.1:9999"
Transactions_List = []

def DPSdateconverttostring(datetimeobj):
    year = datetimeobj.year
    month = datetimeobj.month
    day = datetimeobj.day
    hour = datetimeobj.hour
    minute = datetimeobj.minute
    second = datetimeobj.second
    return str(day)+"-"+str(month)+"-"+str(year)+":"+str(second)+"-"+str(minute)+"-"+str(hour)

def DPSdateconvertstringtodate(datetimestring):
    dsplitt = datetimestring.split(':')
    date = [int(splitval) for splitval in dsplitt[0].split('-')]
    time = [int(splitval) for splitval in dsplitt[1].split('-')]
    
    day = date[0]
    month = date[1]
    year = date[2]
    
    hours = time[2]
    minutes = time[1]
    seconds = time[0]

    return datetime(year=year, month=month, day=day, hour=hours, minute=minutes,second=seconds)

def time_convertion(curr_time):
    return datetime.fromtimestamp(curr_time).strftime('%H:%M')


def consensus_mechanism():
	global blockchain
	
	longest_chain = None
	cur_len = len(blockchain.chain)
	
	for peer in peers:
		response = requests.get('{}chain'.format(peer))
		length = response.json()['length']
		chain = response.json()['chain']
	
		if length > cur_len and blockchain.chain_valid(chain):
			cur_len = length
			longest_chain = chain

	if longest_chain:
		blockchain = longest_chain
		return True

	else:
		return False


def propogate_block(block):
	try:
		for peer in peers:
			prop_to_peer = "{}add_block".format(peer)
			requests.post(prop_to_peer, data = json.dumps(block.__dict__, sort_keys=True))
	
	except:
		return Response({"Please try again later"}, status=400, mimetype='application/json')

def create_chain_from_dump(chain_dump):

	try:
		generated_blockchain = Blockchain()
		generated_blockchain.generate_block_zero()

		for block_id, block_data in enumerate(chain_dump):
			
			if block_id == 0:
				continue

			block = Block(block_data["index"], block_data["transactions"], block_data["timestamp"], block_data["previous_hash"], block_data["nonce"])
			proof = block_data['hash']
			added = generated_blockchain.add_block(block, proof)

			if added == False:
				return Response({"Chain is tampered."}, status=400, mimetype='application/json')
		
		return generated_blockchain
	
	except:
		return Response({"The server is under maintanence. Please get back later"}, status=400, mimetype='application/json')


@application.route('/Fetch_Transactions', methods=['GET'])
def fetch_transactions():

    global Transactions_List
    global Payment_Portal_Gateway

    Get_Block_Chain = "{}/chain".format(Payment_Portal_Gateway)

    try:
        response = requests.get(Get_Block_Chain)

        if response.status_code == 200:	
            block_data = []

            chain = json.loads(response.content)

            for block in chain["chain"]:
                for transaction in block["transactions"]:
                    transaction["index"] = block["index"]
                    transaction["hash"] = block["previous_hash"]
                    block_data.append(transaction)
            

            Transactions_List = sorted(block_data, key=lambda x:  x['timestamp'], reverse=True)
    
            print(Transactions_List)
            return Response({"Successfully fetched"}, status=200, mimetype='application/json')

    except:
        return Response({"The server is under maintanence. Please get back later"},status=400, mimetype='application/json')


@application.route('/pay', methods=['POST'])
def Payment_processing():

    transaction_id = request.get_json()['transaction_id']
    payer = request.get_json()['payer']
    payee = request.get_json()['payee']
    amount = request.get_json()['amount']
    balance = request.get_json()['balance']


    transaction_details = {
       'transaction_id' : transaction_id,
       'payer' : payer,
       'payee' : payee,
       'amount' : amount,
       'balance' : balance
    }

    new_transaction_gateway = "{}/new_transaction".format(Payment_Portal_Gateway)

    requests.post(new_transaction_gateway, json = transaction_details)

    new_mining_gateway = "{}/mine".format(Payment_Portal_Gateway)

    requests.get(new_mining_gateway)

    return Response({"Payment Successful"}, status=200, mimetype='application/json')
	

@application.route('/new_transaction', methods=['POST'])
def new_transaction():
	check_fields = ['transaction_id', 'payer', 'payee', 'amount', 'balance']
	
	try:
		transaction_details = request.get_json()
		
		for field in check_fields:
			if not transaction_details.get(field):
				return Response({"Transaction Data Invalid"}, status=404, mimetype='application/json')
	
		transaction_details["timestamp"] = DPSdateconverttostring(datetime.now())
	
		blockchain.add_new_transaction(transaction_details)
	
		return Response({"Transaction Saved Successfully"}, status=201, mimetype='application/json')
	
	except:
		return Response({"The server is under maintanence. Please get back later"}, status=400, mimetype='application/json')
	
	
@application.route('/chain', methods=['GET'])
def get_chain():
	save_chain_state = []

	for block in blockchain.__getBlockChain__():
		save_chain_state.append(block.__dict__)

	retval = {
		"length": len(save_chain_state), 
		"chain": save_chain_state, 
		"peers": list(peers)
	}
	
	return retval, 200


@application.route('/unmined_transactions')
def unmined_transactions():
	return json.dumps(blockchain.unconfirmed_transactions)


@application.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():

	try:
		unconfirmed_transaction_status = blockchain.mine()

		if unconfirmed_transaction_status == False:
			return Response({"No pending transactions"}, status=400, mimetype='application/json')

		else:
			chain_length = len(blockchain.chain)
			consensus_mechanism()

			if chain_length == len(blockchain.chain):
				propogate_block(blockchain.last_block)

			return Response({"Block Mined Successfully. Number of blocks in the chain - {}".format(blockchain.last_block.index)}, status=200, mimetype='application/json')

	except:
		return Response({"The server is under maintanence. Please get back later"}, status=400, mimetype='application/json')


@application.route('/add_block', methods=['POST'])
def add_new_block():
    block_data = request.get_json()
    block = Block(block_data["index"], block_data["transactions"], block_data["timestamp"], block_data["previous_hash"], block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if added == False:
        return Response({"The block was discarded"}, status=400, mimetype='application/json')

    return Response({"Successfully added to chain"}, status=200, mimetype='application/json')


@application.route('/register_peer', methods=['POST'])
def register_peers():
	global peers

	try:
		node_address = request.get_json()["node_address"]

		if not node_address:
			return Response({"Incorrect Data recieved"}, status=400, mimetype='application/json')

		peers.add(node_address)

		return Response({"Node successfully registered"}, status=200, mimetype='application/json')
	
	except:
		return Response({"The server is under maintanence. Please get back later"}, status=400, mimetype='application/json')


@application.route('/register_existing_miner', methods=['POST'])
def register_existing_miner():
	global blockchain
	global peers

	try:
		node_address = request.get_json()["node_address"]

		if not node_address:
			return Response({"Incorrect Data recieved"}, status=400, mimetype='application/json')

		data = {
			"node_address": request.host_url
		}

		response = requests.post(node_address + "/register_node", data = data)

		if response.status_code == 200:
			chain_dump = response.json()['chain']
			blockchain = create_chain_from_dump(chain_dump)
			peers.update(response.json()['peers'])
			return Response({"Successfully registered"}, status=200, mimetype='application/json')

		else:
			return Response({"Please try again later"}, status=400, mimetype='application/json')

	except:
		return Response({"The server is under maintanence. Please get back later"}, status=400, mimetype='application/json')

#----------------------------------------------------------------------------------------------------------------------------------------

@application.route('/')
def home():
	return render_template('login.html')

@application.route('/signup')
def signup():
	return render_template('signup.html')

@application.route('/transferFunds')
def transferFunds():
    if(session['user_available']):
	    return render_template('transferfunds.html')
    return redirect(url_for('logout'))

@application.route('/contactUs')
def contactUs():
    if(session['user_available']):
	    return render_template('contactusprofile.html')
    return redirect(url_for('logout'))

@application.route('/transactions')
def transactions():
    if(session['user_available']):
	    return render_template('transactions.html')
    return redirect(url_for('logout'))

@application.route('/processTransactions', methods=['GET'])
def processTransactions():
    response = fetch_transactions()
    global Transactions_List
    if(session['user_available']):
        resu = db.session.query(User).filter_by(email=session['current_user']).first()
        resp = db.session.query(Profile).filter_by(puid=resu.uid).first()
        uacn = resp.acc_no
        response_all = []
        i = 1
        sorted(Transactions_List, key = lambda k: k['timestamp'])
        for row in Transactions_List:
            rowd = {}
            if(row['payer']==uacn):
                rowd['tid'] = i
                rowd['date'] = DPSdateconvertstringtodate(row['timestamp']) 
                rowd['acnn']= row['payee']  
                rowd['transact'] = " - "+ row['amount']
                rowd['balance']= "Rs. "+str(int(row['balance'])-int(row['amount']))
                i += 1
            elif(row['payee']==uacn):
                rowd['tid'] = i
                rowd['date'] = DPSdateconvertstringtodate(row['timestamp'])
                rowd['acnn']= row['payer']  
                rowd['transact'] = " + "+ row['amount']
                rowd['balance']= "Rs. "+str(int(row['balance'])+int(row['amount']))
                i+= 1
            response_all.append(rowd)
        if(len(response_all)>15):
            response_all = response_all[0:15]
        #print(Transactions_List)
        return jsonify(response_all)
    return redirect(url_for('logout'))

@application.route('/otp', methods=['GET'])
def otp():
    ret = {}
    otp = str(randint(100000,1000000))
    ret['otp'] = otp
    return jsonify(ret)

@application.route('/profile', methods=['GET'])
def profile():
    if(session['user_available']):
        resu = db.session.query(User).filter_by(email=session['current_user']).first()
        resp = db.session.query(Profile).filter_by(puid=resu.uid).first()
        fname = resp.firstname
        lname = resp.lastname
        adhn = resp.aadhar_no
        phnn = resp.phone_no
        acnn = resp.acc_no
        blc = resp.balance
        return render_template('profile.html', firstname=fname, lastname=lname,aadhar_no=adhn,phn_no=phnn,acn=acnn,balance=blc, email=resu.email)
    return redirect(url_for('logout'))

@application.route('/editProfile', methods=['GET'])
def editProfile():
    if(session['user_available']):
        resu = db.session.query(User).filter_by(email=session['current_user']).first()
        resp = db.session.query(Profile).filter_by(puid=resu.uid).first()
        fname = resp.firstname
        lname = resp.lastname
        adhn = resp.aadhar_no
        phnn = resp.phone_no
        return render_template('editprofile.html', firstname=fname, lastname=lname,aadhar_no=adhn,phn_no=phnn,email=resu.email)
    return redirect(url_for('logout'))

@application.route('/processSignup', methods=['POST'])
def processSignup():
    email = request.form['email']
    pwd = request.form['password']
    pwd_rep = request.form['passwordr']
    if(pwd != pwd_rep):
        return jsonify({'error' : 'Passwords do not match!'})
    quer_res = db.session.query(User).filter_by(email = email)
    if(quer_res.scalar() is None):
        reg = User(email, pwd)
        db.session.add(reg)
        db.session.commit()
        resu = db.session.query(User).filter_by(email=email).first()
        obj = Profile(resu.uid, "", "", "","",str(randint(10000,100000)),str(randint(1000,100001)))
        db.session.add(obj)
        db.session.commit()
        return jsonify({'msg' : "Successfully created !"})
    else:
        return jsonify({'error' : 'User already exist !'}) 
    return jsonify({'msg' : "Successfully created!"})
    
@application.route('/processLogin', methods=['GET','POST'])
def processLogin():
    if(request.method == 'POST'):
        email = request.form['email']
        pwd = request.form['password']
        quer_res = User.query.filter_by(email=email)
        log = quer_res.first()
        ret = {}
        if(quer_res.scalar() is not None):
            if(log.password == pwd):
                current_user = email
                session['current_user'] = current_user
                session['user_available'] = True
                ret['response'] = 1
                ret['redirecturl'] = '/profile'
                return jsonify(ret) 
            else:
                ret['response'] = 0
                ret['error'] = 'Incorrect password !'
                return jsonify(ret) 
        else:
            ret['response'] = 0
            ret['error'] = 'User does not exist !'
            return jsonify(ret)
    return redirect(url_for('logout'))


@application.route('/processEditProfile', methods=['POST'])
def processEditprofile():
    if(session['user_available']):
        ret = {}
        fname = (request.form['fname']).strip()
        lname = (request.form['lname']).strip()
        adhn = (request.form['adhn']).strip()
        phnn = (request.form['phnn']).strip()
        #acnn = (request.form['acnn']).strip()
        email = (request.form['email']).strip()
        pwd =  (request.form['pwd']).strip()
        pwdr = (request.form['pwdr']).strip()
        if((pwd!="" and pwdr!="") and (pwd != pwdr)):
            ret['response'] = 0
            ret['error'] = '  Passwords do not match !'
            return jsonify(ret)

        if(" " in pwd):
            ret['response'] = 0
            ret['error'] = '  Password should not have spaces !'
            return jsonify(ret)

        quer_res = db.session.query(User).filter_by(email=email)
        if(quer_res.count()==1 and quer_res.first().email!=session['current_user']):
            ret['response'] = 0
            ret['error'] = '  User already exist !'
            return jsonify(ret)

        resu = db.session.query(User).filter_by(email=session['current_user']).first()
        user_id = resu.uid
        if(pwd.strip()==""):
            pwd = resu.password
        db.session.query(Profile).filter_by(puid=user_id).update(dict(firstname=fname, lastname=lname, aadhar_no=adhn, phone_no=phnn))
        db.session.query(User).filter_by(uid=user_id).update(dict(email=email, password=pwd))
        db.session.commit()
        session['current_user'] = email
        ret['response'] = 1
        ret['msg'] = 'Successfully updated!'
        ret['redirecturl'] = '/profile'
        return jsonify(ret)
    return redirect(url_for('logout'))


@application.route('/processTransferFunds', methods=['POST'])
def processtransferFunds():
    if(session['user_available']):
        ret = {}
        payee = (request.form['payee']).strip()
        amt = (request.form['amt']).strip()
        
        otp_enter = (request.form['otp_enter']).strip()
        otp_gen = (request.form['otp_gen']).strip()
        if(otp_enter!=otp_gen):
            ret['response'] = 0
            ret['error'] = 'Invalid OTP !'
            return jsonify(ret)
        
        resu = db.session.query(User).filter_by(email=session['current_user']).first()
        resp = db.session.query(Profile).filter_by(puid=resu.uid).first()
        payer = resp.acc_no
        balance = resp.balance
        transaction_id = str(randint(0,10000))

        if(int(balance)< int(amt)+500):
            ret['response'] = 0
            ret['error'] = 'Not enough balance !'
            return jsonify(ret)
        
        if(payer==payee):
            ret['response'] = 0
            ret['error'] = 'Cannot pay to self !'
            return jsonify(ret)

        resp_quer = db.session.query(Profile).filter_by(acc_no=payee)
        if(resp_quer.scalar() is None):
            ret['response'] = 0
            ret['error'] = 'Invalid Account No. !'
            return jsonify(ret)

        resp_payee = resp_quer.first()
        payee_uid = resp_payee.puid
        payee_balance = resp_payee.balance

        tpayload = {
		'transaction_id' : transaction_id,
		'payer' : payer,
		'payee' : payee,
		'amount' : amt,
		'balance' : balance
	    }

        response = requests.post(Payment_Portal_Gateway+'/pay', data = json.dumps(tpayload), headers = headers)

        status = response.status_code
        # status = 200
        if(status == 200):  #response.status
            resu = db.session.query(User).filter_by(email=session['current_user']).first()
            user_id = resu.uid
            new_balance = int(balance)-int(amt)
            db.session.query(Profile).filter_by(puid=user_id).update(dict(balance=new_balance))
            db.session.commit()

            new_balance_payee = int(payee_balance)+int(amt)
            db.session.query(Profile).filter_by(puid=payee_uid).update(dict(balance=new_balance_payee))

            tpayer = Transactions(user_id,str(amt),"NIL","Rs. "+str(new_balance))
            tpayee = Transactions(payee_uid,"NIL",str(amt),"Rs. "+  str(new_balance_payee))
            db.session.add(tpayer)
            db.session.commit()
            db.session.add(tpayee)
            db.session.commit()

            ret['response'] = 1
            ret['msg'] = 'Transaction successful !'
            return jsonify(ret)
        else:
            ret['response'] = 0
            ret['error'] = 'Transaction failed !'
            return jsonify(ret)
    return redirect(url_for('logout'))

@application.route('/processContactUs', methods=['POST'])
def processContactUs():
    if(session['user_available']):
        ret = {}
        fname = (request.form['fname']).strip()
        lname = (request.form['lname']).strip()
        email = (request.form['email']).strip()
        subject =  (request.form['subject']).strip()
        msg = (request.form['msg']).strip()
        ret['response'] = 1
        ret['msg'] = "Sent!"
        return jsonify(ret)
    return redirect(url_for('logout'))

@application.route('/logout')
def logout():
    session.clear()
    session['user_available'] = False
    session['current_user'] = ""
    return redirect(url_for('home'))


if __name__ == '__main__':	
	application.debug=True
	application.run(port=9999)