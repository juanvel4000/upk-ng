import upk_data,upk_pkg,upk_utils,sys,os,upk_net
from upk_utils import echo
note = False
if os.path.isfile('upk_info.py'):
    from upk_info import version, rel, maintainer
else:
    note = True
    version, rel, maintainer, impnote = "0.0", "1", "John Doe", "this is either raw code or an invalid build\n-> please build using buildUtil"
    
from upk_data import requestLock, requestRoot, quitLock

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
        upk_net.checkConf()
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
                echo("install <package> [options]   -   download (and install) a package from a(ny) repository",3)
                echo("list [repo]                   -   list all the available packages from [repo] or any repository",3)
                echo("build <workdir> [output]      -   build <workdir> as [output], default output: name-version.upk",3)
                echo("addrepo <name> <url>          -   add a new repository to the repository list",3)
                echo("update [repo]                 -   update [repo] or all repositories",3)
                echo("help                          -   show this message",3)
                echo("version                       -   show the upk-ng version, maintainer and release",3)
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
                requestRoot()
                check = True
                architecture = os.uname()
                downloadOnly = False
                version = "any"
                if '--skipcheck' in sys.argv: # disable sha256sum check
                    check = False
                if '--any' in sys.argv: # any architecture
                    architecture = "any"
                if '--dl' in sys.argv: # only download
                    downloadOnly = True
                if "--version" in sys.argv:
                    index = sys.argv.index("--version")  
                    if index + 1 < len(sys.argv):  
                        version = sys.argv[index + 1]

                data = upk_net.getRepo(sys.argv[2], architecture, version)
                if not data:
                    echo(f"could not find {sys.argv[2]}, check your network, update repositories or check if the package exists in the repositoies", ke="!")
                    exit(1)
                # pkg has been found
                pkgId = data[1]
                pkgRepo = data[0]
                
                # download
                output = upk_net.downloadfromRepobyid(pkgId, pkgRepo, None, architecture, version, check)
                if not output:
                    echo("could not download the package, check your network")
                    raise FileNotFoundError("network error")
                if downloadOnly == True:
                    echo(f"downloaded package to {output}")
                    exit(0)
                if not check:
                    echo("skipping sum check")
                    pass
                else:
                    echo("checking sum...")
                    check = sha256sumCheck(output)
                    if not check:
                        echo("sum is invalid, removing downloaded packages")
                        os.remove(output)
                        os.remove(f'{output}.sha256')
                        exit(1)
                    echo("valid sum, continuing")
                result = upk_pkg.installPackage(output)
                upk_net.installDepends(result[1])
                requestLock()
            case 'list':
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
                if note == True:
                    echo(impnote)
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