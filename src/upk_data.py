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
        for crit in ["name", "maintainer", "version", "summary", "architecture"]: # check for critical stuff
            if not crit in obj:
                raise KeyError(f"{crit} not found in manifest")
        if not "depends" in obj:
            obj['depends'] = "dummy" # dummy package, nothing
        if not "checkpoint" in obj:
            obj['checkpoint'] = True
        else:
            if obj['checkpoint'] not in [True, False]:
                obj['checkpoint'] = True
        return obj
    except Exception as e:
        raise e
class dbManager: 
    def __init__(self, root="/"):
        self.root = root
        os.makedirs(f'{root}/var/lib/upk-ng/', exist_ok=True)
        self.conn = sqlite3.connect(f'{root}/var/lib/upk-ng/upkng.db')
        self.cursor = self.conn.cursor()
        self._initTransaction()
        self.conn.row_factory = sqlite3.Row
        self.cursor.execute("SELECT COUNT(*) FROM packages")
        count = self.cursor.fetchone()[0]
        if count == 1:
            echo(f"initializing database... ({count} package installed)")
        else:
            echo(f"initializing database... ({count} packages installed)")  
    
        
    def _initTransaction(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            version TEXT NOT NULL,
            installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            files TEXT NOT NULL,
            checkpoint BOOL NOT NULL DEFAULT 1, 
            hasCheckpoint BOOL NOT NULL DEFAULT 0
        );
        """)
        self.conn.commit()

        self._updateTableStructure()

    def _updateTableStructure(self):
        self.cursor.execute("PRAGMA table_info(packages)")
        existing_columns = {row[1] for row in self.cursor.fetchall()}

        expected_columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "name": "TEXT NOT NULL",
            "version": "TEXT NOT NULL",
            "installed_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "files": "TEXT NOT NULL",
            "checkpoint": "BOOL NOT NULL DEFAULT 1",
            "hasCheckpoint": "BOOL NOT NULL DEFAULT 0"
        }

        for column, definition in expected_columns.items():
            if column not in existing_columns:
                self.cursor.execute(f"ALTER TABLE packages ADD COLUMN {column} {definition}")

        self.conn.commit()
    def addPackage(self, name, version, index, checkpoint=True):
        self.cursor.execute("""
            SELECT * FROM packages WHERE name = ?
        """, (name,))
        existing_package = self.cursor.fetchone()  

        if existing_package:
            self.cursor.execute("""
                UPDATE packages
                SET version = ?, files = ?, checkpoint=?
                WHERE name = ?
            """, (version, index, checkpoint, name))
        else:
            self.cursor.execute("""
                INSERT INTO packages (name, version, files, checkpoint, hasCheckpoint)
                VALUES (?, ?, ?, ?, 0)
            """, (name, version, index, checkpoint))
        
        self.conn.commit()

    def delPackage(self, name):
        self.cursor.execute("""
        DELETE FROM packages WHERE name = ?
        """, (name,))
        self.conn.commit()
    def getPackage(self, name):
        self.cursor.execute("SELECT * FROM packages WHERE name = ?", (name,))
        columns = [desc[0] for desc in self.cursor.description]
        row = self.cursor.fetchone()
        return dict(zip(columns, row)) if row else None

    def getAllPackages(self):
        self.cursor.execute("SELECT * FROM packages")
        columns = [desc[0] for desc in self.cursor.description] 
        rows = self.cursor.fetchall()  
        packages = [dict(zip(columns, row)) for row in rows] 
        return packages if packages else None
    def endTransaction(self):
        self.conn.close()

# START UPK REQUESTS
def requestRoot():
    if os.geteuid() != 0:
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
        lock.write("""
        here is the dragon
                         / \  //\
           |\___/|      /   \//  \\
            /0  0  \__  /    //  | \ \    
           /     /  \/_/    //   |  \  \  
           @_^_@'/   \/_   //    |   \   \ 
           //_^_/     \/_ //     |    \    \
        ( //) |        \///      |     \     \
      ( / /) _|_ /   )  //       |      \     _\
    ( // /) '/,_ _ _/  ( ; -.    |    _ _\.-~        .-~~~^-.
  (( / / )) ,-{        _      `-.|.-~-.           .~         `.
 (( // / ))  '/\      /                 ~-. _ .-~      .-~^-.  \
 (( /// ))      `.   {            }                   /      \  \
  (( / ))     .----~-.\        \-'                 .~         \  `. \^-.
             ///.----..>        \             _ -~             `.  ^-`  ^-_
               ///-._ _ _ _ _ _ _}^ - - - - ~                     ~-- ,.-~
                                                                  /.-~
        
        """)
    return True
def quitLock():
    if os.path.isfile('/var/lib/upk-ng/lock'):
        os.remove('/var/lib/upk-ng/lock')
    return True