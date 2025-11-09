# Etherpad

https://etherpad.inf.ethz.ch/p/cx-docker-workshop

# Linux containers intro
Goal of containers: give similar security and feel to VMs with much lower cost.

OS level virtualization: all implemented in the kernel (Linux), around the usual APIs (file access, networking, cpu scheduling, etc.).

No hardware support needed on the CPU.

Advanteges (compared to VMs):
  - hardware independent (supported on weird architectures, e.g. arm64)
  - very fast (startup time in milliseconds)
  - low memory footprint (no extra booted kernel, systemd, basic linux daemons, etc.)
  - file sharing trivial, no need for "network" based file sharing on virtual ethernet
  - partial containers (e.g. only virtualizing network) possible
  - virtualization transparent: host `ps -ef` shows everything

Disadvanteges (compared to VMs):
  - less secure: a kernel security issue gives full access to the host machine, no hardware boundary
  - single OS, no way to run windows apps on a linux host
  - virtualization transparent: host `ps -ef` shows everything

## Linux kernel feature #1: cgroups demo (memory and OOM)
```
sudo -i
  cd /sys/fs/cgroup
  mkdir workshop-test
  cat cgroup.procs   # empty
  echo $$ >cgroup.procs
  cat cgroup.procs   # shell and cat, ancestors are always there, better than ulimit!
  cat /proc/$$/cgroup
  echo $((100*1024*1024)) >memory.max
  echo 0 >memory.swap.max
  cat memory.peak
  cat memory.current
  tail -n1 /dev/zero
  dmesg --since -10s -T
  cat memory.peak
  cat memory.current
sudo rmdir /sys/fs/cgroup/workshop-test
```

