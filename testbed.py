import bcrypt

from structure import Area, Room, Exit, Player


def populate(session):
    session.add(Area(ref='default', name='Test Area'))

    room1 = Room(
        area_ref='default', tag='room1',
        name='Test Room 1',
        desc='You are in the first test room.',
    )

    room2 = Room(
        area_ref='default', tag='room2',
        name='Test Room 2',
        desc='You are in the second test room.',
    )

    room3 = Room(
        area_ref='default', tag='room3',
        name='Test Room 3',
        desc='You are in the third test room.',
    )

    session.add_all([room1, room2, room3])
    session.commit()

    exit1 = Exit(
        from_room_id=room1.id,
        direction='n',
        to_room_id=room2.id,
    )

    exit2 = Exit(
        from_room_id=room2.id,
        direction='s',
        to_room_id=room1.id,
    )

    exit3 = Exit(
        from_room_id=room1.id,
        direction='s',
        to_room_id=room3.id,
    )

    exit4 = Exit(
        from_room_id=room3.id,
        direction='n',
        to_room_id=room1.id,
    )

    session.add_all([exit1, exit2, exit3, exit4])
    session.commit()

    player1 = Player(
        name='Brandar',
        password=bcrypt.hashpw(b'test', bcrypt.gensalt()),
    )

    session.add(player1)
    session.commit()
