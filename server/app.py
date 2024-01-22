from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, DateField, IntegerField, DateTimeField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError, NumberRange
from models import db, User, Inventory, MovingDetail, Notification, Message
import datetime
from datetime import timedelta
import math

app = Flask(__name__)

app.config['SECRET_KEY'] = b'\x11O\xf0d<\xac,\x05\xd6\x8c\xc6%\x8d\xa2\x1d\x17\xbf\x93dw\xa9H/\x96'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gichachi:9614@localhost/moverdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = b'\x11O\xf0d<\xac,\x05\xd6\x8c\xc6%\x8d\xa2\x1d\x17\xbf\x93dw\xa9H/\x96'

jwt = JWTManager(app)
CORS(app)
api = Api(app)
db.init_app(app)
migrate = Migrate(app, db)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def calculate_price(distance, home_size, packing_service):
    base_price_per_km = 500  # 500 currency units per km
    size_factor = {
        "bedsitter": 1,
        "one bedroom": 1.5,
        "studio": 1.2,
        "two bedroom": 2
    }
    packing_service_fee = 200 if packing_service else 0

    price = distance * base_price_per_km * size_factor[home_size.lower()] + packing_service_fee
    return price


class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    second_name = StringField('Second Name')
    surname = StringField('Surname', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*]).{8,}$', 
               message="Password should have at least one lowercase, one uppercase, one number, and one special character.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    accept_terms = BooleanField('I accept the Terms and Conditions', validators=[DataRequired()])

    def validate_date_of_birth(form, field):
        if field.data:
            today = datetime.date.today()
            age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))
            if age < 18:
                raise ValidationError('You must be at least 18 years old to register.')
            
    def validate_phone_number(form, field):
        if field.data:
            if not field.data.isdigit() or len(field.data) != 9:
                raise ValidationError('Phone number must be exactly 9 digits.')

