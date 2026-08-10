from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField, 
    IntegerField, TextAreaField, SelectField, DateField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange
from app.utils.validators import validate_trek_dates

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=7, max=20)])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message="Password must be at least 6 characters long.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message="Passwords must match.")
    ])
    
    # Optional emergency context fields
    blood_group = SelectField('Blood Group', choices=[
        ('', 'Select Blood Group (Optional)'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[Optional()])
    
    medical_conditions = TextAreaField('Medical Conditions (Optional)', validators=[Optional()])
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Optional(), Length(max=100)])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[Optional(), Length(max=20)])
    
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=7, max=20)])
    blood_group = SelectField('Blood Group', choices=[
        ('', 'Select Blood Group'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[Optional()])
    medical_conditions = TextAreaField('Medical Conditions (Optional)', validators=[Optional()])
    emergency_contact_name = StringField('Emergency Contact Name', validators=[Optional(), Length(max=100)])
    emergency_contact_phone = StringField('Emergency Contact Phone', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=6, message="Password must be at least 6 characters long.")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('new_password', message="Passwords must match.")
    ])
    submit = SubmitField('Change Password')

class TrekForm(FlaskForm):
    title = StringField('Trek Title', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    altitude = IntegerField('Altitude (Meters)', validators=[
        DataRequired(), 
        NumberRange(min=0, message="Altitude must be positive.")
    ])
    difficulty_level = SelectField('Difficulty Level', choices=[
        ('Easy', 'Easy'),
        ('Moderate', 'Moderate'),
        ('Hard', 'Hard')
    ], validators=[DataRequired()])
    duration_days = IntegerField('Duration (Days)', validators=[
        DataRequired(), 
        NumberRange(min=1, message="Duration must be at least 1 day.")
    ])
    description = TextAreaField('Description', validators=[DataRequired()])
    max_slots = IntegerField('Max Capacity (Slots)', validators=[
        DataRequired(), 
        NumberRange(min=1, message="Slots must be at least 1.")
    ])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired(), validate_trek_dates])
    meeting_point = StringField('Meeting Point', validators=[DataRequired(), Length(max=150)])
    trek_status = SelectField('Trek Status', choices=[
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ], default='Open', validators=[DataRequired()])
    submit = SubmitField('Save Trek')

class StaffForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=7, max=20)])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message="Password must be at least 6 characters.")
    ])
    submit = SubmitField('Create Staff Account')

class AssignmentForm(FlaskForm):
    staff_id = SelectField('Select Staff', coerce=int, validators=[DataRequired()])
    assigned_role = SelectField('Assigned Role', choices=[
        ('Guide', 'Guide'),
        ('Medic', 'Medic')
    ], validators=[DataRequired()])
    submit = SubmitField('Assign Staff')

class BookingForm(FlaskForm):
    special_requests = TextAreaField('Special Requests / Notes (Optional)', validators=[Optional()])
    
    # Pre-filled/editable emergency info for the trek booking specifically
    blood_group = SelectField('Confirm Blood Group', choices=[
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[DataRequired()])
    medical_conditions = TextAreaField('Confirm/Update Medical Conditions', validators=[Optional()])
    emergency_contact_name = StringField('Confirm Emergency Contact Name', validators=[DataRequired(), Length(max=100)])
    emergency_contact_phone = StringField('Confirm Emergency Contact Phone', validators=[DataRequired(), Length(max=20)])
    
    submit = SubmitField('Confirm Booking')

class AttendanceForm(FlaskForm):
    attendance_status = SelectField('Attendance Status', choices=[
        ('Present', 'Present'),
        ('Absent', 'Absent')
    ], validators=[DataRequired()])
    notes = TextAreaField('Staff Notes (Optional)', validators=[Optional()])
    submit = SubmitField('Submit Attendance')

class TrekStatusForm(FlaskForm):
    trek_status = SelectField('Update Status', choices=[
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    reason = TextAreaField('Reason for Change', validators=[DataRequired(), Length(min=5, message="Please write a clear reason.")])
    submit = SubmitField('Log & Update Status')

class TrekSlotsForm(FlaskForm):
    available_slots = IntegerField('Available Slots', validators=[
        DataRequired(), 
        NumberRange(min=0, message="Slots cannot be negative.")
    ])
    submit = SubmitField('Update Slots')
