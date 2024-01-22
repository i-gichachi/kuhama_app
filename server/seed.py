from app import app, db
from models import User, Inventory, MovingDetail, Notification, Message
from datetime import datetime, timedelta

# Function to add initial data to the database
def seed_data():
    with app.app_context():
        
        user1 = User(
            first_name="John",
            second_name="Mwangi",
            surname="Kamau",
            username="johnkamau",
            email="johnk@gmail.com",
            phone_number="720383689",
            gender="male",
            location="Nairobi",
            date_of_birth=datetime(1990, 1, 1),
            user_type='customer'
        )
        user1.password = 'John@123'

        user2 = User(
            first_name="Ian",
            second_name="Mwaura",
            surname="Gichachi",
            username="gichachu",
            email="img@gmail.com",
            phone_number="720569305",
            gender="male",
            location="Nairobi",
            date_of_birth=datetime(1989, 1, 4),
            user_type='admin'
        )
        user2.password = 'Gichachi@123'

        inventory1 = Inventory(
            user_id=user1.id,
            item_name="Table",
            quantity=1,
            description="Wooden dining table",
            category="Furniture",
            condition="New"
        )

        moving_detail1 = MovingDetail(
            user_id=user1.id,
            from_location="Nairobi",
            to_location="Mombasa",
            from_lat=-1.2921,
            from_lon=36.8219,
            to_lat=-4.0435,
            to_lon=39.6682,
            home_size="two bedroom",
            moving_date=datetime.now() + timedelta(days=10),
            price=15000.00,
            packing_service=True,
            additional_details="Fragile items included",
            status="pending"
        )

        notification1 = Notification(
            user_id=user1.id,
            message="Welcome to Kukuhamisha!",
            read=False,
            created_at=datetime.utcnow()
        )

        message1 = Message(
            sender_id=user1.id,  
            receiver_id=user2.id, 
            content="Hello, I need assistance with my moving details",
            created_at=datetime.utcnow()
        )

        # Add objects to session and commit to database
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(inventory1)
        db.session.add(moving_detail1)
        db.session.add(notification1)
        db.session.add(message1)
        db.session.commit()

# Run the seeding function
if __name__ == "__main__":
    seed_data()
