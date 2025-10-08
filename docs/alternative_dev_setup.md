# Alternative development setups

> [!NOTE]
> This document was moved from the README and has largely been superceded by the `run_dev.sh`
> script. It describes alternative ways to manage Python and JavaScript dependancies and should
> only be used if the `run_dev.sh` script in not suitable for your workflow or system.

> [!WARN]
> This section interleaves advice on uv, conda and venv, but assumes that you will pick one
> one option, stick with it and won't mix advice between the three tools.

  * [Additional Software](#additional-software)
    * [Install NPM](#install-npm)
    * [Install UV](#install-uv)
    * [Install Conda](#install-conda)
  * [Extra Initial Setup](#extra-initial-setup)
    * [Setup a Python virtual environment](#setup-a-python-virtual-environment)
      * [UV](#uv)
      * [Python venv/virtualenv](#python-venvvirtualenv)
      * [Conda](#conda)
    * [Initialise the NPM project](#initialise-the-npm-project)
    * [Run the web app locally](#run-the-web-app-locally)
  * [New Sessions 2](#new-sessions-2)
  * [Working on the code](#working-on-the-code)
    * [Python](#python)
    * [JavaScript](#javascript)
    * [Running the latest code](#running-the-latest-code)


## Additional Software
### Install NPM

NPM can be installed without root access with the following steps:

 * Go to [nodejs.org/en/download/](https://nodejs.org/en/download/). 
 * Selected the latest version from the first drop down
 * Click the green 'Standalone Binary (.xz)' button
 * Extract the tarball
 * Add the `bin` directory to the `PATH` variable:
   ```bash
   export PATH=/full/path/to/node/bin:$PATH
   ```

### Install UV

UV can be installed without root privileges by following the instructions
at [docs.astral.sh](https://docs.astral.sh/uv/getting-started/installation/).

### Install Conda

Follow the installation instructions on the [conda web site](https://docs.conda.io/projects/conda/en/stable/user-guide/install/linux.html).

### Setup a Python virtual environment

It is recommended to keep the Python dependencies for the project in a separate environment.
This can be done with (at least) three software packages.
Any one of the following three will do the job, however UV is much more convenient to use.
If UV is not available, Python venv/virtualenv should be considered before Conda environments,
unless the system installed version of Python is too old.

#### UV

UV creates temporary environments whenever a Python script or program is run using `uv run`.
If `uv` is installed, no additional setup is needed at this stage.

#### Python venv/virtualenv

Python has a builtin mechanism for creating virtual environments, however it uses the
Python installation of the operating system. If the version is recent enough, a
virtual environment can be created with:
```bash
python -m venv .venv
. .venv/bin/activate
pip install .
```

#### Conda

Conda is a popular package manager and can install recent versions of Python without root permissions.
A conda environment can be created with:
```bash
conda create -n scotclimpact python=3.13.0
conda activate scotclimpact
pip install .
```


### Initialise the NPM project

JavaScript dependencies need to be downloaded and the code compiled to a browser
supported format with:
```bash
cd scotclimpact/static
npm install
npm run build
cd -
```

### Run the web app locally

When using UV, the following command will download all Python dependencies and run the web app:
```bash
uv run -- flask --app scotclimpact run -p 8000
```

With conda and a virtual environment, the web app can be started with:
```bash
flask --app scotclimpact run -p 8000
```
The web app should be running and available at [http://localhost:8000](http://localhost:8000).

## New sessions 2

In addition to sourcing `env_vars`, conda or virtual environments should be reactivated 
in new terminal sessions. If using conda:
```bash
conda activate scotclimpact
```
For venv/virtualenv:
```bash
. .venv/bin/activate
```

## Working on the code

Changes to the Python code might require additional steps to run, depending on how the Python environment
is managed. Changes to the JavaScript code should be recompiled too.

### Python

With UV no extra steps are needed when changing the Python code, but conda and virtual environments
might need the following to install the updated code in the environment:
```
pip install .
```

### JavaScript

Changes to `scotclimpact/static/src/` should be compiled with
```bash
cd scotclimpact/static
npm run build
cd -
```

### Running the latest code

Running the web app with the latest changes is the same as [run the web app locally](#run-the-web-app-locally) above.

