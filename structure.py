import uuid

from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, String, Numeric, Boolean


Base = declarative_base()


def generate_id():
    return str(uuid.uuid4())


class Tagged(object):
    id = Column(String, primary_key=True, default=generate_id)

    @declared_attr
    def area_ref(cls):
        return Column(String, ForeignKey('areas.ref'))

    tag = Column(String)


class Area(Base):
    __tablename__ = 'areas'

    ref = Column(String, primary_key=True)

    name = Column(String)

    rooms = relationship('Room', backref='area')
    master_items = relationship('MasterItem', backref='area')
    placements = relationship('Placement', backref='area')
    contents_placements = relationship('ContentsPlacement', backref='area')
    doors = relationship('Door', backref='area')


class Room(Tagged, Base):
    __tablename__ = 'rooms'

    name = Column(String)
    desc = Column(String)

    items = relationship('Item', backref='room')


class MasterItem(Tagged, Base):
    __tablename__ = 'master_items'

    name = Column(String)
    desc = Column(String)
    weight = Column(Numeric(precision=7, scale=1))
    capacity = Column(Numeric(precision=7, scale=1))


class Item(Base):
    __tablename__ = 'items'

    id = Column(String, primary_key=True, default=generate_id)

    master_item_id = Column(String, ForeignKey('master_items.id'))

    name = Column(String)
    desc = Column(String)
    weight = Column(Numeric(precision=7, scale=1))
    capacity = Column(Numeric(precision=7, scale=1))

    owner_id = Column(String, ForeignKey('players.id'))
    container_id = Column(String, ForeignKey('items.id'))
    room_id = Column(String, ForeignKey('rooms.id'))

    master_item = relationship('MasterItem', backref='instances')
    owner = relationship('Player', backref='items')
    contents = relationship('Item')
    container = relationship('Item', remote_side=[id])


class Placement(Tagged, Base):
    __tablename__ = 'placements'

    master_item_id = Column(String, ForeignKey('master_items.id'))
    room_id = Column(String, ForeignKey('rooms.id'))

    item_id = Column(String, ForeignKey('items.id'))

    master_item = relationship('MasterItem', backref='placements')
    room = relationship('Room', backref='placements')
    item = relationship('Item')


class ContentsPlacement(Tagged, Base):
    __tablename__ = 'contents_placements'

    parent_id = Column(String, ForeignKey('placements.id'))
    master_item_id = Column(String, ForeignKey('master_items.id'))

    item_id = Column(String, ForeignKey('items.id'))

    parent = relationship('Placement', backref='contents_placements')
    master_item = relationship('MasterItem', backref='contents_placements')
    item = relationship('Item')


class Door(Tagged, Base):
    __tablename__ = 'doors'

    desc = Column(String)
    default_closed = Column(Boolean)
    default_locked = Column(Boolean)

    closed = Column(Boolean)
    locked = Column(Boolean)


class Key(Base):
    __tablename__ = 'key_maps'

    door_id = Column(String, ForeignKey('doors.id'), primary_key=True)
    key_item_id = Column(String, ForeignKey('master_items.id'), primary_key=True)

    door = relationship('Door', backref='keys')
    key_item = relationship('MasterItem')


class Exit(Base):
    __tablename__ = 'exit_maps'

    from_room_id = Column(String, ForeignKey('rooms.id'), primary_key=True)
    direction = Column(String, primary_key=True)
    to_room_id = Column(String, ForeignKey('rooms.id'))
    door_id = Column(String, ForeignKey('doors.id'))

    from_room = relationship('Room', primaryjoin='Exit.from_room_id==Room.id', backref='exits')
    to_room = relationship('Room', primaryjoin='Exit.to_room_id==Room.id')
    door = relationship('Door', backref='exits')


class MasterNPC(Tagged, Base):
    __tablename__ = 'master_npcs'


class Player(Base):
    __tablename__ = 'players'

    id = Column(String, primary_key=True, default=generate_id)

    master_npc_id = Column(String, ForeignKey('master_npcs.id'))

    socket_id = Column(String, unique=True)

    master_npc = relationship('MasterNPC', backref='instances')

    name = Column(String, unique=True)
    password = Column(String)
