from upk_data import dbManager, getManifest, convertFts
from upk_utils import extract, echo, createDirlist, genSha256sum
import os, shutil, json
import tempfile
def installPackage(f, root="/"):
    shum = genSha256sum(f)
    tmp = os.path.join(root, 'tmp', 'upk', shum)

    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp, exist_ok=True)
    man = extract(f, tmp)['Manifest']

    for dirpath, dirnames, filenames in os.walk(tmp):
        for d in dirnames:
            dest_dir = os.path.join(root, os.path.relpath(os.path.join(dirpath, d), tmp))
            os.makedirs(dest_dir, exist_ok=True)
        for file in filenames:
            src = os.path.join(dirpath, file)
            dest = os.path.join(root, os.path.relpath(src, tmp))
            os.makedirs(os.path.dirname(dest), exist_ok=True)  
            shutil.move(src, dest)

    db = dbManager(root)
    db.addPackage(man['name'], man['version'], man['bigstring'])
    db.endTransaction()
    shutil.rmtree(tmp)
    echo(f"installed {man['name']} {man['version']}")
    return man['name'], man['depends'], man

def deletePackage(name, root=""):
    db = dbManager(root)
    pkg = db.getPackage(name)
    if pkg == None:
        echo("package does not exist")
        return None
    echo(f"removing {name}")
    bs = pkg[4].splitlines()
    for i in bs:
        os.remove(os.path.join(root, i))
    db = dbManager(root)
    pkg = db.delPackage(name)
    db.endTransaction()