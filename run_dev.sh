#!/bin/bash

# This script runs the latest versions of the code in development mode.
# It will download correct versions of NPM and UV if they are not present.

#NODE_VERSION=v24.9.0
NODE_VERSION=v22.20.0
UV_VERSION=0.8.24
TOOLS_DIR=.tools
UV_DIR="${TOOLS_DIR}/uv/${UV_VERSION}"
NODE_PARENT_DIR="${TOOLS_DIR}/node"
NODE_DIR="${NODE_PARENT_DIR}/node-${NODE_VERSION}-linux-x64/bin"

PATH="${UV_DIR}:${NODE_DIR}:${PATH}"

function usage() {
    echo "Run the web tool in developer mode."
    echo "usage:"
    echo "  ./run_dev.sh [-h,--help]"
    echo
    echo "Options:"
    echo "  -h,--help     prints this message"
}

function parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit
                ;;
            *)
                echo "Invalid argument: $1"
                exit 1
        esac
    done
}


function check_version() {
    ## Checks if a program ($1) exists and that the version matches $2.
    ## Usage:
    ##   check_version PROG PROG_VERSION

    PROG=$1
    PROG_VERSION=$2

    WHICH=$(which $PROG)
    if [[ -z "${WHICH}" ]]; then
        echo "no ${PROG}"
        return 1
    else
        echo "Found ${PROG}:"
        echo "  ${WHICH}"
    fi

    FOUND_VERSION=$(${WHICH} --version)
    echo "  version: ${FOUND_VERSION}"

    if [[ -z $(echo "${FOUND_VERSION}" | grep "${PROG_VERSION}") ]]; then
        echo "${PROG} incorrect version expected: ${PROG_VERSION}"
        return 1
    fi
}

function check_node_version() {
    check_version node $NODE_VERSION
}

function install_node() {
    if check_node_version; then
        return
    fi

    mkdir -p $NODE_PARENT_DIR
    cd $NODE_PARENT_DIR


    DIR_NAME="node-${NODE_VERSION}-linux-x64"
    TAR_NAME="${DIR_NAME}.tar.xz"
    DOWNLOAD_URL="https://nodejs.org/dist/${NODE_VERSION}/${TAR_NAME}"

    echo "Downloading: ${DOWNLOAD_URL}"

    wget ${DOWNLOAD_URL} || exit 1
    tar xf ${TAR_NAME} || exit 1

    cd -
}

function check_uv_version() {
    check_version uv $UV_VERSION
}

function install_uv() {
    # Skip this step if the expected version uv is already installed
    
    if check_uv_version; then
        return
    fi

    ## Install uv to $UV_DIR using their installation script. 
    ## See https://docs.astral.sh/uv/reference/installer/ for details. 
    curl -LsSf https://astral.sh/uv/${UV_VERSION}/install.sh \
        | env UV_INSTALL_DIR="${UV_DIR}" UV_NO_MODIFY_PATH=1 sh
}

## Load possible scripts containing environment variables
if [ -f .dev-env ]; then
    source .dev-env
fi

if [ -f env_vars ]; then
    source env_vars
fi

## TODO check if GIT_DATA_REPO_TOKEN exists

function compile_js() {
    ## Compile the JavaScript code
    cd scotclimpact/static

    ## Install JS depenancies
    if [[ ! -d "node_modules" ]]; then
        npm install || exit 1
    fi

    ## Compile JS code
    if [[ ! -f "dist/main.js" || "src/main.js" -nt "dist/main.js" ]]; then
        npm run build || exit 1
    fi
    cd -
}

function run_flask() {
    ## Run the Flask app
    uv run -- flask --app scotclimpact run -p 8000
}


function main() {
    parse_args "$@"

    install_uv
    install_node

    compile_js

    run_flask
}

main "$@" || exit 1
