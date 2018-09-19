from config.database import db
from models.User import User
from models.Conversation import Conversation
from models.Circle import Circle
from models.Device import Device
from models.Message import Message
from models.UserToConversation import UserToConversation
from models.UserToCircle import UserToCircle


def get_user(email):
    return db.session.query(User).filter(User.email == email).first()


def get_circle(circle_id):
    return db.session.query(Circle).filter(Circle.id == circle_id).first()


def get_conversation(conversation_id):
    return db.session.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_device(username):
    return db.session.query(Device).filter(Device.username == username).first()


def get_message(message_id):
    return db.session.query(Message).filter(Message.id == message_id).first()


def clean_default_content():
    user = db.session.query(User).filter(User.email == "user1.beta@test.com").first()
    user2 = db.session.query(User).filter(User.email == "user2.beta@test.cm").first()
    device = db.session.query(Device).filter(Device.username == "device1").first()
    if device:
        circle = device.circle
        if circle:
            db.session.delete(circle)
    if device:
        db.session.delete(device)
    if user:
        db.session.delete(user)
    if user2:
        db.session.delete(user2)


def init_default_content(p1, p2):
    user = db.session.query(User).filter(User.email == "user1.beta@test.com").first()
    user2 = db.session.query(User).filter(User.email == "user2.beta@test.cm").first()
    if user is None and user2 is None:
        user = User(email="user1.beta@test.com", password=p1, first_name="user1",
                    last_name="beta", birthday="2019-09-05")
        user2 = User(email="user2.beta@test.com", password=p2, first_name="user2",
                     last_name="beta", birthday="2019-09-05")
        circle = Circle("Cercle Beta 1")
        db.session.commit()
        UserToCircle(user=user, circle=circle, privilege="ADMIN")
        UserToCircle(user=user2, circle=circle)
        db.session.commit()
        device = db.session.query(Device).filter(Device.username == "device1").first()
        if device is None:
            device = Device(name="Device beta 1")
            device.circle = circle
            device.username = "device1"
            device.set_password("test")
            device.activate(device.key)
            db.session.commit()
        if len(circle.conversations) == 0:
            conversation = Conversation(device_access=True, name="Conversation avec device", circle=circle)
            conversation2 = Conversation(device_access=False, name="Conversation sans device", circle=circle)
            db.session.commit()
            if len(user.conversation_links) == 0:
                cl1 = UserToConversation(privilege="ADMIN", user=user, conversation=conversation)
                cl2 = UserToConversation(user=user2, conversation=conversation)
                db.session.commit()
                Message(content="Message conversation avec device from user1", link=cl1, conversation=conversation)
                Message(content="Message conversation avec device from user2", link=cl2, conversation=conversation)
                message3 = Message(content="Message conversation avec device from device",
                                   is_user=False, conversation=conversation)
                message3.device = device
                db.session.commit()
            if len(user2.conversation_links) == 0:
                cl3 = UserToConversation(privilege="ADMIN", user=user, conversation=conversation2)
                cl4 = UserToConversation(user=user2, conversation=conversation2)
                db.session.commit()
                Message(content="Message conversation sans device from user1", link=cl3, conversation=conversation2)
                Message(content="Message conversation sans device from user2", link=cl4, conversation=conversation2)
        db.session.commit()
