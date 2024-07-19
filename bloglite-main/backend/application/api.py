from flask_restful import Resource
from flask_restful import reqparse
from flask_restful import fields, marshal_with
from .models import Caretaker,Tasks,Contacts,UserPatient
from application.validation import BusinessValidationError
from application.database import db
from datetime import datetime
from main import app as app
from flask_security import auth_required
from sqlalchemy.sql import text
from werkzeug.security import generate_password_hash
import os

response_fields = {

    "user_id" : fields.String,
    "email": fields.String,
    "dob": fields.Integer,
    "location": fields.Integer,
    "phone": fields.Integer,
    "password": fields.Integer,
    "username": fields.Integer,
   
   
}
delete_response_fields = {

    "user_id" : fields.String  
   
}
  
'''
Request Parsers and Output Resource Fields for UserPatientAPI 
'''
user_parser = reqparse.RequestParser()
user_parser.add_argument("user_id")
user_parser.add_argument("email")
user_parser.add_argument("dob")
user_parser.add_argument("location")
user_parser.add_argument("phone")
user_parser.add_argument("password")

class UserPatientAPI(Resource):
    
    @marshal_with(response_fields)
    @auth_required("token")
    def get(self,user_id=None):
        # Default to 200 OK
        if user_id!=None:
            data=UserPatient.query.with_entities(UserPatient.user_id).filter_by(user_id=user_id).all()
            return data,200

        
    @auth_required("token")
    @marshal_with(response_fields)
    def post(self):
        args = user_parser.parse_args() 
        user_id=args.get("user_id", None)
        username=args.get("username", None)
        dob=args.get("dob", None)
        location=args.get("location", None)
        phone=args.get("phone", None)
        password=args.get("password", None)
        user = db.session.query(UserPatient).filter_by(user_id=user_id).first()   
        if user is None:
            raise BusinessValidationError(status_code=404, error_code="ERROR_U00", error_message="User not found")        
        
        add_user = UserPatient(user_id=user_id,username=username,dob=dob,location=location,phone=phone,password=password)
        db.session.add(add_user)
        db.session.commit()

        Msg={"message":"User Added"}
        return Msg,200 

    @auth_required("token")
    @marshal_with(delete_response_fields)
    def delete(self, user_id):

        exists=db.session.query(UserPatient).filter_by(user_id=user_id).first() 
        if exists is None:
            raise BusinessValidationError(status_code=400, error_code="ERROR_U03", error_message="You have not liked the post")
        db.session.delete(exists)
        db.session.commit()
        Msg={"message":"User Deleted"}
        return Msg,200 
    

    # put for appending the caretaker info 
    
'''
Request Parsers and Output Resource Fields for CaretakerAPI 
'''

caretaker_parser = reqparse.RequestParser()

caretaker_parser.add_argument("caretaker_id" )
caretaker_parser.add_argument("name")
caretaker_parser.add_argument("mobile")
caretaker_parser.add_argument("caretaker_pic")
caretaker_parser.add_argument("description")


caretaker_fields = {
    "caretaker_id" : fields.String,
    "name": fields.String,
    "mobile": fields.Integer,
    "caretaker_pic": fields.Integer,
    "description": fields.Integer    
}

delete_response_caretaker_fields = {

    "caretaker_id" : fields.String
   
}
class CaretakerAPI(Resource):

    
    @marshal_with(caretaker_fields)
    def get(self,caretaker_id=None):
        # Default to 200 OK
        if caretaker_id!=None:
            caretaker = Caretaker.query.filter_by(caretaker_id=caretaker_id).first()   
            if caretaker is None:
                raise BusinessValidationError(status_code=404, error_code="ERROR_B01", error_message="Caretaker details not found")
            else:
                return caretaker,200
        
    
    @auth_required("token")
    @marshal_with(caretaker_fields)
    def post(self):
        args = caretaker_parser.parse_args() 
        caretaker_id=args.get("caretaker_id",None)
        name=args.get("name", None)
        mobile=args.get("mobile", None)
        caretaker_pic=args.get("caretaker_pic", None)
        description=args.get("description", None)
        
        if name is None:
            raise BusinessValidationError(status_code=400, error_code="ERROR_B02", error_message="Caretaker Name is required")

        caretaker = Caretaker(caretaker_id=caretaker_id,name=name,mobile=mobile,caretaker_pic=caretaker_pic,description=description)
        caretaker_name = Caretaker.query.filter_by(name=name).first() 
        
        if caretaker_name!=None:
            raise BusinessValidationError(status_code=400, error_code="ERROR_B04", error_message="Caretaker Name already exists.. Please choose another name")
        else:
            db.session.add(caretaker)              
            db.session.commit()
        
        return caretaker,200

    @auth_required("token")
    @marshal_with(delete_response_caretaker_fields)
    def delete(self,caretaker_id=None):
        # Default to 200 OK
        if caretaker_id!=None:
            caretaker = Caretaker.query.filter_by(caretaker_id=caretaker_id).first()   
          
            if caretaker is None:
                raise BusinessValidationError(status_code=404, error_code="ERROR_B01", error_message="Caretaker not found")
            else:     
                db.session.delete(caretaker)
                db.session.commit()
        Msg={"message":"User Deleted"}
        return Msg,200      
        
         
