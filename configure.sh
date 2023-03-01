#!/bin/bash
#############
# CONSTANTS #
#############
# Colour constants
RED='\033[0;31m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BOLD='\u001b[1m'
NC='\033[0m' # No colour

# Script constants
VENV_ACT=".venv/bin/activate"
PIP_REQS="requirements.txt"
PYTHON_DEPS="python3.10 python3.10-venv python3-pip"
EXT_DEPS="git nasm"

#############
# FUNCTIONS #
#############
function activate_env() {
    if source $VENV_ACT; then
        echo -e "${GREEN}Virtual environment activation successful!${NC}"
    else
        echo -e "${RED}Activating the virtual environment failed.${NC}"
        exit 1
    fi
}

function install_pip_reqs() {
    if [ ! -f $PIP_REQS ]; then
        # If the reqs file doesn't exist then nothing can be done.
        echo -e "${RED}$PIP_REQS not found, cannot install dependencies.${NC}"
        exit 1
    fi

    # Install pip packages from REQS file
    if [ -z $1 ]; then
        echo -e "${BLUE}Installing pip package requirements...${NC}"
        pip install -r $PIP_REQS
    else
        echo -e "${BLUE}Checking pip package requirements...${NC}"
        pip install -r $PIP_REQS > /dev/null
    fi

    if [ ! $? -eq 0 ] ; then
        # Some of the pip packages failed to install, things may still work but its
        # probably best to send an error
        echo -e "${RED}Pip failed to install some packages.${NC}"
        exit 1
    else
        echo -e "${GREEN}Installed successfully!${NC}"
    fi
}

########
# MAIN #
########
# Ensure that python3, pip3, and venv are installed
echo -e "${BLUE}Checking for python dependencies...${NC}"
dpkg -s $PYTHON_DEPS > /dev/null
if [ ! $? -eq 0 ]; then
    echo -e "${YELLOW}Not found, trying to install one (or more) of $PYTHON_DEPS.${NC}"
    apt-get install $PYTHON_DEPS -y
else
    echo -e "${GREEN}Found!${NC}"
fi

# Ensure that other dependcies are installed
echo -e "${BLUE}Checking for external dependencies...${NC}"
dpkg -s $EXT_DEPS > /dev/null
if [ ! $? -eq 0 ]; then
    echo -e "${YELLOW}Not found, trying to install one (or more) of $EXT_DEPS.${NC}"
    apt-get install $EXT_DEPS -y
else
    echo -e "${GREEN}Found!${NC}"
fi

# Check for the virtual environment
echo -e "${BLUE}Looking for virtual environment...${NC}"
if [ -f $VENV_ACT ]; then
    echo -e "${GREEN}Found!${NC}"

    # We already have a venv, so just activate it
    activate_env

    # Check for new pip packages by installing pip deps, using the requirements.txt file
    install_pip_reqs true

else
    # The virtual environment was not found so we need to make one and install the packages.
    echo -e "${YELLOW}Couldn't find virtual environment, creating it now...${NC}"
    mkdir .venv
    python3 -m venv .venv
    export PATH=$PWD/.venv/bin/:$PATH

    if [ ! -f $VENV_ACT ]; then
        # We failed to create the venv, so all hope is lost
        echo -e "${RED}Failed to create new virtual environment.${NC}"
        exit 1
    else
        echo -e "${GREEN}Environment created!${NC}"
    fi

    # Activate the newly-create virtual environment.
    activate_env

    # Install the pip dependencies, using the requirements.txt file
    install_pip_reqs

    pre-commit install
fi

echo -e "${BOLD}Makka Pakka Activated${NC}"
