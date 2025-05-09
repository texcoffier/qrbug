# QRBug

[🇫🇷 Français](https://github.com/texcoffier/qrbug/blob/main/README_FR.md)

QRBug is a software made to allow users to report any failures or incidents on any equipment using simple QR Codes.  
The software was originally made for the University Claude Bernard Lyon 1.

## Install
First, install Python version 3.10 or higher *(we recommend Python 3.12)*.  
Then, clone or download this repo to a local folder.

### Linux
There is an install script for Linux users : `./install.sh`  
Run it, and you will be good to go.

### Windows/macOS
First, ensure that the Python executable is in your system PATH.  

Create a new virtual environment at the root of the repo.  
To do this, make sure you have `pip` installed.

Run `pip install virtualenv` to make sure you can install virtual environments.

Then, create the virtual environment by running `python3 -m venv .venv`.

Activate the newly created virtual environment :  
On **macOS** : `source .venv/bin/activate`  
On **Windows** : `.venv\Scripts\activate`

Finally, install the software and all its dependencies into the virtual environment :  
```bash
python3 -m pip install -e .
```

## Tests
To make sure all tests pass, you can run the `test.sh` file on Linux or the command `python -m unittest` on other operating systems.

## Running
To start the server, run the following command :
```bash
python -m aiohttp.web -H "<IP>" -P "<PORT>" qrbug.server:init_server
```
Of course, replace `<IP>` and `<PORT>` with the corresponding values.  
If you are unsure of what to put there, replace `<IP>` with `localhost` and `<PORT>` with `8080`.