'''
Request Parsers and Output Resource Fields forTasksAPI 
'''

tasks_parser = reqparse.RequestParser()

tasks_parser.add_argument("task_id", location='form')
tasks_parser.add_argument("user_id", location='form')
tasks_parser.add_argument("time", location='form')
tasks_parser.add_argument("emoji", location='form')
tasks_parser.add_argument("description", location='form')

task_resource_fields = {
    "task_id": fields.String,
    "user_id": fields.String,
    "time": fields.String,
    "emoji": fields.String,
    "description": fields.String,

    
}
delete_task_resource_fields = {
    "task_id": fields.String,   
}

class TasksAPI(Resource):

    @auth_required("token")
    @marshal_with(task_resource_fields)
    def get(self,user_id=None,task_id=None):
        # Default to 200 OK
        if user_id!=None or task_id!=None:
            data = Tasks.query.filter_by(user_id=user_id,task_id=task_id).first()   
            if data is None:
                raise BusinessValidationError(status_code=404, error_code="ERROR_U00", error_message="User not found")
                  
            else:
                return data,200
    
    @marshal_with(task_resource_fields)
    def post(self):
        args = tasks_parser.parse_args() 
        task_id=args.get("task_id", None)
        user_id=args.get("user_id", None)
        time=args.get("time", None)
        emoji=args.get("emoji", None)
        description=args.get("description", None)

        tasks = Tasks(task_id=task_id,user_id=user_id,time=time,emoji=emoji,description=description )
        db.session.add(tasks)
        db.session.commit()
        Msg={"message":"User created successfully"}
        return Msg,200 


    @auth_required("token")
    @marshal_with(delete_task_resource_fields)
    def delete(self,task_id=None):
        # Default to 200 OK
        if task_id!=None:
            data = Tasks.query.filter_by(task_id=task_id).first()   
            if data is None:
                raise BusinessValidationError(status_code=404, error_code="ERROR_U00", error_message="Task not found")    
            else:
                db.session.delete(data)
                db.session.commit()      
        Msg={"message":"Task deleted successfully"}
        return Msg,200 

            
'''
Request Parsers and Output Resource Fields for FollowerAPI 
'''

contact_parser = reqparse.RequestParser()

contact_parser.add_argument("acquaintances_id")
contact_parser.add_argument("name")
contact_parser.add_argument("acquaintances_pic")
contact_parser.add_argument("relation")

delete_contact_resource_fields = {
    "acquaintances_id": fields.Integer,
    "name": fields.Integer,
}
contact_resource_fields = {
    "acquaintances_id": fields.Integer,
    "name": fields.Integer,
    "acquaintances_pic": fields.Integer,
    "relation": fields.Integer,
}

class ContactsAPI(Resource):
    
    @marshal_with(contact_resource_fields)
    @auth_required("token")
    def get(self,acquaintances_id=None):
        # Default to 200 OK
        if acquaintances_id!=None:
            data = Contacts.query.filter_by(acquaintances_id=acquaintances_id).first()   
            if data is None:
                raise BusinessValidationError(status_code=404, error_code="ERROR_U00", error_message="acquaintances_id not found")
                  
            else:
                data=db.session.query(Contacts).filter_by(acquaintances_id=acquaintances_id).all()
                return data,200
        
    @auth_required("token")
    @marshal_with(contact_resource_fields)
    def post(self):
        args = contact_parser.parse_args() 
        acquaintances_id=args.get("acquaintances_id", None)
        name=args.get("name", None)
        acquaintances_pic=args.get("acquaintances_pic", None)
        relation=args.get("relation", None)

        contact = db.session.query(Contacts).filter_by(acquaintances_id=acquaintances_id).first()   
        if contact is None:
            raise BusinessValidationError(status_code=404, error_code="ERROR_U00", error_message="Contact not found")
    
        exists=db.session.query(Contacts).filter_by(acquaintances_id=acquaintances_id).first() is not None
        if exists is not None:
            raise BusinessValidationError(status_code=400, error_code="ERROR_U03", error_message="Contact already exists")
        
        contact = Contacts(acquaintances_id=acquaintances_id, name=name, acquaintances_pic=acquaintances_pic,relation=relation  )
        db.session.add(contact)
        db.session.commit()

        Msg={"message":"Contact addeed successfully"}
        return Msg,200 

    @auth_required("token")
    @marshal_with(delete_contact_resource_fields)
    def delete(self,acquaintances_id):

        contact = db.session.query(Contacts).filter_by(acquaintances_id=acquaintances_id).first()   
        if contact is None:
            raise BusinessValidationError(status_code=404, error_code="ERROR_U00", error_message="Contact not found")
        contact = Contact(acquaintances_id=acquaintances_id)
        db.session.delete(contact)
        db.session.commit()      
        Msg={"message":"Contact Deleted"}
        return Msg,200 
    