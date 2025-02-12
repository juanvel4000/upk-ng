from upk_data import requestRoot
import os, configparser, urllib.request
from upk_utils import echo

def checkConf():
    requestRoot()
    os.makedirs('/etc/upk-ng', exist_ok=True)
    if not os.path.isfile('/etc/upk-ng/repos'):
        with open('/etc/upk-ng/repos', 'w') as repos:
            repos.write("""; repository list for upk-ng
; add repos like this
; [reponame]
; server = url
""")

def updateRepo(repo):
    try:
        checkConf()
        cfg = configparser.ConfigParser()
        cfg.read('/etc/upk-ng/repos')
        if repo not in cfg:
            return False
        os.makedirs('/var/upk-ng/repos', exist_ok=True)
        echo("downloading Release")
        urllib.request.urlretrieve(f"{cfg[repo]['server']}/Release", f"/var/upk-ng/repos/{repo}")
        echo("repository updated")
    except urllib.error.HTTPError:
        echo("error downloading the repository")
def updateAllrepos():
    cfg = configparser.ConfigParser()
    cfg.read('/etc/upk-ng/repos')
    for i in cfg.sections():
        echo(f'updating {i}')
        updateRepo(i)

def getRepo(package, arch="any", version="any"):
    for i in os.listdir('/var/upk-ng/repos'):
        with open(f'/var/upk-ng/repos/{i}', 'r') as repo:
            for p in repo:
                if not p.strip():
                    continue
                name, ver, archt, pkgId = p.strip().split('=>')
                if name == package and (arch == "any" or archt == os.uname().machine) and (version == "any" or version == ver):
                    return i, pkgId 
    return False


def downloadfromRepobyid(pkgId, repo, output=None, arch="any", version="any", includesum=True):
    try:
        with open(f'/var/upk-ng/repos/{repo}', 'r') as r:
            for p in r:
                pkg = p.strip().split('=>')

                if len(pkg) < 4:
                    continue
                
                name, ver, archt, pid = pkg
                
                if pid == pkgId:
                    output = output or f"/var/cache/upk-ng/{name}-{ver}-{archt}.upk"
                    os.makedirs(os.path.dirname(output), exist_ok=True)

                    cfg = configparser.ConfigParser()
                    cfg.read('/etc/upk-ng/repos')

                    if repo not in cfg or 'server' not in cfg[repo]:
                        print(f"error: missing server information for repo '{repo}'")
                        return False

                    srv = cfg[repo]['server']
                    echo(f"retrieving {name}:{ver}-{archt}")

                    urllib.request.urlretrieve(f'{srv}/pool/{name}-{ver}-{archt}.upk', output)

                    if includesum:
                        urllib.request.urlretrieve(f'{srv}/sums/{name}-{ver}-{archt}.sha256', f'{output}.sha256')
                    else:
                        print("warning: sha256sum not downloaded, package may be invalid")

                    return output

        return False
    except Exception as e:
        print(f"error: {e}")
        return False

def installDepends(obj, repo="any", arch="any", version="any", includesum=True, alsoinstall=True, root="/"):
    try:
        failure, success = [], []
        for i in obj:
            if i == "dummy":
                continue
            repository = getRepo(i, arch, version) if repo == "any" else (repo, None)
            if not repository:
                failure.append(i)
                continue
            loca = downloadfromRepobyid(repository[1], repository[0], None, arch, version, includesum)
            if not loca:
                failure.append(i)
                continue
            if includesum and not os.path.isfile(f'{loca}.sha256'):
                failure.append(i)
                continue
            if alsoinstall:
                d = upk_pkg.installPackage(loca, root)
                success.append({"name": i, "repo": repository[0], "location": loca, "installed": alsoinstall, "checksum": includesum})
        return failure, success
    except Exception as e:
        raise e
def listRepo(repo):
    checkConf()
    pkgs = {}
    with open(f'/var/upk-ng/repos/{repo}', 'r') as pkg:
        lines = pkg.readlines()
        for i in lines:
            data = i.strip().split('=>')
            
            if len(data) >= 4:
                pkgs[data[0]] = {
                    "name": data[0],
                    "version": data[1],
                    "architecture": data[2],
                    "id": data[3],
                    "repo": repo
                }
            else:
                pass
    return pkgs

def listallRepos():
    if not os.path.isdir(f'/var/upk-ng/repos'):
        return False
    repos = os.listdir('/var/upk-ng/repos')
    pkgs = {}
    for i in repos:
        pkgs[i] = listRepo(i)
    return pkgs
