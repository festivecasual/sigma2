import sqlalchemy
from sqlalchemy.orm import sessionmaker

import structure
import testbed
import recurring
from server import Server


if __name__ == '__main__':
    engine = sqlalchemy.create_engine('sqlite:///:memory:')
    structure.Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    testbed.populate(session)

    # Clear any remnant attached Player sockets
    for p in session.query(structure.Player).filter(structure.Player.socket_id != None):
        p.socket_id = None
    session.commit()

    server = Server(session)

    recurring.kickstart_tasks(server)

    try:
        server.events.run()
    except (KeyboardInterrupt, SystemExit):
        print('SHUTTING DOWN')
        raise SystemExit