Notes:
  - cgroups are hierarchical (we could have a second cgroup INSIDE `workshop-test`)
  - processes in cgroups inherint parent cgroupness (so can't be tricked by lot of children, unlike ulimit)
  - cgroups can be used for usage limits (max), but also for statistics (current, peak)
  - on memory overuse the same mechanism (kernel OOM killer) is used as full machine OOM

## Linux kernel feature #2: namespace demo (e.g. network isolation)
```
sudo -i
  unshare -mnupf --mount-proc /bin/bash
    hostname
    hostname test
    hostname
    ps -ef
    ifconfig -a
    ping www.inf.ethz.ch
    unshare -mnupf --mount-proc /bin/bash
      sleep 420   # exercise: how many PIDs does this sleep have? use nsenter to find out!
```

<!-- Answer: 3 PIDs on the 3 levels. -->

Notes:
  - flag `mnup`: mount, network, UTS (hostname), pid namespaces are isolated
  - flag `f`: forking new shell (needed for PID namespace)
  - flag `mount-proc`: mounting new /proc (for `ps`)
  - to make this actually useful, a lot more plumbing is needed (network virtual interfaces, disk space management, etc.)
  - this plumbing is what Docker does

# Docker
Docker is a convenient CLI interface for managing namespaces together with cgroups (and we call these combos containers).

Docker is not the only container management framework, there are others (podman, cri-o, containerd, etc.).

## Architecture (docker daemon, docker client)
![Docker architecture](images/docker-architecture.webp)

On a standard Linux workstation:

  - docker client: `docker` command line in a terminal window
  - docker host: the linux workstation itself, running the docker daemon (e.g. from systemd)
  - image registry: docker hub or any other public registry (e.g. github, google cloud, etc.)

In our case (CX):

  - docker client: the web UI on expert.ethz.ch (of course everything is graphical and students just press buttons)
  - docker host: the machines that scale out the student jobs (we call them runners)
  - image registry: cxhub.ethz.ch, operated by CX/ISG

Docker on Windows and macOS:

  - docker client: terminal window on the real host OS
  - docker host: a Linux VM managed by Windows/macOS (not really visible/accessible, but it's there, we need the Linux kernel)

In case of Windows/macOS this additional layer of Linux VM will cause some troubles, as we will see.
For now, it's enough to remember, that in some sense the native platform for Docker is Linux.

## "docker run --rm -it" for small cli experiments (e.g. shyaml)
Example: experimenting with https://github.com/0k/shyaml (part of some CX shell scripts)

```
docker run --rm -it nilcons/debian /bin/bash
  apt update
  apt install pip
  pip install --break-system-packages shyaml
  echo src: / >>/test.yaml
  echo out: /bin >>/test.yaml
  cat /test.yaml | shyaml get-value out ; echo
```

Notes:
  - once we exit the shell, the container is fully deleted, no mess on our machine
  - during the experiments the environment is secure, no risk for the host
  - can run untrusted code, and we don't have to be careful with our commands

## Long running docker containers
On servers (or if container state is important to you for longer
experiments), people of course run long-running containers, e.g.:

```
docker run --restart unless-stopped --name longrunning -d nilcons/debian sleep 120
```

Note: containers have names and IDs.  IDs are auto-generated, names
can be manually specified (but auto-generated if not specified).

### exec

Runs a secondary shell (or any other command) in a container

```
docker exec -it longrunning /bin/bash
```

### cp
`docker cp` can be used to copy files between the host and a container.

### ps and stats
Shows running containers.

To show stopped containers too: `docker ps -a`

To see memory/CPU usage: `docker stats --no-stream`

### stop (or kill)
For maintenance, e.g. on servers.

After `stop`, one can still see the container in `docker ps -a`, and use `docker cp`.

Stopping a container is backwards compatible with Linux's init:
  - TERM signal
  - 30 seconds grace period
  - KILL signal.

If prefer to kill right away, use `docker kill`

### start
If a stopped container is needed again, it can be started with `docker start`.

### rm
A container (and all its storage) can be deleted with `docker rm`, or
this is done automatically on container exit when `docker run --rm` was used.

## Exercise: inspecting a file
The image `ghcr.io/errge/docker-workshop-inspect` has a `hello.txt` file in the `/app` folder.

Can you retrieve the content of that file?

## Image management
But what are these `nilcons/debian` things that we instantiate to containers?

These are called images, think: "snapshot", containing the root filesystem of a VM.

They are stored on image servers (so called image registries), the
biggest public and default registry being https://hub.docker.com .

The real name for our image is actually `docker.io/nilcons/debian:latest`,
but the docker client defaults to the `docker.io` image registry server,
and `latest` is the default version.

### Image cache, tags, cleanup
Images are always cached locally, you can see the cache with `docker images`.

Similarly to containers, images have IDs and names (called tags).

Notes:
  - an image can have multiple tags
  - pulled images get the tag how they were pulled (e.g. `nilcons/debian`)
  - local image tags can be arbitrary strings
  - a local image can only be pushed to a registry, if they already have the correct tag

Create new tag for already exisiting image (think of it like your bookmark);

```
docker tag nilcons/debian the-one-we-used-on-the-workshop
```

Remove just one tag (and delete layers if it was the last tag):

```
docker rmi alpine/crane
```

See space usage:

```
docker system df
```

Remove intermediary untagged images (we will talk about them later):

```
docker image prune
```

Remove all unused images (no container running from them right now):

```
docker image prune -a
```

### Building our own images: Dockerfile
Empty directory with a simple `Dockerfile`:
```
FROM nilcons/debian
RUN apt-get update
RUN apt-get -y install figlet
```

Build it with: `docker build -t deb-figlet .`

After build:
  - try it out!
  - `docker image history deb-figlet`
  - `docker inspect image deb-figlet`
  - explain layers and storage tree!
  - explain and try out `CMD` and `ENTRYPOINT`
  - other important metadata stuff: `ENV`, `WORKDIR`
  - use `COPY` to have an embedded test file

### Exercise: encrypted message
Create a `Dockerfile` that inherits from `ttl.sh/docker-workshop-ethz-encrypted:24h`.

The `Dockerfile` should create the following folders:

  - `/data/folder1/`
  - `/home/ubuntu/Documents/`

There should be a file in `/home/ubuntu/Documents/message.txt` with this content:

```
rmUCPf4e7NySq91PSS8svLakkC79JkJe033KN2nr3TkPdcbmmz/bSrUatoskX5Pj78Qntd2cornRAjvF
snkgLAiNF5cElGQD2cYI7fYN7WKsfuE3pmNgSuuYJbBtSTduT/Tc1IeoV/6xycjQ1cW1A+Hz1yG2qpqI
K5k+CaGnXbMco0W1/BEjMxC6Nhf7QAtJSxpM+7s5Fb7cXpMVJuRSrQ/Briy8DNvqeD2TIiGAukvXzB9V
NNaYaClsvBPTpfNdgncae3do3FXjDXw4FltSzcm+WWp+an1YNG0fXL+/qaV2A3Xsf2Cw1fVWI7KTx+M4
M4yFDB6D0Yl8mCrk8ecxllaeF2RaPn1eRk47efQhT1z0n0zvIltvlZbXf+4f+KoCIOq3cqLoBsA3FRDA
fDEWpQ05TMxnE2Ev6C2nLMdWFLv4WD6bTp5hxlMMbPduzO7rvJ52WcEz5mOhjoCCGXneX94YvPEM4t5C
lfXRenn7mV7Wxjn1TDSH8nzWWnxWsg1ELquYxqmnmnXZ6P4zN/K1atNue28sxaoTD6uHLCFDqY5MDbHw
e8u+HtrWpwfb026b/hLcWe3JoHk0kDR+QwgO4xnpQsFjkJzljjQp0pN0V+ICmsoRgoE1O6/IB608cGtG
F8EOEgBBHExkeiyYs49/La2FqBKRu5UTZ7bHVbzblNY=
```

Let's build the image, run it, and get the decrypted message!

## Volumes
The default Docker isolation is great for experiments, but we
sometimes need exposure to the real world!

For example:
  - file sharing with host for persistent data files
  - implementing web based projects that we want to publish (on our real IP)

### host file sharing (docker run -v ./container-data:/data)
Run a container with `--rm` and host file sharing multiple times and
check that the data is persistent!

Discussion: how fast is the data synchronization between the host and
the container?

<!-- Answer (as always): it depends, it's also a trick question.

On Linux: there is no synchronization at all, so instantaneous.

On macOS/Windows: there is a sync speed, that actually can be a bottleneck.
-->

### data persistence (docker run -v my-volume:/data)
Alternative: instead of using local directories for persisting your
data, docker can take over the volume management for you.

Try it out and show `docker volume ls`

### Container vs host user
By default, processes in a container are running as root (uid 0).

What effect does this have on file permissions?

<!-- Answer: no usernames in the kernel, only UIDs, so everything
that is created in the container will be owned by root outside. -->

Can be overridden in the command line:

```
docker run -it --rm --user 1000:1000 nilcons/debian id
```

Or in a shell script (best practice pattern, can see this a lot):

```
docker run -it --rm --user `id -u`:`id -g` nilcons/debian id
```

Question: why the uid and the gid are without username inside (it's correct outside)?

<!-- Answer: no user in /etc/passwd and no group in /etc/group, username -->
<!-- and group names are a user-space concept, in the kernel there are only UID/GIDs. -->

Override can also happen in the `Dockerfile` with `USER`.

Note: can still be overridden for exec `--user 0:0`, no security
against the host, it's your computer fully if you are root on the host!

### Exercise: attention to details
Run `ttl.sh/docker-workshop-ethz-details:24h` and fix the missing details!

Running the container correctly will reveal the code to solve the challenge.

This exercise is kinda difficult in the sense, that you have to know a bit
of unix/linux too, and be creative, work in teams if you want!

## Networking
### port forward: docker run -p 3000:8080
Try it out with `stefanprodan/podinfo`.

### --network=none
Very useful for airgapping some app, you don't trust (e.g. from a clever student).

### --network=host
If you want to have the same `localhost`, and want all ports to be exposed by default.

Not a good practice, mostly for debugging, not for production, security implications.

Doesn't really work on macOS and Windows, why?

### Exercise: connecting to TCP
A container image with a TCP server is available at `ttl.sh/docker-workshop-ethz-tcp:24h`.

You should find the port of the server and send a specific payload to it to get the solution.

## docker socket mounting
Kernel namespaces and cgroup recursion is historically difficult, they
are working on it.

Clean docker in docker is therefore with restrictions (today better
than 5 years ago, but still).

Workaround: using `-v` to pass in the docker unix socket from outside,
and then a program that is running in the container can talk to docker
to start/delete/manage containers.

This provides no security, because if the app is hacked, the attacker
can create a fully privileged docker container with shell, that has
the whole host machine root directory mounted with `-v`.

In practice, this is still useful to manage dependencies of the app
with `Dockerfile`s and images.

This is what we are doing currently on our runners.

# Lunch
# Code Expert specific: Environments
Let's explore how our student sandboxes are built with docker!

## Try to hack a bit on the student UI
Go to expert.ethz.ch and load up the palindrom python sample.

Implement a solution, and try a couple of different things:
  - running
  - testing
  - asking for a repl

In the repl, one can:

```
import subprocess
subprocess.run(['bash'])
```

One can even look a bit around:
  - instead of `route` one can `cat /proc/net/route`
  - instead of `ifconfig` one can `cat /proc/net/fib_trie`
  - instead of `ps`, one can `grep -a . /proc/*/cmdline | tr '\0' ' '`
  - we can see our mounts in `/proc/mounts`

Well, no network, PID namespace is isolated, no mounts are interesting... Sad.

But how was this environment built?

## Dockerfile of the python3.11 environment
Let's start at https://gitlab.inf.ethz.ch/OU-LECTURERS/containers/cxenv/python-3_11/-/blob/main/Dockerfile?ref_type=heads

Try to build this image locally:

  - backtrack on the path formed from the `FROM` fields
  - checkout all the github repos needed
  - build from the ground up
  - look into `Dockerfile`s on the way and try to understand them (if we have time)

## Reproduce the repl locally
Now, that we have the image, let's try to run it, and we see `ACTION` is missing.

Let's do a grep in all our container source files: `grep -r provided *`

Let's read `cxenv-base-rhel8/scripts/.start` a little bit, and we see that
`ACTION` is an env var, that needs to be provided.

So we can pass this with `-e ACTION=actions` and e.g. `-e ACTIONS=repl`.

But of course `-e ACTIONS=test` still doesn't work, because we have no project.

## Reproduce run/test locally
Go to the `palindrom` subdir and:

```
docker run -v ./:/var/lib/cxrun/projectfiles -e ACTION=run -it --rm cx/cxenv/python-3_11
```

Actions defined in `conf.yml` and scripts under `scripts/`.

Reminder: file permissions are problematic, simple solution:
`sudo chown -R 601:601 .`, but remember to change it back and maybe
`sudo chmod 0777` the files that you have to edit with your editor.

For simple projects maybe it's best practice to try not to write to
`/var/lib/cxrun/projectfiles/tmp`, instead use `/tmp`.


# Bigger apps in Docker
So far we only used single containers, but microservice apps nowadays
need a lot of apps working together.

For example zulip needs all of this to function:

  - postgres
  - memcached
  - redis
  - rabbitmq
  - zulip itself

Maintaining, and starting up all of this is a lot of work, and with
big docker installations easy to lose track which rabbitmq belongs to
which app.

With docker compose, we can hold together all the parts of an
installation like this.

## Compose example
```
git clone https://github.com/zulip/docker-zulip.git
```

And look at `docker-compose.yml`

## Configure it
Register gitlab app at: https://gitlab.inf.ethz.ch/oauth/applications

- Ports to `80xx`
- `SETTING_EXTERNAL_HOST` to `<IP>:8443`
- `ZULIP_AUTH_BACKENDS` to `GitLabAuthBackend`
- `SETTING_SOCIAL_AUTH_GITLAB_KEY` to gitlab api key
- `SECRETS_social_auth_gitlab_secret` to gitlab api secret
- `SETTING_SOCIAL_AUTH_GITLAB_API_URL` to `https://gitlab.inf.ethz.ch`

Start with: `docker compose up`

Get realm creation URL with: `docker compose exec -u zulip zulip  /home/zulip/deployments/current/manage.py generate_realm_creation_link`

## Let's play with it
Try this out together and see how it goes.

## Cleanup

`docker compose rm` + `docker compose down -v`
