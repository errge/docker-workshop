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

## TODO Exercise: something from learnk8s

## Image management
But what are these `nilcons/debian` things that we can instantiate?

These are called images, think: "snapshot", containing the root filesystem of a VM.

They are stored on image servers (so called image registries), the
biggest public and default registry being https://hub.docker.com .

The real name for our image is actually `docker.io/nilcons/debian`,
but the docker client defaults to the `docker.io` image registry server.

### Image cache
Images are always cached locally, you can see the cache with `docker images`.

Similarly to images TODO

### rmi
### TODO check cxhub pull without auth but on ethz/eduroam wifi
## Dockerfile syntax and semantics
### Layer and storage tree (CoW: OverlayFS, Btrfs)
### Data layers: FROM, RUN
### Metadata layers: ENTRYPOINT, CMD, WORKDIR, USER, ENV
## TODO Dockerfileexercises from learnk8s
## Volumes
### host file sharing (docker -v ./asfdsaf:/data)
### data persistence (docker -v my-volume:/data)
## Networking tricks
### port forward
"docker run --rm -it -p 3000:8080" for small web experiments
### --network=none
### --network=host (Windows notes, security)
## Container vs host user
### Running as root
### Running as user (but still exec as root)
## docker socket mounting


# Lunch

# Code Expert specific: Environments
## ISG + CX build image (mention level, no details)
## cxenv base image
### scripts/ and helpers (.func, .start)
### cxrun 601 and cxuser 602 + sudoers (and demo of the example project)
## Code reading: current python-3_11 cxenv repo
# Demo
## Build of the python 3.11 image
## Running the python repl locally
## Running a complete student project locally
# Bigger apps in Docker
## Compose for multiple containers
## Networking (with compose, e.g. app container connecting to database container)
## Demo: some open source app that has a db (e.g. zulip, still have to test)
## Showing to colleagues with port forwarding (or --network=host)
## If we have time: Portainer demo
