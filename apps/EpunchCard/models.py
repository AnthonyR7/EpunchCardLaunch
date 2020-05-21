from __future__ import unicode_literals
from django.db import models
import jsonfield
from django.contrib.auth.hashers import check_password
import re
from datetime import date, datetime
from time import strptime
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MaxValueValidator, MinValueValidator
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
class UserManager(models.Manager):
    def reg_validator(self, postData):
        
        errors = []
        if len(postData['name']) <1:
            errors.append('Name must be not empty!')
        if len(postData['name']) > 1:
            if (postData['name'].replace(" ","").isalpha()) != True:
                errors.append("No numbers in your name please!")

        if len(postData['title']) < 1:
            errors.append( "Title is needed.")

        if len(postData['password']) < 8:
            errors.append( "Pass word must be at least 8 characters.")

        if postData['password'] != postData['confirm_password']:
            errors.append("Pass words do NOT match!")

        identical = StaffMember.objects.filter(email = postData['email'])
        if identical:
            errors.append("Sorry this email name is already taken! Try a different one.")

        if len(postData['email']) > 1:
            if not EMAIL_REGEX.match(postData['email']):
                errors.append("Invalid Email Address!")

        return errors
    
    def log_validator(self, postData):
        missing = []
        if len(postData["confirm_email"]) < 1:
            missing.append("Email is needed!")
        if len(postData["login_password"]) < 1:
            missing.append("Login Password is needed!")

        else:
            try:
                confirm_email = postData["confirm_email"]
                confirm_password = postData["login_password"]
                searched_user = StaffMember.objects.get( email = confirm_email)
                if not check_password(confirm_password, searched_user.password):
                    missing.append("Incorrect password")
            except ObjectDoesNotExist:
                missing.append("Account not in database.")
        return missing
# to keep track of which admin creates a staffmember
class StaffMember(models.Model):
    admin_id = models.CharField(max_length = 2000, default=0)
    name = models.CharField(max_length = 255)
    title = models.CharField(max_length = 255)
    email = models.CharField(max_length = 255)
    password = models.CharField(max_length = 255)
    total = models.DecimalField(max_digits=4000, decimal_places=1, default=0)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()
class PunchCard(models.Model):
    clock = jsonfield.JSONField(default=list)
    employee = models.ForeignKey(StaffMember, on_delete=models.PROTECT)

