from upk_data import dbManager, getManifest, convertFts
from upk_utils import extract, echo, createDirlist, genSha256sum,subprocess
import os, shutil, json
import tempfile
def installPackage(f, root="/"):
    shum = genSha256sum(f)
    tmp = os.path.join(root, 'tmp', 'upk', shum)

    if os.path.isdir(tmp):
        shutil.rmtree(tmp)
    os.makedirs(tmp, exist_ok=True)
    man = extract(f, tmp)['Manifest']
    pre = False
    post = False
    if "scripts" in man:
        post = man['scripts']['Post']
        pre = man['scripts']['pre']
    if not pre:
        pass
    else:
        subprocess.run([f'{tmp}/scripts/{pre}'], shell=True)
    
    for dirpath, dirnames, filenames in os.walk(tmp):
        if 'scripts' in dirnames:
            dirnames.remove('scripts')
        
        for d in dirnames:
            dest_dir = os.path.join(root, os.path.relpath(os.path.join(dirpath, d), tmp))
            os.makedirs(dest_dir, exist_ok=True)

        for file in filenames:
            src = os.path.join(dirpath, file)
            dest = os.path.join(root, os.path.relpath(src, tmp))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(src, dest)
    if not post:
        pass
    else:
        subprocess.run([f'{tmp}/scripts/{pre}'], shell=True)
    db = dbManager(root)
    db.addPackage(man['name'], man['version'], man['bigstring'], man['freeze'])
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
    bs = pkg['files'].strip().split('\n')
    for i in bs:
        os.remove(os.path.join(root, i))
    db = dbManager(root)
    pkg = db.delPackage(name)
    db.endTransaction()