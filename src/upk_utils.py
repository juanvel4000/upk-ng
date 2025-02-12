import tarfile, hashlib, os, shutil, json
from upk_data import getManifest, convertFts
def echo(m, l=1, ks="-", ke=">", n=True):
    print(ks * l, end="")
    print(f"{ke} {m}", end="\n" if n else "")
def genSha256sum(f, o=None):
    sha256 = hashlib.sha256()
    try:
        with open(f, "rb") as file:
            while chunk := file.read(8192):
                sha256.update(chunk)
        shum = sha256.hexdigest()
        if o:
            with open(o, 'w') as output:
                output.write(shum)
        return shum
    except FileNotFoundError:
        raise FileNotFoundError(f"{f} not found")
    except Exception as e:
        raise e

def createDirlist(d, e=['UPK']):
    echo(f"logging all files in {d}", 2)
    if e is None:
        e = []

    bigstring = ""
    for dirpath, dirnames, filenames in os.walk(d):
        dirnames[:] = [dn for dn in dirnames if os.path.join(dirpath, dn) not in e]

        if any(dirpath.startswith(os.path.join(d, excluded)) for excluded in e):
            continue

        for f in filenames:
            p = os.path.join(dirpath, f)
            r = os.path.relpath(p, d)
            bigstring += r + "\n"

    return bigstring.strip()



def ft(tarinfo, x):
    return tarinfo

def extract(f, o="/tmp/upkng/extract"):
    try:
        echo(f"unpacking {os.path.basename(f)}...", 1)
        with tarfile.open(f, 'r|xz') as tar:
            os.makedirs(o, exist_ok=True)
            tar.extractall(o, filter=ft)  
        
        manifest_path = os.path.join(o, 'UPK', 'info.json')
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"manifest file not found at {manifest_path}")
        
        man = getManifest(convertFts(manifest_path))
        shutil.rmtree(os.path.join(o, 'UPK'))
        
        return {
            "Output": o,
            "Manifest": man
        }
    except tarfile.TarError as te:
        raise Exception(f"Error extracting tar file: {str(te)}") from te
    except FileNotFoundError as fnf:
        raise Exception(f"File not found: {str(fnf)}") from fnf
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}") from e


def compress(workdir, o=None, arch=os.uname()):
    if not os.path.isfile(os.path.join(workdir, 'UPK', 'info.json')):
        raise FileNotFoundError("could not find UPK/info.json in workdir")
    man = getManifest(convertFts(os.path.join(workdir, 'UPK', 'info.json')))
    if not man:
        raise KeyError("invalid manifest")
    if o == None:
        o = f"{man['name']}-{man['version']}."
        op = o + "upk"
        osh = o + "sha256"
    echo(f"creating package {op}...")
    dirlist = createDirlist(workdir)
    
    with open(os.path.join(workdir, 'UPK', 'info.json'), 'r') as j:
        d = json.load(j)
    d["files"] = dirlist.splitlines()
    d['bigstring'] = dirlist
    with open(os.path.join(workdir, 'UPK', 'info.json'), 'w') as j:
        json.dump(d, j, indent=4)


    with tarfile.open(op, 'w:xz') as pkg:
        for dirpath, dirnames, filenames in os.walk(workdir):

            for f in filenames:
                file_path = os.path.join(dirpath, f)
                arcname = os.path.relpath(file_path, workdir)
                pkg.add(file_path, arcname=arcname)
    echo("generating a hash", 2)
    genSha256sum(op, f"{osh}")
    echo ("done", 2)
    return o