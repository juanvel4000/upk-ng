import upk_data, upk_pkg, upk_utils, sys, os, upk_net, upk_checkpoint
from upk_utils import echo
from upk_info import rel, version, maintainer
from upk_data import requestLock, requestRoot, quitLock

def exit(code):
    sys.exit(code)

def sha256sumCheck(f):
    valid = upk_utils.genSha256sum(f)
    if not os.path.isfile(f'{f}.sha256'):
        return False
    expected = open(f'{f}.sha256', 'r').read()
    if expected != valid:
        return False
    return True

if __name__ == "__main__":
    try:
        os.makedirs(f'/var/lib/upk-ng', exist_ok=True)
        if len(sys.argv) < 2:
            echo("error: usage: << upk [command] >>")
            sys.exit(1)
        match sys.argv[1]:
            case 'help':
                echo(f"upk-ng {version}-{rel}")
                echo("next generation upk package manager")
                echo("usage: << upk [options] >>")
                echo("options", 2)
                echo("remove <package> [root]       -   remove <package> from [root], default root: /", 3)
                echo("install-local <package>       -   install a package file (.upk)", 3)
                echo("install <package> [options]   -   download (and install) a package from a(ny) repository", 3)
                echo("list [repo]                   -   list all the available packages from [repo] or any repository", 3)
                echo("build <workdir> [output]      -   build <workdir> as [output], default output: name-version.upk", 3)
                echo("addrepo <name> <url>          -   add a new repository to the repository list", 3)
                echo("update [repo]                 -   update [repo] or all repositories", 3)
                echo("help                          -   show this message", 3)
                echo("version                       -   show the upk-ng version, maintainer and release", 3)
                echo("checkpoint <package>          -   create a checkpoint of <package>, replace <package> with --all to create a checkpoint for every package")
                echo("rollback <package> [version]  -   rollback <package> [version], [version] does not apply when <package> is --all")
            case 'remove':
                requestRoot()
                requestLock()
                root = "/"
                if len(sys.argv) > 3:
                    root = sys.argv[3]
                if len(sys.argv) < 2:
                    echo("error: missing arguments for << upk remove >>")
                    sys.exit(1)
                upk_pkg.deletePackage(sys.argv[2], root)
            case 'install-local':
                requestLock()
                requestRoot()
                root = "/"
                if len(sys.argv) > 3:
                    root = sys.argv[3]
                if len(sys.argv) < 2:
                    echo("error: missing arguments for << upk install-local >>")
                    sys.exit(1)
                upk_pkg.installPackage(sys.argv[2], root)
            case 'install':
                upk_net.checkConf()
                requestRoot()
                check = True
                architecture = os.uname()
                downloadOnly = False
                version = "any"
                pkgRepo = ""
                specificRepo = False
                root = "/"
                if '--skipcheck' in sys.argv:
                    check = False
                if '--any' in sys.argv:
                    architecture = "any"
                if '--dl' in sys.argv:
                    downloadOnly = True
                if "--version" in sys.argv:
                    index = sys.argv.index("--version")  
                    if index + 1 < len(sys.argv):  
                        version = sys.argv[index + 1]
                if "--repo" in sys.argv:
                    if sys.argv.index("--repo") + 1 < len(sys.argv):
                        pkgRepo = sys.argv[sys.argv.index("--repo") + 1]
                        specificRepo = True
                if "--root" in sys.argv:
                    if sys.argv.index("--root") + 1 < len(sys.argv):
                        root = sys.argv[sys.argv.index("--root") + 1]
                if not specificRepo:
                    data = upk_net.getRepo(sys.argv[2], architecture, version)
                    if not data:
                        echo(f"could not find {sys.argv[2]}, update repositories or check if the package exists in the repositories", ke="!")
                        exit(1)
                    pkgId = data[1]
                    pkgRepo = data[0]
                else:
                    pkgId = upk_net.getId(pkgRepo, sys.argv[2], architecture, version)
                    if not pkgId:
                        echo("package not found in specified repo")
                        exit(1)
                output = upk_net.downloadfromRepobyid(pkgId, pkgRepo, None, architecture, version, check)
                if not output:
                    echo("could not download the package, check your network")
                    raise FileNotFoundError("network error")
                if downloadOnly:
                    echo(f"downloaded package to {output}")
                    exit(0)
                if not check:
                    echo("skipping sum check")
                else:
                    echo("checking sum...")
                    check = sha256sumCheck(output)
                    if not check:
                        echo("sum is invalid, removing downloaded packages")
                        os.remove(output)
                        os.remove(f'{output}.sha256')
                        exit(1)
                    echo("valid sum, continuing")
                result = upk_pkg.installPackage(output, root)
                upk_net.installDepends(result[1])
                quitLock()
            case 'list':
                upk_net.checkConf()
                if len(sys.argv) >= 3:
                    repo = upk_net.listRepo(sys.argv[2])
                    for pkg in repo:
                        pkg = repo[pkg]
                        echo(f"{pkg['name']} / {pkg['version']}-{pkg['architecture']}", 2)        
                        echo(f"source: {pkg['repo']}::{pkg['id']}")
                    exit(0)
                repos = upk_net.listallRepos()
                for repo in repos:
                    repo = repos[repo]
                    for pkg in repo:
                        pkg = repo[pkg]
                        echo(f"{pkg['name']} / {pkg['version']}-{pkg['architecture']}", 2)        
                        echo(f"source: {pkg['repo']}::{pkg['id']}")
                exit(0)
            case 'build':
                if len(sys.argv) < 3:
                    echo("error: missing arguments for << upk build >>")
                    sys.exit(1)
                o = None
                if len(sys.argv) > 3:
                    o = sys.argv[3]
                upk_utils.compress(sys.argv[2], o)  
            case 'addrepo':
                requestRoot()
                upk_net.checkConf()
                if len(sys.argv) < 4:
                    echo("error: missing arguments for addrepo")
                    exit(1)
                open('/etc/upk-ng/repos', 'a').write(f"[{sys.argv[2]}]\nserver = {sys.argv[3]}\n")
                echo(f"added {sys.argv[2]}, run << upk update >>")
            case 'list-local':
                requestRoot()
                requestLock()
                db = upk_data.dbManager('/')
                pkgs = db.getAllPackages()
                for i in pkgs:
                    echo(f"{i['name']} {i['version']}", 2)
                    echo(f"id: {i['id']} installed at: {i['installed_at']}")
            case 'list-files':
                if len(sys.argv) < 3:
                    echo("error: missing arguments for list-files")
                    exit(1)
                db = upk_data.dbManager('/')
                i = db.getPackage(sys.argv[2])
                print(f"/{i[4]}")                
            case 'update':
                requestRoot()
                requestLock()
                upk_net.checkConf()
                if len(sys.argv) >= 3:
                    upk_net.updateRepo(sys.argv[2])
                    exit(0)
                else:
                    upk_net.updateAllrepos()
            case 'version':
                echo(f"upk-ng ver {version}")
                echo(f"release {rel} by {maintainer}") 
            case 'checkpoint':
                requestRoot()
                requestLock()
                if len(sys.argv) < 3:
                    echo("missing arguments for checkpoint")
                    exit(1)
                if sys.argv[2] == "--all":
                    db = upk_data.dbManager('/')
                    pkgs = db.getAllPackages()
                    for i in pkgs:
                        upk_checkpoint.newCheckpoint(i['name'])
                else:
                    upk_checkpoint.newCheckpoint(sys.argv[2])
            case 'rollback':
                requestRoot()
                requestLock()
                if len(sys.argv) < 3:
                    echo("missing arguments for rollback")
                    exit(1)
                if sys.argv[2] == "--all":
                    db = upk_data.dbManager('/')
                    pkgs = db.getAllPackages()
                    for i in pkgs:
                        if i['isFrozen'] == 0:
                            continue
                        if i['name'] == "upk-ng":
                            echo("cannot rollback upk-ng, please run (as root) << git clone https://github.com/juanvel4000/upk-ng && cd upk-ng/src && python upk.py rollback upk-ng >>")
                        upk_checkpoint.rollbackPackage(i['name'], None)
                else:
                    version = None
                    if len(sys.argv) < 4:
                        version = sys.argv[3]
                    upk_checkpoint.rollbackPackage(sys.argv[2], version)
            case _:
                echo(f"invalid command {sys.argv[1]}, view << upk help >> for more information")

    except Exception as e:
        raiseex = "1"
        if raiseex == "0":
            echo(e)
        else:
            raise e
        sys.exit(1)
    finally:
        quitLock()
