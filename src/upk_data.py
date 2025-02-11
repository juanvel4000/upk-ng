import sqlite3, json, os # sqlite: db and stuff, json: manifest
def convertFts(f): # convert file to str
    if os.path.isfile(f):
        return open(f, 'r').read()
    else:
        raise FileNotFoundError(f"{f} not found")
def getManifest(string): # usage: getManifest(convertFts(file))
    try:
        obj = json.loads(string)
        for crit in ["name", "maintainer", "version", "summary" ]: # check for critical stuff
            if not crit in obj:
                raise KeyError(f"{crit} not found in manifest")
        if not "depends" in obj:
            obj['depends'] = "dummy" # dummy package, nothing
        return obj
    except Exception as e:
        raise e
class dbManager: # Expects a Package List Database table ,not a repository list
    def __init__(self, root="/"):
        self.root = root
        if not os.path.isfile(f'{root}/var/upk-ng/upkng.db'):
            os.makedirs(f'{root}/var/upk-ng', exist_ok=True)
            open(f'{root}/var/upk-ng/upkng.db', 'w').write(' ').close()
        self.conn = sqlite3.connect(f'{root}/var/upk-ng/upkng.db')
        self.cursor = self.conn.cursor()
        self._initTransaction()
    def add(self, name, version):
        self.cursor.execute("""""")
    def _initTransaction(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            version TEXT NOT NULL,
            installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            index TEXT NOT NULL 
        )
        """)
        self.conn.commit()
    def addPackage(self, name, version, index):
        self.cursor.execute("""
            INSERT INTO packages (name, version, index)
            VALUES (?, ?, ?)
        """, (name, version, index))
        self.conn.commit()
    def delPackage(self, name):
        self.cursor.execute("""
        DELETE FROM packages WHERE name = ?
        """, (name))
        self.cursor.commit()
    def getPackage(self, name):
        self.cursor.execute("""
        SELECT * FROM packages WHERE name = ?
        """, (name))
        pkg = self.cursor.fetchone()
        return pkg
    def endTransaction(self):
        self.conn.close()
