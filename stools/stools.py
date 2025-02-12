import os
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

    def addpackage(self, name, version, arch):
        if os.path.isfile(f'{self.folder}/pool/{name}-{version}.upk'):
            os.rename(f'{self.folder}/pool/{name}-{version}.upk', f'{self.folder}/pool/{name}-{version}-{arch}.upk')
        if os.path.isfile(f'{self.folder}/sums/{name}-{version}.sha256'):
            os.rename(f'{self.folder}/sums/{name}-{version}.sha256', f'{self.folder}/sums/{name}-{version}-{arch}.sha256')

        with open(f'{self.folder}/Release', 'r') as release:
            lines = release.readlines()
            highestid = 0
            for i in lines:
                pkgId = int(i.strip().split('=>')[3])  
                if pkgId > highestid:
                    highestid = pkgId
            newId = highestid + 1

        with open(f'{self.folder}/Release', 'a') as rel:
            rel.write(f'{name}=>{version}=>{arch}=>{newId}\n')

        echo(f"added {name} {version}-{arch} with id {newId}")
        return True

    def delPackage(self, name):
        os.rename(f'{self.folder}/Release', f'{self.folder}/Release.bak')
        with open(f'{self.folder}/Release.bak', 'r') as rel:
            lines = rel.readlines()
        
        with open(f'{self.folder}/Release', 'w') as newrel:
            currentId = 1
            for i in lines:
                pkg = i.strip().split('=>')
                if pkg[0].lower() == name.lower(): 
                    continue
                newrel.write(f'{pkg[0]}=>{pkg[1]}=>{pkg[2]}=>{currentId}\n')
                currentId += 1
        
        echo(f"package {name} removed successfully.")
        return True


if __name__ == "__main__":
    print(f"upk-stools {version}-{rel}: easy to use repository helper")
    print("=============================================")
    print("enter your folder containing the repository: (enter stools.exit to exit)")
    
    while True:
        folder = input("repository folder: ").lower()  
        if os.path.isdir(folder): 
            break
        if folder == "stools.exit":
            exit(0)
        print("\ninvalid folder. please try again.")

    repo = Repository(folder)

    while True:
        print("\nwhat do you want to do?")
        print("1. add a package")
        print("2. delete a package")
        print("3. quit")
        option = input("your selection: ").lower()  

        if option == '1':
            name = input("package name: ").lower()  
            ver = input("package version: ").lower() 
            arch = input("package architecture: ").lower()  
            repo.addpackage(name, ver, arch)

        elif option == '2':
            name = input("package to delete: ").lower() 
            repo.delPackage(name)

        elif option == '3':
            print("exiting...")
            exit(0)

        else:
            print("unknown action. please try again.")
            continue
