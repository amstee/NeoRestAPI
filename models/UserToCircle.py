from config.database import db
from dateutil import parser as DateParser
import datetime


class UserToCircle(db.Model):
    __tablename__ = "user_to_circle"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    circle_id = db.Column(db.Integer, db.ForeignKey("circles.id"))
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    privilege = db.Column(db.String(10))

    user = db.relationship("User", back_populates="circle_link")
    circle = db.relationship("Circle", back_populates="user_link")

    def __repr__(self):
        return "<UserToCircle(id='%d' user_id='%d' circle_id='%d' created='%s' updated='%s' privilege='%s')>"\
               % (self.id, self.user_id, self.circle_id, str(self.created), str(self.updated), self.privilege)

    def __init__(self, created=datetime.datetime.now(), updated=datetime.datetime.now(), privilege="DEFAULT",
                 user=None, circle=None):
        if created is not None:
            if type(created) is str:
                self.created = DateParser.parse(created)
            else:
                self.created = created
        if updated is not None:
            if type(updated) is str:
                self.updated = DateParser.parse(updated)
            else:
                self.updated = updated
        if privilege is not None:
            self.privilege = privilege
        if user is not None:
            self.user = user
        if circle is not None:
            self.circle = circle
        db.session.add(self)

    def update_content(self, created=None, updated=datetime.datetime.now(), privilege=None):
        if created is not None:
            if type(created) is str:
                self.created = DateParser.parse(created)
            else:
                self.created = created
        if updated is not None:
            if type(updated) is str:
                self.updated = DateParser.parse(updated)
            else:
                self.updated = updated
        if privilege is not None and privilege != "":
            self.privilege = privilege
        db.session.commit()

    def get_content(self, user=True):
        if user:
            return {
                "id": self.id,
                "user": self.user_id,
                "circle": self.circle.get_simple_content(),
                "created": self.created,
                "updated": self.updated,
                "privilege": self.privilege
            }
        else:
            return {
                "id": self.id,
                "user": self.user.get_simple_content(),
                "circle": self.circle_id,
                "created": self.created,
                "updated": self.updated,
                "privilege": self.privilege
            }
