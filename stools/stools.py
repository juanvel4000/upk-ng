import os, configparser, paramiko, getpass, sys
from scp import SCPClient

if os.path.isfile('stools_info.py'):
    from stools_info import version, rel
else:
    version, rel = "0.0", "1"

def echo(m, l=1, ks="-", ke=">", n=True):
    print(ks * l, end="")
    print(f"{ke} {m.lower()}", end="\n" if n else "")

class Repository:
    def __init__(self, folder):
        self.folder = folder
        for i in [folder, f'{folder}/pool', f'{folder}/sums']:
            os.makedirs(i, exist_ok=True)
        self.sshStatus = False

    def addpackage(self, name, version, arch):
        for ext in ['upk', 'sha256']:
            old_path = f'{self.folder}/pool/{name}-{version}.{ext}'
            new_path = f'{self.folder}/pool/{name}-{version}-{arch}.{ext}'
            if os.path.isfile(old_path):
                os.rename(old_path, new_path)

        with open(f'{self.folder}/Release', 'r+') as release:
            lines = release.readlines()
            highestid = max([int(i.strip().split('=>')[3]) for i in lines], default=0)
            newId = highestid + 1
            release.write(f'{name}=>{version}=>{arch}=>{newId}\n')

        echo(f"added {name} {version}-{arch} with id {newId}")

    def delPackage(self, name):
        with open(f'{self.folder}/Release', 'r') as rel:
            lines = [i.strip().split('=>') for i in rel.readlines() if i.strip().split('=>')[0].lower() != name.lower()]
        with open(f'{self.folder}/Release', 'w') as newrel:
            for idx, pkg in enumerate(lines, 1):
                newrel.write(f'{pkg[0]}=>{pkg[1]}=>{pkg[2]}=>{idx}\n')
        echo(f"package {name} removed successfully.")

if __name__ == "__main__":
    print(f"upk-stools {version}-{rel}: easy to use repository helper")
    print("=============================================")
    config_path = os.path.join(os.path.expanduser('~'), '.stools.env')

    if os.path.isfile(config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        if not config.has_section('stools'):
            sys.exit(1)
        folder = config['stools']['folder']
    else:
        while True:
            folder = input("repository folder: ").strip()
            if os.path.isdir(folder):
                break
            if folder.lower() == "stools.exit":
                sys.exit(0)
            print("invalid folder. please try again.")

    repo = Repository(folder)

    while True:
        print("what do you want to do?")
        os.makedirs(f'{folder}/pool', exist_ok=True)
        os.makedirs(f'{folder}/sums', exist_ok=True)
        open(f'{folder}/Release', 'a').write('\r').close() # carriage return because i ensured it would always break line
        print("a: add a package")
        print("d: delete a package")
        print("q: quit\n")
        option = input("your selection: ").lower()

        if option == 'a':
            repo.addpackage(input("package name: ").strip(), input("package version: ").strip(), input("package architecture: ").strip())
        elif option == 'd':
            repo.delPackage(input("package to delete: ").strip())
        elif option == 'q':
            sys.exit(1)
        else:
            print("unknown action. please try again.")
