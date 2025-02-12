
# upk-ng

**u**nnamed **p**ac**k**age manager **-** **n**ext **g**eneration, a simple package manager written in python


## features

- **databases**: uses sqlite3
- **packages**: compressed with .tar.xz, lossless and better packages
- **simple**: built with simplicity in mind
- **python**: built in python


## building
upk-ng **buildUtil** is a simple script written for easy compilation/packaging of the **upk-ng** package manager
make sure you have the dependencies to use **buildUtil**

### dependencies
- **nuitka**: required for compiling the package, install with `pip`
- **python**: required for nuitka and the package itself
- **bash**: for running buildUtil
- **ccache**, **distcc**: optional for speeding the compilation times

### compilation
1. compile using buildUtil

~~~bash
./buildUtil.sh build <version> <release> <maintainer>
~~~
**tip**: you can put your own version, release and maintainer, probably you already noticed it

_this will compile **upk-ng** to the **output/** directory_

2. package the build
you should put in `version` and `maintainer` the same you put in the first step
~~~bash
./buildUtil.sh package <version> <maintainer>
~~~

3. bootstrap the package
install it to your system, or to a different root using the compiled upk from **output/**, as root
~~~
./output/upk install-local ./upk-ng-<version>.upk <root>
~~~
_**<root>** is optional_

## installation

bootstrap the precompiled upk from the main repo (run all commands as root)
~~~
python ./src/upk.py addrepo main https://juanvel4000.serv00.net/upk-ng/main
python ./src/upk.py update
python ./src/upk.py install upk-ng
~~~

## stools

**upk**-**s**erver**tools** is a repository manager written in python, it is an easy way to manage **Release** files if you maintain a repository


### installation

ensure you have the **main** repository (as root)
~~~
upk addrepo main https://juanvel4000.serv00.net/upk-ng/main
upk update
~~~
install the stools package
~~~
upk install stools
~~~