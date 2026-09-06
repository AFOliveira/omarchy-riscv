# Omarchy RISC-V / SpacemiT K3

Integration workspace for the tested K3 port. This repository pins the source trees needed to build the port and records how the existing board was provisioned. Modified code lives in AFOliveira's public forks; unchanged dependencies retain their upstream URLs.

The core Omarchy desktop has booted on the physical K3 and survived a normal reboot. Arch owns PID 1, networking and the GPU-backed Hyprland session. The running kernel is SpacemiT's unchanged **6.18.3-generic**. The separately rebuilt kernel has **not** successfully booted on the physical board.

## Installed versions

Checked directly on the physical host on 2026-09-06:

| Component | Installed baseline |
| --- | --- |
| Kernel | SpacemiT/Bianbu `6.18.3-generic`, with matching vendor modules, firmware and graphics libraries |
| Arch | Community Arch Linux RISC-V, rolling release; staged from the `2026-08-27` rootfs and subsequently updated with pacman |
| Omarchy | Upstream tag `v3.8.4` plus the K3 port; the tag's version file reports `3.8.3` |
| Hyprland | `0.55.4-2.3` |
| systemd | `261.2-1` |
| glibc | `2.44+r24+g16be1518495f-1.1` |
| GCC | `16.2.1+r23+gd564253eb6c8-1` |
| LuaJIT | `2.1.1786451769-1.1` |

The Arch rootfs date identifies the starting archive, not a fixed Arch release or an immutable package snapshot. The kernel submodule records the source used for the separate kernel build; it does not establish the provenance of the preinstalled vendor kernel binary.

## Pinned source layout

| Path | Repository | Purpose |
| --- | --- | --- |
| `omarchy/` | [AFOliveira/omarchy, riscv/k3-bringup](https://github.com/AFOliveira/omarchy/tree/riscv/k3-bringup) | Omarchy v3.8.4 integration, build tools, boot/recovery support and tests |
| `omarchy/ports/k3/packages/` | [AFOliveira/omarchy-pkgs, riscv/k3](https://github.com/AFOliveira/omarchy-pkgs/tree/riscv/k3) | Nested submodule containing the tested RISC-V package profile |
| `kernel/` | [SpacemiT Linux 6.18](https://github.com/spacemit-com/linux-6.18) | Unmodified vendor source, with build configuration applied outside the source tree |
| `noVNC/` | [noVNC](https://github.com/novnc/noVNC) | Unmodified browser viewer |

Git submodule entries pin exact commits. `sources.lock.json` repeats those pins for inspection and records the Arch rootfs URL and SHA-256. PKGBUILDs pin their source archives and patches with checksums. Arch dependencies, Docker's Debian base tag and build-time plugin resolution remain rolling; this is not a fully reproducible distribution snapshot or a flashable image.

## Get the sources

Allow at least 30 GiB free for complete source checkout, kernel compilation and rootfs tests. Git and Python 3 are needed for checkout; Docker, curl and `qemu-system-riscv64` are also needed for workstation builds.

```bash
gh repo clone AFOliveira/omarchy-riscv
cd omarchy-riscv
./omarchy-riscv doctor
./omarchy-riscv bootstrap
./omarchy-riscv verify
```

`git clone --recurse-submodules` also works. Use `bootstrap --without-kernel` and `verify --without-kernel` to prepare only the desktop/package/viewer sources on a workstation with limited disk space. Kernel builds still require the complete kernel checkout.

## Build and test

```bash
# RV64GC and Arch rootfs checks, K3 kernel/DTBs/modules, and QEMU test kernel:
./omarchy-riscv build

# Or select a stage:
./omarchy-riscv smoke
./omarchy-riscv build-kernel
./omarchy-riscv build-qemu
```

Artifacts are written below `omarchy/build/`. The K3 kernel recipe uses `k3_bianbu_defconfig`, adds `-omarchy-k3` to the release name and disables debug information/BTF to reduce storage. The generic QEMU kernel has its own configuration and output directory. A successful QEMU boot does not validate K3 peripherals or physical kernel replacement.

On the provisioned Arch RISC-V host, or from the Bianbu staging environment:

```bash
# Run from this checkout; native packages require the staged Arch prerequisites.
sudo ./omarchy-riscv native-packages
sudo ./omarchy-riscv native-packages luajit
```

Packages compile as the ordinary user and install through pacman. The tested package overrides are under `omarchy/ports/k3/packages/ports/k3/pkgbuilds/`; upstream production publishing commands in the package repository are not the K3 builder. The package builder retains its existing `afonso`/UID 1000 provisioning assumptions.

## Board setup and remote desktop

Read [board setup](docs/board-setup.md), then the source port's [boot/recovery guide](omarchy/ports/k3/host-boot.md). The retained scripts target the original allocation's partition IDs and stock boot-file hashes. They are not safe to apply unchanged to an arbitrary K3. Physical boot support preserves the vendor kernel, device tree, initramfs and GPU libraries.

For the existing board, keep SSH credentials in your local state directory or set `K3_SSH_CONFIG` to your own SSH configuration containing an `omarchy-k3` alias:

```bash
./omarchy-riscv viewer-setup
./omarchy-riscv viewer
```

The viewer listens on workstation loopback and reaches the board through SSH. Vendor GPU binaries are obtained from the allocated Bianbu system; they are not included in this repository. Account credentials, access codes and correspondence are not included.

## Demonstrated scope

The [evidence directory](evidence/) records physical boot confirmation, native compilation and editor checks. The desktop passed remote keyboard input, lock/unlock, Chromium page rendering and LazyVim file opening. A fresh recursive source checkout, including the full vendor kernel, passed all four source-pin checks. The umbrella command `native-packages luajit` also built the package on the physical Arch host and passed the Lua equality regression. These checks are recorded in `source-checkout-validation.log`, `source-verification.txt` and `umbrella-native-package-check.log` under `evidence/`. Kernel compilation and the broader native package profile were exercised during bring-up; they were not repeated as a full rebuild for this publication.

Unfinished areas include the rebuilt kernel on hardware, audio/camera, Btrfs snapshots, Limine installation, optional x86/proprietary applications, general installation on another board, and the normal upstream Omarchy upgrade/migration path. The port's updater holds its tested Omarchy and compositor/runtime baseline.
