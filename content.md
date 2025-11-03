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

### Consequence: Docker Desktop on OSX
## "docker run --rm -it" for small cli experiments (e.g. shyaml)
## "docker run --rm -it -p 3000:8080" for small web experiments
## Everyday commands: exec, ps, rm, images, rmi
## Volumes
### host file sharing (docker -v ./asfdsaf:/data)
### data persistence (docker -v my-volume:/data)
## Networking tricks
### --network=none
### --network=host (Windows notes, security)
## Container vs host user
### Running as root
### Running as user (but still exec as root)
## Dockerfile syntax and semantics
### Layer and storage tree (CoW: OverlayFS, Btrfs)
### Data layers: FROM, RUN
### Metadata layers: ENTRYPOINT, CMD, WORKDIR, USER, ENV
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
