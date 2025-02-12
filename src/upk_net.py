from upk_data import requestRoot, requestLock
import os,configparser
import urllib.request, subprocess
from upk_utils import echo
def checkConf():
    requestRoot()
    os.makedirs('/etc/upk-ng', exist_ok=True)
    if not os.path.isfile('/etc/upk-ng/repos'):
        with open('/etc/upk-ng/repos', 'w') as repos:
            repos.write("""
            ; repository list for upk-ng\n
            ; add repos like this\n
            ; [reponame]\n
            ; server = url\n
            
            """)
def updateRepo(repo):
    checkConf()
    cfg = configparser.ConfigParser()
    cfg.read('/etc/upk-ng/repos')
    if repo not in cfg.sections():
        return False
    else:
        rd = cfg[repo]
        os.makedirs('/etc/upk-ng/repos', exist_ok=True)
        echo(f"downloading Release")
        urllib.request.retrieve(rd['server'] + '/Release',f'/var/upk-ng/repos/{repo}')
        echo(f"repository updated")
def updateAllrepos():
    cfg = configparser.ConfigParser()
    cfg.read('/etc/upk-ng/repos')
    for i in cfg.sections():
        echo(f'updating {i}')
        updateRepo(i)    
def getRepo(package, arch="any", version="any"):
    repos = os.listdir('/var/upk-ng/repos')
    for i in repos:
        with open(i, 'r') as repo:
            packages = repo.readlines()
            for i in packages:
                v = packages.strip().split('=>')
                name, ver, archt = v[0], v[1], v[2]
                if name == package:
                    if arch == "any":
                        if version == "any":
                            return repo, v[3]
                        elif version == ver:
                            return repo, v[3]
                        else:
                            continue
                    elif arch == os.uname():
                        return repo, v[3]
                    else:
                        continue
                else:
                    continue
    return False
def downloadfromRepobyid(pkgId, repo, output=None, arch="any", version="any", includesum=True):
    try:
        with open(f'/var/upk-ng/repos/{repo}', 'r') as r:
            entries = r.readlines()
            for i in entries:
                if i.strip().split('=>')[3] == pkgId:
                    data = i.strip().split('=>')
                    if output == None: 
                        output = "/tmp/upk-ng"
                        os.makedirs(output, exist_ok=True)
                        output += f"/{data[0]}-{data[1]}-{data[2]}.upk"
                    cfg = configparser.ConfigParser()
                    cfg.read('/etc/upk-ng/repos')
                    urllib.request.retrieve(f'{cfg[repo]['server']}/pool/{data[0]}-{data[1]}-{data[2]}.upk',output)
                    if includesum:
                        urllib.request.retrieve(f'{cfg[repo]['server']}/pool/{data[0]}-{data[1]}-{data[2]}.upk.sha256',f'{output}.sha256')
                    else:
                        echo("warning: sha256sum not downloaded, package may be invalid")
                    return output
        return False
    except Exception as e:
        raise e

