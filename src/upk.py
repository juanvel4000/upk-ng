import upk_data,upk_pkg,upk_utils,sys,os
from upk_utils import echo
from upk_info import version, rel, maintainer
if __name__ == "__main__":
    try:
            
        if len(sys.argv) < 2:
            echo("error: usage: << upk [command] >>")
            sys.exit(1)
        match sys.argv[1]:
            case 'help':
                echo(f"upk-ng {version}-{rel} (by {maintainer})")
                echo("next generation upk package manager")
            case 'remove':
                root = "/"
                if len(sys.argv) > 3:
                    root = sys.argv[3]
                if len(sys.argv) < 2:
                    echo("error: missing arguments for << upk remove >>")
                    sys.exit(1)
                upk_pkg.deletePackage(sys.argv[2], root)
            case 'install-local':
                root = "/"
                if len(sys.argv) > 3:
                    root = sys.argv[3]
                if len(sys.argv) < 2:
                    echo("error: missing arguments for << upk install-local >>")
                    sys.exit(1)
                upk_pkg.installPackage(sys.argv[2], root)
            case 'build':
                if len(sys.argv) < 3:
                    echo("error: missing arguments for << upk build >>")
                    sys.exit(1)
                o = None
                if len(sys.argv) > 3:
                    o = sys.argv[3]
                upk_utils.compress(sys.argv[2], o)  
            case 'version':
                echo(f"upk-ng ver {version}")
                echo(f"release {rel} by {maintainer}")      
            case _:
                echo(f"invalid command {sys.argv[1]}, view << upk help >> for more information")
    except Exception as e:
            echo(e)
            sys.exit(1)