import sys
from pathlib import Path
import sqlalchemy as sa

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings

engine = sa.create_engine(settings.database_url)
inspector = sa.inspect(engine)
print('tables:', inspector.get_table_names())
if 'users' in inspector.get_table_names():
    cols = inspector.get_columns('users')
    print('users columns:')
    for c in cols:
        print(' ', c['name'], c.get('type'))
else:
    print('users table missing')
