# Required work environment for the Docker Workshop
1. Editor with support for Dockerfile and YAML (e.g. Emacs, VIM, vs-code, ...)
  - check that indentation is working
  - check that syntax highlighting is working
2. Docker (on Linux) or Docker Desktop (on Windows and Mac OSX)
3. Comfortable terminal for issuing commands and experimenting, e.g.:
  - urxvt/xterm/gnome-terminal on Linux
  - iterm2 on OSX
  - Windows Terminal on Windows

The workshop will be editor and terminal independent, so just bring
something you are comfortable with, if you are not comfortable with
anything, please ask around for help, I myself use Emacs, but no time
on the workshop to teach or show that config.

# Detailed instructions for Docker
Some of you might already have Docker installed, so let's test if it
works well enough for the workshop!

(For people with no Docker installed yet, you will find installation
instructions below, and you can come back to testing later.)

## Testing
Your install has to be able to pull containers from the internet and
run them in the command line on your own laptop.  To test if the
installation is correct, run this command in a terminal:

```
docker run -it --rm nilcons/debian /bin/bash -c 'echo $(hostname) $(uname -m) hello lecturers'
```

For me, this is printed:

```
8d8918c50593 x86_64 hello lecturers
```

The ID at the beginning will be completely random (and change with
every re-run), while `x86_64` will match your machine architecture,
with newer Macs it will be `aarch64`.

The next thing we will test is the network setup for Docker, run this:

```
docker run -p 7612:9898 -it --rm stefanprodan/podinfo
```

While the command is running in the terminal window, open your browser
and go to [http://localhost:7612/](http://localhost:7612/).

You should see a purple octopus and the message "greetings from
podinfo" with some version number (v6.9.2 at the time of writing this
document).  Once you finished testing, you can Ctrl-C the `docker run`
command in the terminal window (and this will also stop the webserver,
and you will no longer see the octopus if you reload).

## Docker installation on Linux
If you have a Debian/Ubuntu based installation, most likely you can
install docker with these commands:

```
apt update
apt install docker.io
```

After the installation has finished, restart your machine and go to
the testing section above.

## Docker Desktop installation on OSX
The easiest way to install stuff on OSX, is to have the brew package
manager installed.

You can see if brew installed with the command `brew doctor`.  This
should print `Your system is ready to brew.`, if brew is already
installed.

If brew is not installed yet, you can use this command for the
installation (in a terminal window):

```
/usr/bin/ruby -e "$(curl -fsSL https://raw.github.com/Homebrew/install/HEAD/install)"
```

Once brew is installed, you can install docker with:

```
brew install --cask docker
```

After a restart, you can start Docker Desktop from the Applications in
OSX, and you will have to do this after every restart.  Once Docker
Desktop is running, go back to the testing chapter, and make sure that
it's fully functional.

## Docker Desktop installation on Windows
For windows installation of Docker Desktop, find information here:
[https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)

The recommended configuration is with the WSL2 backend.

Please prepare your installation before the workshop, run the testing
commands above and ask for help, if your Windows based Docker Desktop
installation is not functional.
