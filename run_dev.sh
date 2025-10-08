#!/bin/bash

# This script runs the latest versions of the code in development mode.
# It will also download correct versions of NPM and UV if they are not
# installed on the system.

NODE_VERSION="${WT_NODE_VERSION:-v22.20.0}"
UV_VERSION="${WT_UV_VERSION:-0.8.24}"
TOOLS_DIR="${WT_TOOLS_DIR:-.tools}"

function usage() {
    echo "Run the web tool in developer mode."
    echo "usage:"
    echo "  ./run_dev.sh [-h,--help] [--uv-version UV_VERSION] [--node-version NODE_VERSION] [--tools-dir TOOLS_DIR] [--print-export]"
    echo
    echo "Options:"
    echo "  --uv-version     set the version of UV (default $UV_VERSION)"
    echo "  --node-version   set the version of Node (default $NODE_VERSION)"
    echo "  --tools-dir      set the location for build tools (default $TOOLS_DIR)"
    echo "  --print-export   prints the export command to set the PATH variable to use"
    echo "                   the local versions of build tools"
    echo "  -h,--help        prints this message"
    echo ""
    echo "Environment variables:"
    echo "  WT_UV_VERSION    set the default version of UV"
    echo "  WT_NODE_VERSION  set the default version of Node"
    echo "  WT_TOOLS_DIR     set the default location for build tools"
}

function exit_failure() {
    ## Print a message and exit from the script.
    echo "$@"
    exit 1
}

function parse_args() {
    ## Parse command line arguments
    PRINT_EXPORT=1
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit
                ;;
            --uv-version)
                UV_VERSION=$2
                shift;
                shift;
                ;;
            --node-version)
                NODE_VERSION=$2
                shift;
                shift;
                ;;
            --tools-dir)
                TOOLS_DIR=$2
                shift;
                shift;
                ;;
            --print-export)
                PRINT_EXPORT=0
                shift;
                ;;
            *)
                exit_failure "Invalid argument: $1"
        esac
    done

    # Update variables that could have been overridden by command line arguments.
    UV_DIR="${TOOLS_DIR}/uv/${UV_VERSION}"
    NODE_PARENT_DIR="${TOOLS_DIR}/node"
    NODE_DIR="${NODE_PARENT_DIR}/node-${NODE_VERSION}-linux-x64/bin"
    
    if [[ $PRINT_EXPORT -eq 0 ]]; then
        echo "export PATH=\"${PWD}/${UV_DIR}:${PWD}/${NODE_DIR}:\${PATH}\""
        exit 0
    fi

    PATH="${UV_DIR}:${NODE_DIR}:${PATH}"
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


    NODE_URL="https://nodejs.org/dist"
    DIR_NAME="node-${NODE_VERSION}-linux-x64"
    TAR_NAME="${DIR_NAME}.tar.xz"
    DOWNLOAD_URL="${NODE_URL}/${NODE_VERSION}/${TAR_NAME}"

    echo "Downloading: ${DOWNLOAD_URL}"

    wget ${DOWNLOAD_URL} \
        || exit_failure "Could not download node ${NODE_VERSION}. Make sure that version is still available at ${NODE_URL}"
    tar xf ${TAR_NAME} \
        || exit_failure "Could not extract archive ${TAR_NAME}"

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

function source_env_vars() {
    ## Load possible scripts containing environment variables
    if [ -f env_vars ]; then
        source env_vars
    else
        echo "Environment variables file 'env_vars' does not exist."
    fi

    if [[ -z "$DATA_REPO_GITHUB_TOKEN" ]]; then
        exit_failure "DATA_REPO_GITHUB_TOKEN is not set. See the README for details: https://github.com/SCSDMWT/climate_scenario_web_tool?tab=readme-ov-file#data  "
    fi
}

function compile_js() {
    ## Compile the JavaScript code
    cd scotclimpact/static

    ## Install JS depenancies
    if [[ ! -d "node_modules" ]]; then
        npm install || exit_failure "Could not download JavaScript dependencies."
    fi

    ## Compile JS code
    if [[ ! -f "dist/main.js" || "src/main.js" -nt "dist/main.js" ]]; then
        npm run build || exit_failure "Could not compile JavaScript code."
    fi
    cd -
}

function run_flask() {
    ## Run the Flask app
    uv run -- flask --app scotclimpact run -p 8000
}


function main() {
    # Set environment variables
    source_env_vars
    parse_args "$@"

    # Install tools
    install_uv
    install_node

    # Update JS code
    compile_js

    # Run the web app
    run_flask
}

main "$@" || exit 1
