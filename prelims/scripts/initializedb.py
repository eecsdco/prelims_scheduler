import os
import sys
import transaction

from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    Faculty,
    TimeSlot,
    Event,
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    for fac in open('prelims/scripts/fac_uniqs'):
        fac = fac.strip()
        if len(fac) == 0 or fac[0] == '#':
            continue
        try:
            DBSession.query(Faculty).filter_by(uniqname=fac).one()
        except NoResultFound:
            f = Faculty(uniqname=fac)
            DBSession.add(f)
    transaction.commit()
