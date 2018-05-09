from config.database import db_session
from models.User import User
from models.Conversation import Conversation
from models.Circle import Circle
from models.Device import Device
from models.Message import Message
from models.UserToConversation import UserToConversation
from models.UserToCircle import UserToCircle

def initDefaultContent():
    user = db_session.query(User).filter(User.email=="user1.beta@test.com").first()
    user2 = db_session.query(User).filter(User.email=="user2.beta@test.cm").first()
    if user is None and user2 is None:
        user = User(email="user1.beta@test.com", password="test", first_name="user1",
                    last_name="beta", birthday="2019-09-05")
        user2 = User(email="user2.beta@test.com", password="test", first_name="user2",
                    last_name="beta", birthday="2019-09-05")
        circle = Circle("Cercle Beta 1")
        if user.circleLink is None:
            link = UserToCircle(user=user, circle=circle, privilege="ADMIN")
        else:
            link = user.circleLink
        if user2.circleLink is None:
            link2 = UserToCircle(user=user2, circle=circle)
        else:
            link2 = user2.circleLink
        device = db_session.query(Device).filter(Device.username=="device1").first()
        if device is None:
            device = Device(name="Device beta 1")
            device.circle = circle
            device.username = "device1"
            device.password = "test"
            device.activate(device.key)
        if len(circle.conversations) == 0:
            conversation = Conversation(device_access=True, name="Conversation avec device", circle=circle)
            conversation2 = Conversation(device_access=False, name="Conversation sans device", circle=circle)
            if len(user.conversationLinks) == 0:
                cl1 = UserToConversation(privilege="ADMIN", user=user, conversation=conversation)
                cl2 = UserToConversation(user=user2, conversation=conversation)
                message1 = Message(content="Message conversation avec device from user1", link=cl1, conversation=conversation)
                message2 = Message(content="Message conversation avec device from user2", link=cl2, conversation=conversation)
                message3 = Message(content="Message conversation avec device from device", isUser=False, conversation=conversation)
                message3.device = device
            if len(user2.conversationLinks) == 0:
                cl3 = UserToConversation(privilege="ADMIN", user=user, conversation=conversation2)
                cl4 = UserToConversation(user=user2, conversation=conversation2)
                message4 = Message(content="Message conversation sans device from user1", link=cl3, conversation=conversation2)
                message5 = Message(content="Message conversation sans device from user2", link=cl4, conversation=conversation2)
        db_session.commit()
