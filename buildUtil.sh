#!/bin/bash
set -e

checkProgram() {
    if ! command -v "$1" &>/dev/null; then
        echo "program $1 not found"
        exit 1
    fi
    echo $(command -v "$1")
}
buildwithNuitka() {
    python=$(checkProgram "python3" || checkProgram "python" || checkProgram "py")
    nuitka=$(checkProgram "nuitka")
    srcdir=$(pwd)/src
    main="upk.py"
    echo "starting to build upk-ng"
    if ! [ -d "$(pwd)/output" ]; then
        mkdir -p "$(pwd)/output"
    fi
    echo "building with nuitka..."
    $nuitka --follow-imports --standalone --output-dir="$(pwd)/output" --onefile "$srcdir/$main"
    mv output/upk.bin output/upk
    echo "upk executable ready on output/upk"
}
packageUpk() {
    python=$(checkProgram "python3" || checkProgram "python" || checkProgram "py")
    upkbin="$(pwd)/output/upk"
    if ! [ -f "$upkbin" ]; then
        echo "please build with <<$0 build>> and then try again"
        exit 1
    fi
    echo "creating proper directories"
    mkdir -p $(pwd)/package
    mkdir -p $(pwd)/package/{UPK,usr/bin}
    echo "writting a manifest"
    rm -f $(pwd)/package/UPK/info.json
    cat << EOF > $(pwd)/package/UPK/info.json
{
    "name": "upk-ng",
    "version": "$1",
    "maintainer": "$2",
    "summary": "unnamed package manager - next generation"
}

EOF
    echo "packaging upk-ng"
    cp -r "$upkbin" "$(pwd)/package/usr/bin"
    "$upkbin" "build" "$(pwd)/package"


}
ver="0.1"

case "$1" in
    "build")
        buildwithNuitka
    ;;
    "package")
    
        if [ -z "$2" ]; then
            version="git-$(git rev-parse HEAD)"
        else 
            version="$2"
        fi
        if [ -z "$3" ]; then
            maintainer="juanvel400"
        else 
            maintainer="manual:$3"
        fi
        packageUpk "$version" "$maintainer"
    ;;
    "help")
        echo "usage: $0 [options]"
        echo "upk-ng build utility"
        echo " options:"
        echo "   help                        - show this message"
        echo "   build                       - use nuitka to build a standalone binary in the output/ folder"
        echo "   package <ver> <maintainer>  - create a upk-ng package you can later install with upk" 
        echo "   clean                       - clean output/ (warning: this may slow the next build)"
        echo "upk-ng buildutil $ver"
    ;;
    "clean")
        echo "cleaning up..."
        if [ -d "$(pwd)/output" ]; then
            rm -rv "$(pwd)/output/*" >> "cleanLog"
            read -rp "do you want to see the deleted files? [y/N] " willview
            case "$willview" in
                Yy)
                    cat cleanLog
                    rm cleanLog
                    exit 0
                ;;
                *)
                    rm cleanLog
                    exit 0
                ;;
            esac
        else
            echo "output directory does not exist."
            exit 1
        fi
    ;;
    *)
        echo "usage: $0 [build|help|clean|package]"
        exit 1
    ;;
esac
