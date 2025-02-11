import upk_data,upk_pkg,upk_utils,sys 
from upk_utils import echo
if __name__ == "__main__":
    rel = 1
    ver = "0.1"
    if len(sys.argv) < 1:
        echo("error: usage: << upk [command] >>")
        sys.exit(1)
    match sys.argv[1]:
        case 'help':
            echo("upk-ng")
            echo("next generation upk package manager")
            echo("release {rel}, version {ver}")
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

        case _:
            echo(f"invalid command: {sys.argv[1]}, view << upk help >> for more information")
        