class LoginForm(FlaskForm):
    login = StringField('Username/Email/Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class InventoryForm(FlaskForm):
    item_name = StringField('Item Name', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    description = StringField('Description', validators=[DataRequired()]) 
    category = StringField('Category', validators=[DataRequired()]) 
    condition = StringField('Condition', validators=[DataRequired()])

class MovingDetailForm(FlaskForm):
    from_location = StringField('From Location', validators=[DataRequired()])
    from_lat = FloatField('From Latitude', validators=[DataRequired()])
    from_lon = FloatField('From Longitude', validators=[DataRequired()])
    to_location = StringField('To Location', validators=[DataRequired()])
    to_lat = FloatField('To Latitude', validators=[DataRequired()])
    to_lon = FloatField('To Longitude', validators=[DataRequired()])
    home_size = SelectField('Home Size', choices=[
        ('bedsitter', 'Bedsitter'),
        ('one bedroom', 'One Bedroom'),
        ('studio', 'Studio'),
        ('two bedroom', 'Two Bedroom')
    ], validators=[DataRequired()])
    moving_date = DateTimeField('Moving Date', validators=[DataRequired()], format='%Y-%m-%d %H:%M:%S')
    price = FloatField('Price', validators=[DataRequired()])
    packing_service = BooleanField('Packing Service')
    additional_details = StringField('Additional Details')

    @staticmethod
    def validate_moving_date(form, field):
        if field.data:
            min_date = datetime.now() + timedelta(days=7)
            if field.data < datetime.now():
                raise ValidationError('Moving date cannot be in the past.')
            elif field.data < min_date:
                raise ValidationError('Moving date should be at least 7 days from today.')

            
class HomePageResource(Resource):
    def get(self):
        return {
            'message': 'Welcome to Kukuhamisha App'
        }

api.add_resource(HomePageResource, '/')

class LoginResource(Resource):
    def post(self):
        data = request.get_json()

        user = User.query.filter(
            (User.username == data['login']) |
            (User.email == data['login']) |
            (User.phone_number == data['login'])
        ).first()

        if user and check_password_hash(user.password_hash, data['password']):
            access_token = create_access_token(identity=user.id)
            return {'access_token': access_token}, 200
        else:
            return {'message': 'Invalid username, email, phone number or password'}, 401

api.add_resource(LoginResource, '/login')

class LogoutResource(Resource):
    @jwt_required()
    def post(self):
        
        return {'message': 'User logged out successfully'}, 200

api.add_resource(LogoutResource, '/logout')

class SignupResource(Resource):
    def post(self):
        data = request.get_json()

        # Basic validation
        if not all(key in data for key in ['first_name', 'surname', 'username', 'email', 'phone_number', 'gender', 'date_of_birth', 'password']):
            return {'message': 'Missing required fields'}, 400

        # Convert date_of_birth to datetime object
        try:
            date_of_birth = datetime.datetime.strptime(data['date_of_birth'], '%Y-%m-%d')
            # Check if user is at least 18 years old
            today = datetime.date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            if age < 18:
                return {'message': 'You must be at least 18 years old to register.'}, 400
        except ValueError:
            return {'message': 'Invalid date format'}, 400

        # Create a new user
        new_user = User(
            first_name=data['first_name'],
            second_name=data.get('second_name', ''),  
            surname=data['surname'],
            username=data['username'],
            email=data['email'],
            phone_number=data['phone_number'],
            gender=data['gender'],
            location=data.get('location', ''),
            date_of_birth=date_of_birth,
            user_type='customer'
        )
        new_user.password_hash = generate_password_hash(data['password'])

        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

        # Notify admins
        admin_users = User.query.filter_by(user_type='admin').all()
        for admin in admin_users:
            new_notification = Notification(user_id=admin.id, message="New user signed up: " + new_user.username)
            db.session.add(new_notification)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': str(e)}, 500

        return {'message': 'User registered successfully'}, 201

api.add_resource(SignupResource, '/signup')

class UserResource(Resource):
    @jwt_required()
    def get(self):

        current_user_id = get_jwt_identity()

        user = User.query.get(current_user_id)

        if user:

            return jsonify(user.to_dict())
        else:
            return {'message': 'User not found'}, 404

api.add_resource(UserResource, '/user/info')

class UpdateUserResource(Resource):
    @jwt_required()
    def put(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if user:
            data = request.get_json()

            if 'email' in data:
                if "@" not in data['email']:
                    return {'message': 'Invalid email format'}, 400
                user.email = data['email']
            if 'phone_number' in data:
                if not data['phone_number'].isdigit() or len(data['phone_number']) != 9:
                    return {'message': 'Phone number must be exactly 9 digits'}, 400
                user.phone_number = data['phone_number']
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'second_name' in data:
                user.second_name = data['second_name']
            if 'surname' in data:
                user.surname = data['surname']
            if 'gender' in data:
                user.gender = data['gender']
            if 'location' in data:
                user.location = data['location']
            if 'date_of_birth' in data:
                user.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d')


            db.session.commit()
            return {'message': 'User information updated successfully'}, 200
        else:
            return {'message': 'User not found'}, 404

api.add_resource(UpdateUserResource, '/user/update')

class InventoryResource(Resource):
    @jwt_required()
    def post(self):
        current_user_info = get_jwt_identity()
        current_user_id = current_user_info['id']
        current_user = User.query.get(current_user_info)

        if current_user.user_type != 'customer':
            return {'message': 'Access denied'}, 403
        
        form = InventoryForm(request.form)

        if form.validate():
            new_item = Inventory(
                user_id=current_user_id,
                item_name=form.item_name.data,
                quantity=form.quantity.data,
                description=form.description.data,
                category=form.category.data,
                condition=form.condition.data
            )
            db.session.add(new_item)
            db.session.commit()

            return {'message': 'Item added to inventory successfully'}, 201
        else:
            return {'message': 'Invalid input'}, 400

api.add_resource(InventoryResource, '/inventory/add')

class InventoryListResource(Resource):
    @jwt_required()
    def get(self):
        current_user_info = get_jwt_identity()
        current_user_id = current_user_info['id']
        current_user = User.query.get(current_user_info)

        if current_user.user_type != 'customer':
            return {'message': 'Access denied'}, 403
        
        search_keyword = request.args.get('keyword', type=str)
        filter_category = request.args.get('category', type=str)
        filter_condition = request.args.get('condition', type=str)

        query = Inventory.query.filter_by(user_id=current_user_id)

        if search_keyword:
            query = query.filter(Inventory.item_name.ilike(f'%{search_keyword}%') | 
                                  Inventory.description.ilike(f'%{search_keyword}%'))
        if filter_category:
            query = query.filter(Inventory.category.ilike(f'%{filter_category}%'))
        if filter_condition:
            query = query.filter(Inventory.condition.ilike(f'%{filter_condition}%'))

        user_inventory = query.all()

        if user_inventory:
            inventory_list = [item.to_dict() for item in user_inventory]
            return jsonify(inventory_list)
        else:
            return {'message': 'No inventory items found'}, 404

api.add_resource(InventoryListResource, '/inventory')

class InventoryUpdateResource(Resource):
    @jwt_required()
    def put(self, item_id):
        current_user_info = get_jwt_identity()
        current_user_id = current_user_info['id']
        current_user = User.query.get(current_user_info)

        if current_user.user_type != 'customer':
            return {'message': 'Access denied'}, 403
        
        item = Inventory.query.filter_by(id=item_id, user_id=current_user_id).first()

        if not item:
            return {'message': 'Item not found'}, 404

        data = request.get_json()
        if 'item_name' in data:
            item.item_name = data['item_name']
        if 'quantity' in data:
            item.quantity = data['quantity']
        if 'description' in data:
            item.description = data['description']
        if 'category' in data:
            item.category = data['category']
        if 'condition' in data:
            item.condition = data['condition']

        db.session.commit()
        return {'message': 'Inventory item updated successfully'}, 200

api.add_resource(InventoryUpdateResource, '/inventory/update/<int:item_id>')

class InventoryDeleteResource(Resource):
    @jwt_required()
    def delete(self, item_id):
        current_user_info = get_jwt_identity()
        current_user_id = current_user_info['id']
        current_user = User.query.get(current_user_info)

        if current_user.user_type != 'customer':
            return {'message': 'Access denied'}, 403
        
        item = Inventory.query.filter_by(id=item_id, user_id=current_user_id).first()

        if not item:
            return {'message': 'Item not found'}, 404

        db.session.delete(item)
        db.session.commit()
        return {'message': 'Inventory item deleted successfully'}, 200

api.add_resource(InventoryDeleteResource, '/inventory/delete/<int:item_id>')

class MovingDetailResource(Resource):
    @jwt_required()
    def post(self):
        current_user_info = get_jwt_identity()
        current_user_id = current_user_info['id']
        current_user = User.query.get(current_user_info)

        if current_user.user_type != 'customer':
            return {'message': 'Access denied'}, 403

        form = MovingDetailForm(request.form)

        if form.validate():
            # Calculate the distance
            distance = haversine_distance(
                form.from_lat.data, form.from_lon.data, form.to_lat.data, form.to_lon.data)

            # Calculate price based on distance, home size, and whether packing service is included
            price = calculate_price(
                distance, form.home_size.data, form.packing_service.data)

            new_moving_detail = MovingDetail(
                user_id=current_user_id,
                from_location=form.from_location.data,
                to_location=form.to_location.data,
                home_size=form.home_size.data.lower(), # using lower case for consistency
                moving_date=form.moving_date.data,
                price=price,
                status='pending',
                additional_details=form.additional_details.data
            )
            db.session.add(new_moving_detail)
            db.session.commit()

            return {'message': 'Moving details added successfully'}, 201
        else:
            return form.errors, 400

api.add_resource(MovingDetailResource, '/moving/add')

class MovingDetailListResource(Resource):
    @jwt_required()
    def get(self):
        current_user_info = get_jwt_identity()
        current_user_id = current_user_info['id']
        current_user = User.query.get(current_user_info)

        if current_user.user_type != 'customer':
            return {'message': 'Access denied'}, 403
        
        user_moving_details = MovingDetail.query.filter_by(user_id=current_user_id).all()

        if user_moving_details:
            details_list = [detail.to_dict() for detail in user_moving_details]
            return jsonify(details_list)
        else:
            return {'message': 'No moving details found'}, 404

api.add_resource(MovingDetailListResource, '/moving')

class MovingDetailUpdateResource(Resource):
    @jwt_required()
    def put(self, detail_id):
        current_user_info = get_jwt_identity()
        current_user_id = current_user_info['id']
        current_user = User.query.get(current_user_info)

        if current_user.user_type != 'customer':
            return {'message': 'Access denied'}, 403
        
        moving_detail = MovingDetail.query.filter_by(id=detail_id, user_id=current_user_id).first()

        if not moving_detail:
            return {'message': 'Moving detail not found'}, 404

        data = request.get_json()
        if 'from_location' in data:
            moving_detail.from_location = data['from_location']
        if 'to_location' in data:
            moving_detail.to_location = data['to_location']
        if 'home_size' in data:
            moving_detail.home_size = data['home_size']
        if 'moving_date' in data:
            # Ensure that moving_date is in the correct format
            try:
                moving_detail.moving_date = datetime.strptime(data['moving_date'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return {'message': 'Invalid moving date format'}, 400
        if 'price' in data:
            moving_detail.price = data['price']
        if 'additional_details' in data:
            moving_detail.additional_details = data['additional_details']

        db.session.commit()
        return {'message': 'Moving detail updated successfully'}, 200

api.add_resource(MovingDetailUpdateResource, '/moving/update/<int:detail_id>')

class MovingDetailDeleteResource(Resource):
    @jwt_required()
    def delete(self, detail_id):
        current_user_info = get_jwt_identity()
        current_user_id = current_user_info['id']
        current_user = User.query.get(current_user_info)

        if current_user.user_type != 'customer':
            return {'message': 'Access denied'}, 403
        
        moving_detail = MovingDetail.query.filter_by(id=detail_id, user_id=current_user_id).first()

        if not moving_detail:
            return {'message': 'Moving detail not found'}, 404

        db.session.delete(moving_detail)
        db.session.commit()
        return {'message': 'Moving detail deleted successfully'}, 200

api.add_resource(MovingDetailDeleteResource, '/moving/delete/<int:detail_id>')

class AdminCustomerListResource(Resource):
    @jwt_required()
    def get(self):
        current_user_info = get_jwt_identity()
        current_user = User.query.get(current_user_info['id'])

        if current_user.user_type != 'admin':
            return {'message': 'Access denied'}, 403

        customers = User.query.filter_by(user_type='customer').all()
        return jsonify([customer.to_dict() for customer in customers])

api.add_resource(AdminCustomerListResource, '/admin/customers')

class AdminCustomerInventoryResource(Resource):
    @jwt_required()
    def get(self, user_id):
        current_user_info = get_jwt_identity()
        current_user = User.query.get(current_user_info['id'])

        if current_user.user_type != 'admin':
            return {'message': 'Access denied'}, 403

        inventory = Inventory.query.filter_by(user_id=user_id).all()
        return jsonify([item.to_dict() for item in inventory])

api.add_resource(AdminCustomerInventoryResource, '/admin/customer/<int:user_id>/inventory')

class AdminDeleteCustomerResource(Resource):
    @jwt_required()
    def delete(self, user_id):
        current_user_info = get_jwt_identity()
        current_user = User.query.get(current_user_info['id'])

        if current_user.user_type != 'admin':
            return {'message': 'Access denied'}, 403

        user_to_delete = User.query.get(user_id)
        if not user_to_delete or user_to_delete.user_type != 'customer':
            return {'message': 'User not found or not a customer'}, 404

        db.session.delete(user_to_delete)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200

api.add_resource(AdminDeleteCustomerResource, '/admin/delete/customer/<int:user_id>')

class AdminUpdateMovingStatusResource(Resource):
    @jwt_required()
    def put(self, moving_detail_id):
        current_user_info = get_jwt_identity()
        current_user = User.query.get(current_user_info['id'])

        if current_user.user_type != 'admin':
            return {'message': 'Access denied'}, 403

        moving_detail = MovingDetail.query.get(moving_detail_id)
        if not moving_detail:
            return {'message': 'Moving detail not found'}, 404

        data = request.get_json()
        new_status = data.get('status')
        if new_status not in ['pending', 'approved', 'rejected', 'completed']:
            return {'message': 'Invalid status'}, 400

        # Update the status
        moving_detail.status = new_status

        # Send a notification to the customer
        customer_notification_message = ''
        if new_status == 'approved':
            customer_notification_message = 'Your moving request has been approved. Please start preparing.'
        elif new_status == 'rejected':
            customer_notification_message = 'Your moving request has been rejected. Please consider changing the date or details.'

        if customer_notification_message:
            new_notification = Notification(user_id=moving_detail.user_id, message=customer_notification_message)
            db.session.add(new_notification)

        db.session.commit()
        return {'message': 'Moving status updated successfully'}, 200

api.add_resource(AdminUpdateMovingStatusResource, '/admin/moving/update-status/<int:moving_detail_id>')

class AdminNotificationsResource(Resource):
    @jwt_required()
    def get(self):
        current_user_info = get_jwt_identity()
        current_user = User.query.get(current_user_info['id'])

        if current_user.user_type != 'admin':
            return {'message': 'Access denied'}, 403

        notifications = Notification.query.filter_by(user_id=current_user.id).all()
        return jsonify([notification.to_dict() for notification in notifications])

api.add_resource(AdminNotificationsResource, '/admin/notifications')

class UserNotificationsResource(Resource):
    @jwt_required()
    def get(self):
        current_user_info = get_jwt_identity()
        current_user = User.query.get(current_user_info['id'])

        if current_user.user_type != 'customer':
            return {'message': 'Access denied'}, 403

        notifications = Notification.query.filter_by(user_id=current_user.id).all()
        return jsonify([notification.to_dict() for notification in notifications])

api.add_resource(UserNotificationsResource, '/user/notifications')

class SendMessageResource(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()

        if 'content' not in data:
            return {'message': 'No message content provided'}, 400

        admin_user = User.query.filter_by(user_type='admin').first()
        if not admin_user:
            return {'message': 'Admin user not found'}, 404

        new_message = Message(sender_id=user_id, receiver_id=admin_user.id, content=data['content'])
        db.session.add(new_message)
        db.session.commit()
        return {'message': 'Message sent successfully'}, 201

api.add_resource(SendMessageResource, '/send-message')

class AdminMessagesResource(Resource):
    @jwt_required()
    def get(self):
        current_user_info = get_jwt_identity()
        current_user = User.query.get(current_user_info)

        if current_user.user_type != 'admin':
            return {'message': 'Access denied'}, 403

        messages = Message.query.filter_by(receiver_id=current_user.id).all()
        return jsonify([message.to_dict() for message in messages])

api.add_resource(AdminMessagesResource, '/admin/messages')

if __name__ == '__main__':
    app.run(port=5555, debug=True)