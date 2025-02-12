#!/bin/bash
set -e
checkProgram() {
    command -v "$1" &>/dev/null || { echo "program $1 not found"; exit 1; }
    command -v "$1"
}

buildwithNuitka() {
    echo "checking programs"
    echo "checking python3"
    python=$(checkProgram "python3" || checkProgram "python" || checkProgram "py")
    echo "found python3"
    echo "checking nuitka"
    nuitka=$(checkProgram "nuitka")
    echo "found nuitka"
    echo "checking source"
    srcdir=$(pwd)/src
    main="upk.py"
    outputdir="$(pwd)/output"
    cat << EOF > $srcdir/upk_info.py
# upk information file autogenerated by buildutil
rel = "$2"
version = "$1"
maintainer = "$3"
EOF
    echo "starting to build upk-ng"
    
    mkdir -p "$(pwd)/output"
    echo "building with nuitka..."
    $nuitka  --standalone --output-dir="$outputdir" --onefile "$srcdir/$main"
    mv output/upk.bin output/upk
    echo "upk executable ready at output/upk"
}

packageUpk() {
    python=$(checkProgram "python3" || checkProgram "python" || checkProgram "py")
    upkbin="$(pwd)/output/upk"
    if [ ! -f "$upkbin" ]; then
        echo "please build with <<$0 build>> and then try again"
        exit 1
    fi
    
    echo "creating proper directories"
    mkdir -p "$(pwd)/package/UPK"
    mkdir -p "$(pwd)/package/usr/bin"
    
    echo "writing a manifest"
    rm -f "$(pwd)/package/UPK/info.json"
    cat << EOF > "$(pwd)/package/UPK/info.json"
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
        version="${2:-git-$(git rev-parse HEAD):-custom}"
        maintainer="${3:-$(git config --global user.name):-John Doe}"
        rel="${4:-$(git rev-parse --abbrev-ref HEAD):-Custom}"
        buildwithNuitka "$version" "$rel" "$maintainer"
    ;;
    "package")
        version="${2:-git-$(git rev-parse HEAD):-custom}"
        maintainer="${3:-$(git config --global user.name):-John Doe}"
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
            read -rp "Do you want to see the deleted files? [y/N] " willview
            case "$willview" in
                [Yy]) cat cleanLog && rm cleanLog ;;
                *) rm cleanLog ;;
            esac
            echo "cleaned output directory"
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
