import os,sys,shutil
import upk_pkg, upk_data
from upk_utils import echo
from upk_data import dbManager
def newCheckpoint(name):
    try:
        upk_data.requestRoot()
        # 1st. get pkg info
        db = dbManager('/')
        pkg = db.getPackage(name)
        if not pkg:
            return False
        name, version = pkg['name'], pkg['version']
        if pkg['checkpoint'] != 1:
            return False
        # 2nd list the pkg files
        files = pkg['files'].strip().split('\n')
        # ensure files are valid
        fail = 0
        for i in files:
            if not os.path.isfile(os.path.join('/', i)):
                fail += 1
        if fail > 0:
            return False
        # create directories for checkpointizeing
        checkpointizedir = os.path.join('/var/lib/upk-ng/checkpoints', name, version)
        if os.path.isdir(checkpointizedir):
            shutil.rmtree(checkpointizedir)
        os.makedirs(checkpointizedir)
        # preppend a / to every file
        filez = []
        for i in files:
            filez.append(os.path.join('/', i))
        files = filez
        # everything is done now, transfer files safely
        fail = 0
        for i in files:
            try:
                src = os.path.abspath(i)
                directory = os.path.dirname(src)
                newdir = checkpointizedir + '/' + directory
                os.makedirs(newdir, exist_ok=True)
                shutil.copy(src, newdir)
            except Exception as e:
                echo(e)
                fail += 1
        if fail > 0:
            return False
        # update the database thing
        db.cursor.execute("UPDATE packages SET isFrozen = 1 WHERE name = ?",(name,))
        db.conn.commit()
        echo(f"created a checkpoint for {name} version {version}")
        return True
    except Exception as e:
        echo(e)
        raise e
def rollbackPackage(name, version=None):
    try:
        db = dbManager('/')
        pkg = db.getPackage(name)
        if not pkg:
            return False
        name, pkg_version = pkg['name'], pkg['version']
        basecheckpointizedir = '/var/lib/upk-ng/checkpoints'
        pkgcheckpointizedir = os.path.join(basecheckpointizedir, name)
        
        for i in [basecheckpointizedir, pkgcheckpointizedir]:
            if not os.path.isdir(i):
                return False
        
        if pkg['isFrozen'] != 1:
            return False
        
        if not os.listdir(pkgcheckpointizedir):
            return False  # no versions
        
        if version is None:
            available_versions = os.listdir(pkgcheckpointizedir)
            available_versions = sorted(available_versions, reverse=True)
            version = available_versions[0]
        
        if not os.path.isdir(os.path.join(pkgcheckpointizedir, version)):
            echo("package version not found")
            return False
        
        vercheckpointizedir = os.path.join(pkgcheckpointizedir, version)
        # starting to decheckpointize
        # step 1, carefully create a list of files to be copied
        files = []
        fail = 0
        for i in os.listdir(vercheckpointizedir):
            src_path = os.path.join(vercheckpointizedir, i)
            if os.path.isdir(src_path):
                continue
            if not os.path.isfile(src_path):
                echo(src_path)
                fail += 1
                continue
            files.append(src_path)
        if fail > 0:
            echo(fail)
            echo("missing file(s)")
            return False
        # step 2, delete the package
        # upk_pkg.deletePackage(name, "/")
        # step 3, copy the files safely
        filelist = []
        for src in files:
            try:
                rel_path = os.path.relpath(src, vercheckpointizedir)
                dest = os.path.join('/', rel_path.lstrip('/'))  # Ensure absolute path
                destdir = os.path.dirname(dest)
                os.makedirs(destdir, exist_ok=True)
                shutil.copy(src, dest)
                filelist.append(dest)
            except Exception as e:
                echo(f"unrecoverable error during file copy: {e}")
                raise e
                sys.exit(1)
        # step 4: add to pkg db
        filelist = "\\n".join(map(str, filelist))
        pkg = db.addPackage(name, version, filelist, True)
        if not os.listdir(pkgcheckpointizedir):
            db.cursor.execute("UPDATE packages SET isFrozen = 0 WHERE name = ?",(name,))
            db.conn.commit()
        return True
    except Exception as e:
        echo(e)
        raise e