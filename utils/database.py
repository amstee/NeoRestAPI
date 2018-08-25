from config.database import db
from models.User import User
from models.Conversation import Conversation
from models.Circle import Circle
from models.Device import Device
from models.Message import Message
from models.UserToConversation import UserToConversation
from models.UserToCircle import UserToCircle


def init_default_content(p1, p2):
    user = db.session.query(User).filter(User.email == "user1.beta@test.com").first()
    user2 = db.session.query(User).filter(User.email == "user2.beta@test.cm").first()
    if user is None and user2 is None:
        user = User(email="user1.beta@test.com", password=p1, first_name="user1",
                    last_name="beta", birthday="2019-09-05")
        user2 = User(email="user2.beta@test.com", password=p2, first_name="user2",
                     last_name="beta", birthday="2019-09-05")
        circle = Circle("Cercle Beta 1")
        UserToCircle(user=user, circle=circle, privilege="ADMIN")
        UserToCircle(user=user2, circle=circle)
        device = db.session.query(Device).filter(Device.username == "device1").first()
        if device is None:
            device = Device(name="Device beta 1")
            device.circle = circle
            device.username = "device1"
            device.set_password("test")
            device.activate(device.key)
        if len(circle.conversations) == 0:
            conversation = Conversation(device_access=True, name="Conversation avec device", circle=circle)
            conversation2 = Conversation(device_access=False, name="Conversation sans device", circle=circle)
            if len(user.conversation_links) == 0:
                cl1 = UserToConversation(privilege="ADMIN", user=user, conversation=conversation)
                cl2 = UserToConversation(user=user2, conversation=conversation)
                Message(content="Message conversation avec device from user1", link=cl1, conversation=conversation)
                Message(content="Message conversation avec device from user2", link=cl2, conversation=conversation)
                message3 = Message(content="Message conversation avec device from device",
                                   is_user=False, conversation=conversation)
                message3.device = device
            if len(user2.conversation_links) == 0:
                cl3 = UserToConversation(privilege="ADMIN", user=user, conversation=conversation2)
                cl4 = UserToConversation(user=user2, conversation=conversation2)
                Message(content="Message conversation sans device from user1", link=cl3, conversation=conversation2)
                Message(content="Message conversation sans device from user2", link=cl4, conversation=conversation2)
        db.session.commit()
