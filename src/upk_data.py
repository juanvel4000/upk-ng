import sqlite3, json, os, time, sys# sqlite: db and stuff, json: manifest, os: general, time: sleep, sys: exit
def echo(m, l=1, ks="-", ke=">", n=True):
    print(ks * l, end="")
    print(f"{ke} {m}", end="\n" if n else "")
def convertFts(f): # convert file to str
    if os.path.isfile(f):
        return open(f, 'r').read()
    else:
        raise FileNotFoundError(f"{f} not found")
def getManifest(string): # usage: getManifest(convertFts(file))
    try:
        obj = json.loads(string)
        for crit in ["name", "maintainer", "version", "summary"]: # check for critical stuff
            if not crit in obj:
                raise KeyError(f"{crit} not found in manifest")
        if not "depends" in obj:
            obj['depends'] = "dummy" # dummy package, nothing
        return obj
    except Exception as e:
        raise e
class dbManager: 
    def __init__(self, root="/"):
        self.root = root
        os.makedirs(f'{root}/var/upk-ng', exist_ok=True)
        self.conn = sqlite3.connect(f'{root}/var/upk-ng/upkng.db')
        self.cursor = self.conn.cursor()
        self._initTransaction()
        self.conn.row_factory = sqlite3.Row
    def add(self, name, version):
        self.cursor.execute("""""")
    def _initTransaction(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            version TEXT NOT NULL,
            installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            files TEXT NOT NULL 
        )
        """)
        self.conn.commit()
    def addPackage(self, name, version, index):
        self.cursor.execute("""
            INSERT INTO packages (name, version, files)
            VALUES (?, ?, ?)
        """, (name, version, index))
        self.conn.commit()
    def delPackage(self, name):
        self.cursor.execute("""
        DELETE FROM packages WHERE name = ?
        """, (name,))
        self.conn.commit()
    def getPackage(self, name):
        self.cursor.execute("""
        SELECT * FROM packages WHERE name = ?
        """, (name,))
        pkg = self.cursor.fetchone()
        return pkg if pkg else None
    def endTransaction(self):
        self.conn.close()

# START UPK REQUESTS
def requestRoot():
    if os.geteuid != 0:
        echo("please run as root")
        sys.exit(1)
def requestLock():
    if os.path.isfile('/var/lib/upk-ng/lock'):
        s = 0
        while True:
            if not os.path.isfile('/var/lib/upk-ng/lock'):
                print(f"\rlock unlocked, waited for {s}s")
                break
            print(f"\rwaiting for lock to be unlocked ({s}s)", end="")
            time.sleep(1)
            s += 1
    with open('/var/lib/upk-ng/lock', 'w') as lock:
        lock.write("im not putting the dragon, later maybe")
    return True
def quitLock():
    if os.path.isfile('/var/lib/upk-ng/lock'):
        os.remove('/var/lib/upk-ng/lock')
    return True