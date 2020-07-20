from sqlalchemy import Column, Integer, String, Sequence, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import connector

class User(connector.Manager.Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(12))
    username = Column(String(12))
    contact = Column(Integer)

class Pets(connector.Manager.Base):
    __tablename__ = 'pets'
    id = Column(Integer, Sequence('pet_id_seq'), primary_key=True)
    id_user = Column(Integer,ForeignKey('users.id'))
    type = Column(String(20))
    breed = Column(String(20))
    place = Column(String(100))
    info = Column(String(200))
    age = Column(Integer)
    color = Column(String(20))
    date = Column(DateTime(timezone=True))


