# Developer Environment Set-Up

## Preparation
The environment works best in Ubuntu

1. Install ubuntu
2. Use the ubuntu package manager (snap) to install vsCode and pyCharm
3. Install git using apt
   > sudo apt install git
4. use "ssh-keygen" to generate your key
   > ssh-keygen
5. Register your key in github (your public key is under ~/.ssh/id_rsa.pub)
6. Install docker-engine: https://docs.docker.com/engine/install/ubuntu/
7. Add yourself to the docker group:
   > sudo usermod -aG docker $USER
   
   > > > > <h3>You have to restart for it to take effect !!! </h3>
8. Install docker-compose
   > sudo apt install docker-compose
9. Install brew 

   > /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

```   
   test -d ~/.linuxbrew && eval "$(~/.linuxbrew/bin/brew shellenv)"
   test -d /home/linuxbrew/.linuxbrew && eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
   test -r ~/.bash_profile && echo "eval \"\$($(brew --prefix)/bin/brew shellenv)\"" >>~/.bash_profile
   echo "eval \"\$($(brew --prefix)/bin/brew shellenv)\"" >>~/.profile
   echo "eval \"\$($(brew --prefix)/bin/brew shellenv)\"" >>~/.bashrc
```

   Note: when you use brew you may get the following error:  "Too many open files @ rb_sysopen". If that happens you can run this command before running brew:
   > ulimit -n 8192

10. install pyenv
   > brew install pyenv

   Load pyenv automatically by appending the following to ~/.bash_profile if it exists, otherwise ~/.profile (for login shells) and ~/.bashrc (for interactive shells):

   > export PYENV_ROOT="$HOME/.pyenv"\
   > command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"\
   > eval "$(pyenv init -)"

   Restart your shell for the changes to take effect.

11. install python 3.10
   > sudo apt install build-essential zlib1g-dev libssl-dev libffi-dev libbz2-dev libreadline-dev libsqlite3-dev liblzma-dev libbz2-dev

   > wget http://nz2.archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.16_amd64.deb

   > sudo dpkg -i libssl1.1_1.1.1f-1ubuntu2.16_amd64.deb
   
   > brew install gcc@11 

   > pyenv install 3.10
   
   > pyenv global 3.10   

   > pip install virtualenv


## Project set-up
1. Clone this repository (remember to use the SSH version)
   > git clone --recursive [PROJECT PATH]
2. Go into the project directory
3. Create and activate the virtualenv
   > python -m venv .venv
   > source .venv/bin/activate
4. Install project dependencies on the terminal of pycharm.
   > ./install_deps.sh
5. Run tests to validate the project works
   > python -m unittest

** The tests run with mongo inmemory - no need to set up mongo   

6. You can also run the tests by right clicking the "tests" package and selecting "Run tests"

## Runtime env set-up

1. Make sure your docker engine is up using "docker version" command
   > docker  version
2. on the project home folder, go to the "deploy" directory and run the following command:
   > ./build_and_run.sh
** IMPORTANT: Make sure to run all projects tests and check after this, as many dependencies may change during the process

** If ther is an issue with the some packages, try to purge the pip cache first:
> pip cache purge
