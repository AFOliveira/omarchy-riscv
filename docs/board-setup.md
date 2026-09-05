# Board provisioning boundaries and sequence

The current installation began on an allocated SpacemiT K3 running Bianbu 4.0. Its Arch userspace was first prepared in a container, then copied into an independent root tree and promoted to the physical host. The final desktop has no parent Bianbu desktop or container manager.

The source scripts preserve the tested allocation's user (`afonso`, UID 1000), filesystem layout, partition IDs and boot-file digest. Networking is captured from the currently assigned Bianbu interface. Porting these scripts to another allocation requires inspecting and adapting those assumptions, then validating recovery before any boot transition. This repository does not create a cloud account or allocate a board.

## Starting from the vendor installation

1. Establish authorized root SSH and a recovery route. Run `omarchy/ports/k3/probe.sh` and save the output outside Git. Preserve the vendor boot files, modules, firmware and GPU libraries. Independent power reset/UART was unavailable on the tested allocation; custom-kernel experiments remain less recoverable than userspace trials.
2. Retrieve the Arch rootfs named in `sources.lock.json`, verify its recorded SHA-256, and place it in `/home/bianbu/omarchy-port/downloads/`. The digest was observed after HTTPS download; it is not an independent publisher signature. Package signature checks remain enabled.
3. Transfer the initialized `omarchy/` checkout, including `ports/k3/packages/`, to the board. The staged Omarchy source is expected at `/opt/omarchy-source`, or at the path selected by `K3_OMARCHY_SOURCE` when configuring the user. The Bianbu staging tools require `systemd-nspawn`, rsync, a compiler and their normal system dependencies.
4. Run `ports/k3/stage-arch.sh` and `ports/k3/install-desktop-packages.sh` as Bianbu root. They provision `/var/lib/machines/omarchy-k3`. Mark the staged system with `/etc/omarchy-k3` inside that root before enabling the port's services. Set the ordinary user's password through the normal account tools and retain authorized SSH keys locally.
5. Run `ports/k3/stage-vendor-graphics.sh` and `ports/k3/build-packages.sh`. Run `ports/k3/configure-user.sh` as the ordinary Arch user with the source path set. The graphics step copies the installed vendor ABI into `/opt/spacemit` inside Arch; it does not replace the vendor kernel.
6. Use `ports/k3/enable-container.sh --cli-only` for CLI staging and `ports/k3/enable-container.sh` for the intermediate graphical session. Complete `ports/k3/configure-session.sh` in that user's graphical session. Validate the terminal, editor, browser, graphics and remote input before changing the physical startup path.
7. Follow the exact prerequisites and recovery-timer tests in [host-boot.md](../omarchy/ports/k3/host-boot.md). `stage-host.sh`, `trial-host.sh`, `trial-physical.sh` and `enable-host-desktop.sh` implement the staged host transition. The boot wrapper first restores the stock boot selection, then starts a timed fallback before executing Arch systemd. Its confirmation service selects future Arch boots only after the host and desktop health checks pass.

The guide documents the demonstrated process; it is not a fresh-board unattended installer. There is no one-command flash step. A working vendor kernel plus an Arch root is sufficient for this first port; using a newly rebuilt kernel is a separate experiment.

## Existing physical Arch installation

SSH with the workstation's local `omarchy-k3` alias reaches the ordinary Arch user directly. Use a root SSH session for administration. The old container alias is unnecessary. The user desktop is started by `omarchy-k3-host-desktop.service`; `omarchy-k3-confirm-host-boot.service` records and confirms the physical boot.

For native package work, clone or transfer this initialized umbrella checkout onto the Arch host and run `sudo ./omarchy-riscv native-packages PACKAGE`. The native builder takes its recipes from the pinned package submodule. Build output and source caches remain on the board and are not Git content.

The original Bianbu installation remains the recovery environment. Use the documented stock-boot restoration procedure in the port guide when intentionally returning to it. A recovery timer cannot resolve a kernel/firmware hang that occurs before the timer starts.
