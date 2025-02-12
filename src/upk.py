import upk_data,upk_pkg,upk_utils,sys,os,upk_net
from upk_utils import echo
from upk_info import version, rel, maintainer
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
            
        if len(sys.argv) < 2:
            echo("error: usage: << upk [command] >>")
            sys.exit(1)
        match sys.argv[1]:
            case 'help':
                echo(f"upk-ng {version}-{rel}")
                echo("next generation upk package manager")
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
                quitLock()
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
                quitLock()
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
                if "--version" in args:
                    index = sys.argv.index("--version")  
                    if index + 1 < len(sys.argv):  
                        version = sys.argv[index + 1]

                data = upk_net.getRepo(sys.argv[2], architecture, version)
                if not data:
                    echo(f"could not find {package}, check your network, update repositories or check if the package exists in the repositoies", ke="!")
                    exit(1)
                # pkg has been found
                pkgId = data[1]
                pkgRepo = data[0]
                
                # download
                output = upk_net.downloadfromRepobyid(pkgId, pkgRepo, None, architecture, version, check)
                if not output:
                    echo("could not download the package, check your network")
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
                upk_pkg.installPackage(output)

                requestLock()
                quitLock()
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
                if len(sys.argv) < 5:
                    echo("error: missing arguments for addrepo")
                open('/etc/upk-ng/repos', 'a').write(f"""
                [{sys.argv[2]}]\n
                server = {sys.argv[3]}\n
                """)
                echo(f"added {sys.argv[2]}, run << upk update >>")
            case 'update':
                requestRoot()
                requestLock()
                upk_net.checkConf()
                if len(sys.argv) < 3:
                    upk_net.updateRepo(sys.argv[2])
                else:
                    upk_net.updateAllrepos()
            case 'version':
                echo(f"upk-ng ver {version}")
                echo(f"release {rel} by {maintainer}")      
            case _:
                echo(f"invalid command {sys.argv[1]}, view << upk help >> for more information")
    except Exception as e:
            echo(e)
            sys.exit(1)