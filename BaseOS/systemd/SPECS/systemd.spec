#global commit c4b843473a75fb38ed5bf54e9d3cfb1cb3719efa
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

#global stable 1

# We ship a .pc file but don't want to have a dep on pkg-config. We
# strip the automatically generated dep here and instead co-own the
# directory.
%global __requires_exclude pkg-config

%global pkgdir %{_prefix}/lib/systemd
%global system_unit_dir %{pkgdir}/system
%global user_unit_dir %{pkgdir}/user

# Bootstrap may be needed to break intercircular dependencies with
# cryptsetup, e.g. when re-building cryptsetup on a json-c SONAME-bump.
%bcond_with    bootstrap
%bcond_without tests
%bcond_without lto

Name:           systemd
Url:            https://www.freedesktop.org/wiki/Software/systemd
Version:        250
Release:        12%{?dist}
# For a breakdown of the licensing, see README
License:        LGPLv2+ and MIT and GPLv2+
Summary:        System and Service Manager

# download tarballs with "spectool -g systemd.spec"
%if %{defined commit}
Source0:        https://github.com/systemd/systemd%{?stable:-stable}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
%else
%if 0%{?stable}
Source0:        https://github.com/systemd/systemd-stable/archive/v%{version_no_tilde}/%{name}-%{version_no_tilde}.tar.gz
%else
Source0:        https://github.com/systemd/systemd/archive/v%{version_no_tilde}/%{name}-%{version_no_tilde}.tar.gz
%endif
%endif
# This file must be available before %%prep.
# It is generated during systemd build and can be found in build/src/core/.
Source1:        triggers.systemd
Source2:        split-files.py
Source3:        purge-nobody-user

# Prevent accidental removal of the systemd package
Source4:        yum-protect-systemd.conf

Source5:        inittab
Source6:        sysctl.conf.README
Source7:        systemd-journal-remote.xml
Source8:        systemd-journal-gatewayd.xml
Source9:        20-yama-ptrace.conf
Source10:       systemd-udev-trigger-no-reload.conf
Source11:       20-grubby.install
Source12:       systemd-user
Source13:       libsystemd-shared.abignore

Source14:       10-oomd-defaults.conf
Source15:       10-oomd-root-slice-defaults.conf
Source16:       10-oomd-user-service-defaults.conf

Source21:       macros.sysusers
Source22:       sysusers.attr
Source23:       sysusers.prov
Source24:       sysusers.generate-pre.sh
Source25:       rc.local

%if 0
GIT_DIR=../../src/systemd/.git git format-patch-ab --no-signature -M -N v235..v235-stable
i=1; for j in 00*patch; do printf "Patch%04d:      %s\n" $i $j; i=$((i+1));done|xclip
GIT_DIR=../../src/systemd/.git git diffab -M v233..master@{2017-06-15} -- hwdb/[67]* hwdb/parse_hwdb.py > hwdb.patch
%endif

# Backports of patches from upstream (0000–0499)
#
# Any patches which are "in preparation" upstream should be listed
# here, rather than in the next section. Packit CI will drop any
# patches in this range before applying upstream pull requests.

# RHEL-specific
Patch0001: 0001-logind-set-RemoveIPC-to-false-by-default.patch
Patch0002: 0002-tmpfiles-don-t-create-resolv.conf-stub-resolv.conf-s.patch
Patch0003: 0003-Copy-40-redhat.rules-from-RHEL-8.patch
Patch0004: 0004-Avoid-tmp-being-mounted-as-tmpfs-without-the-user-s-.patch
Patch0005: 0005-unit-don-t-add-Requires-for-tmp.mount.patch
Patch0006: 0006-units-add-Install-section-to-tmp.mount.patch
Patch0007: 0007-rc-local-order-after-network-online.target.patch
Patch0008: 0008-ci-drop-CIs-irrelevant-for-downstream.patch
Patch0009: 0009-ci-reconfigure-Packit-for-RHEL-9.patch
Patch0010: 0010-ci-run-unit-tests-on-z-stream-branches-as-well.patch
Patch0011: 0011-random-util-increase-random-seed-size-to-1024.patch
Patch0012: 0012-journal-don-t-enable-systemd-journald-audit.socket-b.patch
Patch0013: 0013-journald.conf-don-t-touch-current-audit-settings.patch
Patch0014: 0014-Revert-udev-remove-WAIT_FOR-key.patch
Patch0015: 0015-Really-don-t-enable-systemd-journald-audit.socket.patch
Patch0016: 0016-rules-add-elevator-kernel-command-line-parameter.patch
Patch0017: 0017-units-don-t-enable-tmp.mount-statically-in-local-fs..patch
Patch0018: 0018-pid1-bump-DefaultTasksMax-to-80-of-the-kernel-pid.ma.patch
Patch0019: 0019-set-core-ulimit-to-0-like-on-RHEL-7.patch
Patch0020: 0020-ci-use-C9S-chroots-in-Packit.patch
Patch0021: 0021-test-mountpointutil-util-do-not-assert-in-test_mnt_i.patch
Patch0022: 0022-Treat-EPERM-as-not-available-too.patch
Patch0023: 0023-test-copy-portable-profiles-into-the-image-if-they-d.patch
Patch0024: 0024-test-introduce-get_cgroup_hierarchy-helper.patch
Patch0025: 0025-test-require-unified-cgroup-hierarchy-for-TEST-56.patch
Patch0026: 0026-tests-rework-test-macros-to-not-take-code-as-paramet.patch
Patch0027: 0027-test-allow-to-set-NULL-to-intro-or-outro.patch
Patch0028: 0028-udev-net-setup-link-change-the-default-MACAddressPol.patch
Patch0029: 0029-man-mention-System-Administrator-s-Guide-in-systemct.patch
Patch0030: 0030-Net-naming-scheme-for-RHEL-9.0.patch
Patch0031: 0031-core-decrease-log-level-of-messages-about-use-of-Kil.patch
Patch0032: 0032-ci-replace-apt-key-with-signed-by.patch
Patch0033: 0033-ci-fix-clang-13-installation.patch
Patch0034: 0034-test-check-systemd-RPM-macros.patch
Patch0035: 0035-test-do-not-assume-x86-64-arch-in-TEST-58-REPART.patch
Patch0036: 0036-tests-add-repart-tests-for-block-devices-with-1024-2.patch
Patch0037: 0037-test-accept-both-unpadded-and-padded-partition-sizes.patch
Patch0038: 0038-test-lvm-2.03.15-dropped-the-static-autoactivation.patch
Patch0039: 0039-test-accept-GC-ed-units-in-newer-LVM.patch
Patch0040: 0040-shared-Add-more-dlopen-tests.patch
Patch0041: 0041-systemctl-Show-how-long-a-service-ran-for-after-it-e.patch
Patch0042: 0042-time-util-introduce-TIMESTAMP_UNIX.patch
Patch0043: 0043-systemctl-man-update-docs-for-timestamp.patch
Patch0044: 0044-systemctl-make-timestamp-affect-the-show-verb-as-wel.patch
Patch0045: 0045-tests-allow-running-all-the-services-with-SYSTEMD_LO.patch
Patch0046: 0046-coredump-raise-the-coredump-save-size-on-64bit-syste.patch
Patch0047: 0047-repart-fix-sector-size-handling.patch
Patch0048: 0048-mkdir-allow-to-create-directory-whose-path-contains-.patch
Patch0049: 0049-mkdir-CHASE_NONEXISTENT-cannot-used-in-chase_symlink.patch
Patch0050: 0050-meson-move-efi-file-lists-closer-to-where-they-are-u.patch
Patch0051: 0051-meson-move-efi-summary-section-to-src-boot-efi.patch
Patch0052: 0052-meson-report-SBAT-settings.patch
Patch0053: 0053-boot-Build-BCD-parser-only-on-arches-supported-by-Wi.patch
Patch0054: 0054-meson-Remove-efi-cc-option.patch
Patch0055: 0055-meson-Get-objcopy-location-from-compiler.patch
Patch0056: 0056-meson-Use-files-for-source-lists-for-boot-and-fundam.patch
Patch0057: 0057-meson-Use-files-for-tests.patch
Patch0058: 0058-tests-add-fuzz-bcd.patch
Patch0059: 0059-meson-Use-files-for-fuzzers.patch
Patch0060: 0060-meson-Add-check-argument-to-remaining-run_command-ca.patch
Patch0061: 0061-meson-Use-echo-to-list-files.patch
Patch0062: 0062-test-add-a-test-for-mkdir_p.patch
Patch0063: 0063-util-another-set-of-CVE-2021-4034-assert-s.patch
Patch0064: 0064-basic-update-CIFS-magic.patch
Patch0065: 0065-shared-be-extra-paranoid-and-check-if-argc-0.patch
Patch0066: 0066-core-check-if-argc-0-and-argv-0-is-set.patch
Patch0067: 0067-core-check-argc-argv-uncoditionally.patch
Patch0068: 0068-test-temporary-workaround-for-21819.patch
Patch0069: 0069-test-don-t-leak-local-variable-to-outer-scopes.patch
Patch0070: 0070-tree-wide-don-t-use-strjoina-on-getenv-values.patch
Patch0071: 0071-man-clarify-Environmentfile-format.patch
Patch0072: 0072-test-load-fragment-add-a-basic-test-for-config_parse.patch
Patch0073: 0073-core-execute-use-_cleanup_-in-exec_context_load_envi.patch
Patch0074: 0074-test-env-file-add-tests-for-quoting-in-env-files.patch
Patch0075: 0075-core-shorten-long-unit-names-that-are-based-on-paths.patch
Patch0076: 0076-tests-add-test-case-for-long-unit-names.patch
Patch0077: 0077-tests-reflect-that-we-can-now-handle-devices-with-ve.patch
Patch0078: 0078-test-extend-the-hashed-unit-names-coverage-a-bit.patch
Patch0079: 0079-Revert-kernel-install-also-remove-modules.builtin.al.patch
Patch0080: 0080-Revert-kernel-install-prefer-boot-over-boot-efi-for-.patch
Patch0081: 0081-kernel-install-50-depmod-port-to-bin-sh.patch
Patch0082: 0082-kernel-install-90-loaderentry-port-to-bin-sh.patch
Patch0083: 0083-kernel-install-fix-shellcheck.patch
Patch0084: 0084-kernel-install-port-to-bin-sh.patch
Patch0085: 0085-kernel-install-90-loaderentry-error-out-on-nonexiste.patch
Patch0086: 0086-kernel-install-don-t-pull-out-KERNEL_IMAGE.patch
Patch0087: 0087-kernel-install-prefer-boot-over-boot-efi-for-BOOT_RO.patch
Patch0088: 0088-kernel-install-also-remove-modules.builtin.alias.bin.patch
Patch0089: 0089-kernel-install-add-new-variable-KERNEL_INSTALL_INITR.patch
Patch0090: 0090-kernel-install-k-i-already-creates-ENTRY_DIR_ABS-no-.patch
Patch0091: 0091-kernel-install-prefix-errors-with-Error-exit-immedia.patch
Patch0092: 0092-kernel-install-add-KERNEL_INSTALL_STAGING_AREA-direc.patch
Patch0093: 0093-kernel-install-add-missing-log-line.patch
Patch0094: 0094-kernel-install-don-t-try-to-persist-used-machine-ID-.patch
Patch0095: 0095-kernel-install-add-a-new-ENTRY_TOKEN-variable-for-na.patch
Patch0096: 0096-kernel-install-only-generate-systemd.boot_id-in-kern.patch
Patch0097: 0097-kernel-install-search-harder-for-kernel-image-initrd.patch
Patch0098: 0098-kernel-install-add-new-inspect-verb-showing-paths-an.patch
Patch0099: 0099-ci-Mergify-configuration-update.patch
Patch0100: 0100-ci-Mergify-fix-copy-paste-bug.patch
Patch0101: 0101-shared-Fix-memory-leak-in-bus_append_execute_propert.patch
Patch0102: 0102-fuzz-no-longer-skip-empty-files.patch
Patch0103: 0103-networkctl-open-the-bus-just-once.patch
Patch0104: 0104-json-align-table.patch
Patch0105: 0105-fuzz-json-optionally-allow-logging-and-output.patch
Patch0106: 0106-shared-json-reduce-scope-of-variables.patch
Patch0107: 0107-fuzz-json-also-do-sorting-and-normalizing-and-other-.patch
Patch0108: 0108-shared-json-wrap-long-comments.patch
Patch0109: 0109-shared-json-fix-memory-leak-on-failed-normalization.patch
Patch0110: 0110-shared-json-add-helper-to-ref-first-unref-second.patch
Patch0111: 0111-basic-alloc-util-remove-unnecessary-parens.patch
Patch0112: 0112-fuzz-json-also-try-self-merge-operations.patch
Patch0113: 0113-shared-json-fix-another-memleak-in-normalization.patch
Patch0114: 0114-shared-json-fix-memleak-in-sort.patch
Patch0115: 0115-execute-fix-resource-leak.patch
Patch0116: 0116-tests-ignore-dbus-broker-launcher.patch
Patch0117: 0117-core-timer-fix-memleak.patch
Patch0118: 0118-timedatectl-fix-a-memory-leak.patch
Patch0119: 0119-test-fix-file-descriptor-leak-in-test-psi-util.patch
Patch0120: 0120-test-fix-file-descriptor-leak-in-test-tmpfiles.c.patch
Patch0121: 0121-test-fix-file-descriptor-leak-in-test-fs-util.patch
Patch0122: 0122-test-fix-file-descriptor-leak-in-test-oomd-util.patch
Patch0123: 0123-test-fix-file-descriptor-leak-in-test-catalog.patch
Patch0124: 0124-test-make-masking-of-supplementary-services-configur.patch
Patch0125: 0125-test-fuzz-our-dbus-interfaces-with-dfuzzer.patch
Patch0126: 0126-test-skip-TEST-21-DFUZZER-without-ASan.patch
Patch0127: 0127-core-annotate-Reexecute-as-NoReply.patch
Patch0128: 0128-test-always-force-a-new-image-for-dfuzzer.patch
Patch0129: 0129-test-make-dfuzzer-less-verbose.patch
Patch0130: 0130-test-drop-the-at_exit-coredump-check.patch
Patch0131: 0131-test-make-the-shutdown-routine-a-bit-more-robust.patch
Patch0132: 0132-tree-wide-drop-manually-crafted-message-for-missing-.patch
Patch0133: 0133-test-allow-overriding-QEMU_MEM-when-running-w-ASan.patch
Patch0134: 0134-test-don-t-test-buses-we-don-t-ship.patch
Patch0135: 0135-shutdown-get-only-active-md-arrays.patch
Patch0136: 0136-bus-Use-OrderedSet-for-introspection.patch
Patch0137: 0137-logind-session-dbus-allow-to-set-display-name-via-db.patch
Patch0138: 0138-ci-limit-which-env-variables-we-pass-through-sudo.patch
Patch0139: 0139-ci-Mergify-Add-ci-waived-logic.patch
Patch0140: 0140-json-use-unsigned-for-refernce-counter.patch
Patch0141: 0141-macro-check-over-flow-in-reference-counter.patch
Patch0142: 0142-sd-bus-fix-reference-counter-to-be-incremented.patch
Patch0143: 0143-sd-bus-introduce-ref-unref-function-for-track_item.patch
Patch0144: 0144-sd-bus-do-not-read-unused-value.patch
Patch0145: 0145-sd-bus-do-not-return-negative-errno-when-unknown-nam.patch
Patch0146: 0146-sd-bus-use-hashmap_contains-and-drop-unnecessary-cas.patch
Patch0147: 0147-test-shorten-code-a-bit.patch
Patch0148: 0148-test-add-several-tests-for-track-item.patch
Patch0149: 0149-core-slice-make-slice_freezer_action-return-0-if-fre.patch
Patch0150: 0150-core-unit-fix-use-after-free.patch
Patch0151: 0151-core-timer-fix-potential-use-after-free.patch
Patch0152: 0152-core-command-argument-can-be-longer-than-PATH_MAX.patch
Patch0153: 0153-shared-install-consistently-use-lp-as-the-name-for-t.patch
Patch0154: 0154-shared-specifier-treat-NULL-the-same-as.patch
Patch0155: 0155-shared-install-do-not-print-aliases-longer-than-UNIT.patch
Patch0156: 0156-shared-install-printf-drop-now-unused-install_path_p.patch
Patch0157: 0157-strv-declare-iterator-of-FOREACH_STRING-in-the-loop.patch
Patch0158: 0158-basic-unit-file-split-out-the-subroutine-for-symlink.patch
Patch0159: 0159-basic-stat-util-add-null_or_empty_path_with_root.patch
Patch0160: 0160-shared-install-reuse-the-standard-symlink-verificati.patch
Patch0161: 0161-shared-install-add-a-bit-more-quoting.patch
Patch0162: 0162-test-add-test-for-systemctl-link-enable.patch
Patch0163: 0163-tests-add-helper-for-creating-tempfiles-with-content.patch
Patch0164: 0164-man-clarify-the-descriptions-of-aliases-and-linked-u.patch
Patch0165: 0165-basic-add-new-variable-SYSTEMD_OS_RELEASE-to-overrid.patch
Patch0166: 0166-test-os-util-add-basic-tests-for-os-release-parsing.patch
Patch0167: 0167-basic-env-file-make-load-env-file-deduplicate-entrie.patch
Patch0168: 0168-man-os-release-add-a-note-about-repeating-entries.patch
Patch0169: 0169-shared-specifier-clarify-and-add-test-for-missing-da.patch
Patch0170: 0170-shared-specifier-provide-proper-error-messages-when-.patch
Patch0171: 0171-shared-install-provide-proper-error-messages-when-in.patch
Patch0172: 0172-shared-install-move-scope-into-InstallContext.patch
Patch0173: 0173-shared-specifier-fix-u-U-g-G-when-called-as-unprivil.patch
Patch0174: 0174-shared-install-simplify-unit_file_dump_changes.patch
Patch0175: 0175-shared-install-propagate-errors-about-invalid-aliase.patch
Patch0176: 0176-shared-install-return-failure-when-enablement-fails-.patch
Patch0177: 0177-systemctl-fix-silent-failure-when-root-is-not-found.patch
Patch0178: 0178-shared-install-also-check-for-self-aliases-during-in.patch
Patch0179: 0179-docs-Correct-WantedBy-regarding-template-units.patch
Patch0180: 0180-man-fix-invalid-description-of-template-handling-in-.patch
Patch0181: 0181-shared-install-drop-unnecessary-casts.patch
Patch0182: 0182-strv-make-iterator-in-STRV_FOREACH-declaread-in-the-.patch
Patch0183: 0183-core-ExecContext-restrict_filesystems-is-set-of-stri.patch
Patch0184: 0184-install-when-linking-a-file-create-the-link-first-or.patch
Patch0185: 0185-shared-install-split-unit_file_-disable-enable-so-_r.patch
Patch0186: 0186-shared-install-fix-reenable-on-linked-unit-files.patch
Patch0187: 0187-test-systemctl-enable-extend-the-test-for-repeated-W.patch
Patch0188: 0188-shared-install-when-we-fail-to-chase-a-symlink-show-.patch
Patch0189: 0189-shared-install-do-not-try-to-resolve-symlinks-outsid.patch
Patch0190: 0190-test-systemctl-enable-enhance-the-test-for-unit-file.patch
Patch0191: 0191-shared-install-skip-unnecessary-chasing-of-symlinks-.patch
Patch0192: 0192-shared-install-also-remove-symlinks-like-.wants-foo-.patch
Patch0193: 0193-shared-install-create-relative-symlinks-for-enableme.patch
Patch0194: 0194-shared-install-when-looking-for-symlinks-in-.wants-..patch
Patch0195: 0195-shared-install-stop-passing-duplicate-root-argument-.patch
Patch0196: 0196-basic-unit-file-reverse-negative-conditional.patch
Patch0197: 0197-shared-install-split-UNIT_FILE_SYMLINK-into-two-stat.patch
Patch0198: 0198-shared-install-fix-handling-of-a-linked-unit-file.patch
Patch0199: 0199-test-systemctl-enable-make-shellcheck-happy.patch
Patch0200: 0200-shared-install-when-creating-symlinks-accept-differe.patch
Patch0201: 0201-test-systemctl-enable-use-magic-syntax-to-allow-inve.patch
Patch0202: 0202-test-systemctl-enable-also-use-freshly-built-systemd.patch
Patch0203: 0203-test-systemctl-enable-disable-the-test-for-a-for-now.patch
Patch0204: 0204-Rename-UnitFileScope-to-LookupScope.patch
Patch0205: 0205-core-handle-lookup-paths-being-symlinks.patch
Patch0206: 0206-shared-install-use-correct-cleanup-function.patch
Patch0207: 0207-udev-net_id-avoid-slot-based-names-only-for-single-f.patch
Patch0208: 0208-test-import-logind-test-from-debian-ubuntu-test-suit.patch
Patch0209: 0209-test-drop-redundant-IMAGE_NAME.patch
Patch0210: 0210-test-import-timedated-test-from-debian-ubuntu-test-s.patch
Patch0211: 0211-test-introduce-assert_not_in-helper-function.patch
Patch0212: 0212-test-drop-unnecessary-no-pager-option.patch
Patch0213: 0213-test-support-debian-ubuntu-specific-timezone-config-.patch
Patch0214: 0214-test-import-hostnamed-tests-from-debian-ubuntu-test-.patch
Patch0215: 0215-locale-util-fix-memleak-on-failure.patch
Patch0216: 0216-locale-util-check-if-enumerated-locales-are-valid.patch
Patch0217: 0217-locale-util-align-locale-entries.patch
Patch0218: 0218-core-inline-an-iterator-variable.patch
Patch0219: 0219-locale-setup-merge-locale-handling-in-PID1-and-local.patch
Patch0220: 0220-locale-rename-keymap-util.-ch-localed-util.-ch.patch
Patch0221: 0221-test-add-one-more-path-to-search-keymaps.patch
Patch0222: 0222-test-introduce-inst_recursive-helper-function.patch
Patch0223: 0223-hmac-sha256-move-size-define-to-sha256.h.patch
Patch0224: 0224-tpm2-support-policies-with-PIN.patch
Patch0225: 0225-cryptenroll-add-support-for-TPM2-pin.patch
Patch0226: 0226-cryptsetup-add-support-for-TPM2-pin.patch
Patch0227: 0227-cryptsetup-add-libcryptsetup-TPM2-PIN-support.patch
Patch0228: 0228-cryptenroll-add-TPM2-PIN-documentation.patch
Patch0229: 0229-cryptsetup-add-manual-TPM2-PIN-configuration.patch
Patch0230: 0230-cryptenroll-add-tests-for-TPM2-unlocking.patch
Patch0231: 0231-env-util-replace-unsetenv_erase-by-new-getenv_steal_.patch
Patch0232: 0232-test-install-libxkbcommon-and-x11-keymaps.patch
Patch0233: 0233-test-install-C.UTF-8-and-English-locales.patch
Patch0234: 0234-test-import-localed-tests-from-debian-ubuntu-test-su.patch
Patch0235: 0235-unit-check-for-mount-rate-limiting-before-checking-a.patch
Patch0236: 0236-tests-make-sure-we-delay-running-mount-start-jobs-wh.patch
Patch0237: 0237-test-insert-space-in-for-loop.patch
Patch0238: 0238-test-move-do-at-the-end-of-line.patch
Patch0239: 0239-test-use-trap-RETURN.patch
Patch0240: 0240-test-ignore-the-error-about-our-own-libraries-missin.patch
Patch0241: 0241-test-wrap-binaries-using-systemd-DSOs-when-running-w.patch
Patch0242: 0242-test-set-ASAN_RT_PATH-along-with-LD_PRELOAD-to-the-A.patch
Patch0243: 0243-test-drop-all-LD_PRELOAD-related-ASan-workarounds.patch
Patch0244: 0244-test-don-t-wrap-binaries-built-with-ASan.patch
Patch0245: 0245-test-send-stdout-stderr-of-testsuite-units-to-journa.patch
Patch0246: 0246-test-make-the-busy-loop-in-TEST-02-less-verbose.patch
Patch0247: 0247-test-always-wrap-useradd-userdel-when-running-w-ASan.patch
Patch0248: 0248-test-don-t-flush-debug-logs-to-the-console.patch
Patch0249: 0249-test-fix-a-couple-of-issues-found-by-shellcheck.patch
Patch0250: 0250-test-pass-the-initdir-to-check_result_-qemu-nspawn-h.patch
Patch0251: 0251-test-run-the-custom-check-hooks-before-common-checks.patch
Patch0252: 0252-test-check-journal-directly-instead-of-capturing-con.patch
Patch0253: 0253-test-use-saved-process-PID-instead-of.patch
Patch0254: 0254-test-account-for-ADDR_NO_RANDOMIZE-if-it-s-set.patch
Patch0255: 0255-fuzz-bcd-silence-warning-about-always-true-compariso.patch
Patch0256: 0256-test-disable-test_ntp-on-RHEL.patch
Patch0257: 0257-core-do-not-filter-out-systemd.unit-and-run-level-sp.patch
Patch0258: 0258-test-add-a-simple-test-for-daemon-reexec.patch
Patch0259: 0259-test-install-usr-libexec-vi-as-well.patch
Patch0260: 0260-test-resize-the-terminal-automagically-with-INTERACT.patch
Patch0261: 0261-test-create-an-ASan-wrapper-for-getent-and-su.patch
Patch0262: 0262-test-mark-partition-bootable.patch
Patch0263: 0263-test-bump-the-data-partition-size-if-we-don-t-strip-.patch
Patch0264: 0264-test-use-PBKDF2-with-capped-iterations-instead-of-Ar.patch
Patch0265: 0265-locale-drop-unnecessary-allocation.patch
Patch0266: 0266-Revert-shared-install-create-relative-symlinks-for-e.patch
Patch0267: 0267-glyph-util-add-new-glyphs-for-up-down-arrows.patch
Patch0268: 0268-tree-wide-allow-ASCII-fallback-for-in-logs.patch
Patch0269: 0269-tree-wide-allow-ASCII-fallback-for-in-logs.patch
Patch0270: 0270-core-allow-to-set-default-timeout-for-devices.patch
Patch0271: 0271-man-document-DefaultDeviceTimeoutSec.patch
Patch0272: 0272-man-update-dbus-docs.patch
Patch0273: 0273-hwdb-60-keyboard-Fix-volume-button-mapping-on-Asus-T.patch
Patch0274: 0274-hwdb-CH-Pro-Pedals-not-classified-correctly-due-to-n.patch
Patch0275: 0275-hwdb-Add-accel-orientation-quirk-for-the-GPD-Pocket-.patch
Patch0276: 0276-hostname-Allow-overriding-the-chassis-type-from-hwdb.patch
Patch0277: 0277-hwdb-Add-Microsoft-Surface-Pro-1-chassis-quirk.patch
Patch0278: 0278-hwdb-treat-logitech-craft-keyboard-as-a-keyboard.patch
Patch0279: 0279-test-frequency-in-mouse-DPI-is-optional.patch
Patch0280: 0280-hwdb-add-two-Elecom-trackballs.patch
Patch0281: 0281-hwdb-add-new-database-file-for-PDA-devices.patch
Patch0282: 0282-hwdb-add-support-for-Surface-Laptop-2-3-22303.patch
Patch0283: 0283-hwdb-add-HP-calculators.patch
Patch0284: 0284-hwbd-60-sensor.hwdb-Add-Pipo-W2Pro.patch
Patch0285: 0285-hwdb-60-keyboard-Support-the-buttons-on-CZC-P10T-tab.patch
Patch0286: 0286-hwdb-add-CST-Laser-Trackball-22583.patch
Patch0287: 0287-hwdb-Force-release-calculator-key-on-all-HP-OMEN-lap.patch
Patch0288: 0288-Add-support-for-NEC-VersaPro-VG-S.patch
Patch0289: 0289-Fix-mic-mute-on-Acer-TravelMate-B311-31-22677.patch
Patch0290: 0290-Add-AV-production-controllers-to-hwdb-and-add-uacces.patch
Patch0291: 0291-hwdb-Add-AV-production-access-to-Elgado-Stream-Deck-.patch
Patch0292: 0292-Add-HP-Elitebook-2760p-support-22766.patch
Patch0293: 0293-hwdb-Add-mic-mute-key-mapping-for-HP-Elite-x360.patch
Patch0294: 0294-hwdb-fix-parser-to-work-with-newer-pyparsing.patch
Patch0295: 0295-hwdb-update-for-v251.patch
Patch0296: 0296-hwdb-update-autosuspend-entries.patch
Patch0297: 0297-hwdb-drop-boilerplate-about-match-patterns-being-uns.patch
Patch0298: 0298-hwdb-Update-60-keyboard.hwdb-23074.patch
Patch0299: 0299-hwdb-60-keyboard-Add-Acer-Aspire-One-AO532h-keymappi.patch
Patch0300: 0300-hwdb-60-keyboard-Add-HP-Compaq-KBR0133.patch
Patch0301: 0301-hwdb-add-resolutions-for-the-Vaio-FE14-touchpad-2313.patch
Patch0302: 0302-hwdb-Remap-micmute-to-f20-for-ASUS-WMI-hotkeys.patch
Patch0303: 0303-hwdb-Fix-rotation-for-HP-Pro-Tablet-408-G1.patch
Patch0304: 0304-hwdb-add-keyboard-mapping-for-HP-ProBook-11G2.patch
Patch0305: 0305-hwdb-make-sure-ninja-update-hwdb-works-on-f35.patch
Patch0306: 0306-hwbd-run-update-hwdb-for-v251-rc2.patch
Patch0307: 0307-hwdb-run-ninja-update-hwdb-autosuspend-for-v251-rc2.patch
Patch0308: 0308-Fix-orientation-detection-for-Asus-Transformer-T100T.patch
Patch0309: 0309-Fix-orientation-detection-for-HP-Pavilion-X2-10-k010.patch
Patch0310: 0310-fix-typo.patch
Patch0311: 0311-Adding-a-description-of-the-keyboard-shortcut-Fn-F12.patch
Patch0312: 0312-hwdb-run-update-hwdb.patch
Patch0313: 0313-hwdb-add-rammus-accelerometer-support.patch
Patch0314: 0314-Add-support-to-set-autosuspend-delay-via-hwdb.patch
Patch0315: 0315-Set-autosuspend-delay-for-Fibocom-LG850-GL.patch
Patch0316: 0316-Add-HUION-Inspiroy-H420X-to-hwdb.patch
Patch0317: 0317-hwdb-run-update-hwdb-for-v251-rc3.patch
Patch0318: 0318-hwdb-add-touchpad-parameters-for-Lenovo-T15g-Gen1-23.patch
Patch0319: 0319-hwdb-Add-accel-orientation-for-the-I15-TG.patch
Patch0320: 0320-hwdb-fix-accelerometer-mount-matrix-for-Aquarius-NS4.patch
Patch0321: 0321-hwdb-Add-Google-Hangouts-Meet-speakermic.patch
Patch0322: 0322-hwdb-update-via-ninja-C-build-update-hwdb.patch
Patch0323: 0323-hwdb-Add-Google-Meet-speakermic.patch
Patch0324: 0324-hwdb-Add-accel-orientation-quirk-for-the-Aya-Neo-Nex.patch
Patch0325: 0325-hwdb-Add-HP-Dev-One.patch
Patch0326: 0326-hwdb-analyzers-remove-generic-STM-Device-in-DFU-Mode.patch
Patch0327: 0327-hwdb-Add-Lenovo-ThinkPad-C13-Yoga.patch
Patch0328: 0328-Fix-automatic-screen-rotation-for-Asus-Transformer-T.patch
Patch0329: 0329-hwdb-Add-Acer-Aspire-A317-33-24050.patch
Patch0330: 0330-Add-ACCEL_MOUNT_MATRIX-for-OXP-Mini.patch
Patch0331: 0331-Added-DERE-DBook-D10-24173.patch
Patch0332: 0332-hwdb-analyzers-Clarify-the-type-of-devices-we-want-l.patch
Patch0333: 0333-hwdb-Add-Greaseweazle-drives-to-the-list-of-analyzer.patch
Patch0334: 0334-hwdb-Apply-existing-accel-orientation-quirk-to-all-C.patch
Patch0335: 0335-shared-install-fix-crash-when-reenable-is-called-wit.patch
Patch0336: 0336-scope-allow-unprivileged-delegation-on-scopes.patch
Patch0337: 0337-udev-net_id-add-rhel-9.1-naming-scheme.patch
Patch0338: 0338-core-load-fragment-move-config_parse_sec_fix_0-to-sr.patch
Patch0339: 0339-logind-add-option-to-stop-idle-sessions-after-specif.patch
Patch0340: 0340-tree-wide-fix-typo.patch
Patch0341: 0341-test-several-cleanups-for-TEST-35-LOGIN.patch
Patch0342: 0342-test-start-test-user-session-before-idle-action-sett.patch
Patch0343: 0343-test-ensure-cleanup-functions-return-success.patch
Patch0344: 0344-test-add-test-for-org.freedesktop.login1.Session-Set.patch
Patch0345: 0345-test-add-a-simple-test-for-list-users.patch
Patch0346: 0346-test-merge-grep-awk-calls.patch
Patch0347: 0347-test-wait-for-user-service-or-slice-to-be-finished.patch
Patch0348: 0348-test-terminate-session-and-user-on-cleanup.patch
Patch0349: 0349-test-do-not-restart-getty-tty2-automatically.patch
Patch0350: 0350-tests-add-test-for-StopIdleSessionSec-option.patch
Patch0351: 0351-logind-schedule-idle-check-full-interval-from-now-if.patch

# Downstream-only patches (9000–9999)

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  coreutils
BuildRequires:  libcap-devel
BuildRequires:  libmount-devel
BuildRequires:  libfdisk-devel
BuildRequires:  pam-devel
BuildRequires:  libselinux-devel
BuildRequires:  audit-libs-devel
%if %{without bootstrap}
BuildRequires:  cryptsetup-devel
%endif
BuildRequires:  dbus-devel
# /usr/bin/getfacl is needed by test-acl-util
BuildRequires:  acl
BuildRequires:  libacl-devel
BuildRequires:  gobject-introspection-devel
BuildRequires:  libblkid-devel
BuildRequires:  xz-devel
BuildRequires:  xz
BuildRequires:  lz4-devel
BuildRequires:  lz4
BuildRequires:  bzip2-devel
BuildRequires:  libzstd-devel
BuildRequires:  libidn2-devel
BuildRequires:  libcurl-devel
BuildRequires:  kmod-devel
BuildRequires:  elfutils-devel
BuildRequires:  openssl-devel
BuildRequires:  libgcrypt-devel
BuildRequires:  libgpg-error-devel
BuildRequires:  gnutls-devel
BuildRequires:  libmicrohttpd-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  libxslt
BuildRequires:  docbook-style-xsl
BuildRequires:  pkgconfig
BuildRequires:  gperf
BuildRequires:  gawk
BuildRequires:  tree
BuildRequires:  hostname
BuildRequires:  python3dist(lxml)
BuildRequires:  python3dist(jinja2)
BuildRequires:  firewalld-filesystem
BuildRequires:  libseccomp-devel
BuildRequires:  meson >= 0.43
BuildRequires:  gettext
# We use RUNNING_ON_VALGRIND in tests, so the headers need to be available
BuildRequires:  valgrind-devel
BuildRequires:  pkgconfig(bash-completion)
BuildRequires:  pkgconfig(tss2-esys)
BuildRequires:  pkgconfig(tss2-rc)
BuildRequires:  pkgconfig(tss2-mu)
BuildRequires:  perl
BuildRequires:  perl(IPC::SysV)

Requires(post): coreutils
Requires(post): sed
Requires(post): acl
Requires(post): grep
# systemd-machine-id-setup requires libssl
Requires(post): openssl-libs
Requires(pre):  coreutils
Requires(pre):  /usr/bin/getent
Requires(pre):  /usr/sbin/groupadd
Requires:       dbus >= 1.9.18
Requires:       %{name}-pam = %{version}-%{release}
Requires:       %{name}-rpm-macros = %{version}-%{release}
Requires:       %{name}-libs = %{version}-%{release}
Requires:       util-linux
Provides:       /bin/systemctl
Provides:       /sbin/shutdown
Provides:       syslog
Provides:       systemd-units = %{version}-%{release}
Obsoletes:      system-setup-keyboard < 0.9
Provides:       system-setup-keyboard = 0.9
# systemd-sysv-convert was removed in f20: https://fedorahosted.org/fpc/ticket/308
Obsoletes:      systemd-sysv < 206
# self-obsoletes so that dnf will install new subpackages on upgrade (#1260394)
Obsoletes:      %{name} < 246.6-2
Provides:       systemd-sysv = 206
Conflicts:      initscripts < 9.56.1
%if 0%{?fedora}
Conflicts:      fedora-release < 23-0.12
%endif
Obsoletes:      timedatex < 0.6-3
Provides:       timedatex = 0.6-3
Conflicts:      %{name}-standalone-tmpfiles < %{version}-%{release}^
Obsoletes:      %{name}-standalone-tmpfiles < %{version}-%{release}^
Conflicts:      %{name}-standalone-sysusers < %{version}-%{release}^
Obsoletes:      %{name}-standalone-sysusers < %{version}-%{release}^

# Requires deps for stuff that is dlopen()ed
Requires:       pcre2%{?_isa}

%description
systemd is a system and service manager that runs as PID 1 and starts
the rest of the system. It provides aggressive parallelization
capabilities, uses socket and D-Bus activation for starting services,
offers on-demand starting of daemons, keeps track of processes using
Linux control groups, maintains mount and automount points, and
implements an elaborate transactional dependency-based service control
logic. systemd supports SysV and LSB init scripts and works as a
replacement for sysvinit. Other parts of this package are a logging daemon,
utilities to control basic system configuration like the hostname,
date, locale, maintain a list of logged-in users, system accounts,
runtime directories and settings, and daemons to manage simple network
configuration, network time synchronization, log forwarding, and name
resolution.
%if 0%{?stable}
This package was built from the %{version}-stable branch of systemd.
%endif

%package libs
Summary:        systemd libraries
License:        LGPLv2+ and MIT
Obsoletes:      libudev < 183
Obsoletes:      systemd < 185-4
Conflicts:      systemd < 185-4
Obsoletes:      systemd-compat-libs < 230
Obsoletes:      nss-myhostname < 0.4
Provides:       nss-myhostname = 0.4
Provides:       nss-myhostname%{_isa} = 0.4
Requires(post): coreutils
Requires(post): sed
Requires(post): grep
Requires(post): /usr/bin/getent

%description libs
Libraries for systemd and udev.

%package pam
Summary:        systemd PAM module
Requires:       %{name} = %{version}-%{release}

%description pam
Systemd PAM module registers the session with systemd-logind.

%package rpm-macros
Summary:        Macros that define paths and scriptlets related to systemd
BuildArch:      noarch

%description rpm-macros
Just the definitions of rpm macros.

See
https://docs.fedoraproject.org/en-US/packaging-guidelines/Scriptlets/#_systemd
for information how to use those macros.

%package devel
Summary:        Development headers for systemd
License:        LGPLv2+ and MIT
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Provides:       libudev-devel = %{version}
Provides:       libudev-devel%{_isa} = %{version}
Obsoletes:      libudev-devel < 183
# Fake dependency to make sure systemd-pam is pulled into multilib (#1414153)
Requires:       %{name}-pam = %{version}-%{release}

%description devel
Development headers and auxiliary files for developing applications linking
to libudev or libsystemd.

%package udev
Summary: Rule-based device node and kernel event manager
License:        LGPLv2+

Requires:       systemd%{?_isa} = %{version}-%{release}
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
Requires(post): grep
Requires:       kmod >= 18-4
# https://bodhi.fedoraproject.org/updates/FEDORA-2020-dd43dd05b1
Obsoletes:      systemd < 245.6-1
Provides:       udev = %{version}
Provides:       udev%{_isa} = %{version}
Obsoletes:      udev < 183

# https://bugzilla.redhat.com/show_bug.cgi?id=1377733#c9
Suggests:       systemd-bootchart
# https://bugzilla.redhat.com/show_bug.cgi?id=1408878
Requires:       kbd

# Requires deps for stuff that is dlopen()ed
Requires:       cryptsetup-libs%{?_isa}
# https://bugzilla.redhat.com/show_bug.cgi?id=2017541
Requires:       tpm2-tss%{?_isa}

# https://bugzilla.redhat.com/show_bug.cgi?id=1753381
Provides:       u2f-hidraw-policy = 1.0.2-40
Obsoletes:      u2f-hidraw-policy < 1.0.2-40

%description udev
This package contains systemd-udev and the rules and hardware database
needed to manage device nodes. This package is necessary on physical
machines and in virtual machines, but not in containers.

%package container
# Name is the same as in Debian
Summary: Tools for containers and VMs
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
# obsolete parent package so that dnf will install new subpackage on upgrade (#1260394)
Obsoletes:      %{name} < 229-5
License:        LGPLv2+

%description container
Systemd tools to spawn and manage containers and virtual machines.

This package contains systemd-nspawn, machinectl, systemd-machined,
and systemd-importd.

%package journal-remote
# Name is the same as in Debian
Summary:        Tools to send journal events over the network
Requires:       %{name}%{?_isa} = %{version}-%{release}
License:        LGPLv2+
Requires(pre):    /usr/bin/getent
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd
Requires:       firewalld-filesystem
Provides:       %{name}-journal-gateway = %{version}-%{release}
Provides:       %{name}-journal-gateway%{_isa} = %{version}-%{release}
Obsoletes:      %{name}-journal-gateway < 227-7

%description journal-remote
Programs to forward journal entries over the network, using encrypted HTTP,
and to write journal files from serialized journal contents.

This package contains systemd-journal-gatewayd,
systemd-journal-remote, and systemd-journal-upload.

%package resolved
Summary:        System daemon that provides network name resolution to local applications
Requires:       %{name}%{?_isa} = %{version}-%{release}
License:        LGPLv2+

%description resolved
systemd-resolved is a system service that provides network name
resolution to local applications. It implements a caching and
validating DNS/DNSSEC stub resolver, as well as an LLMNR and
MulticastDNS resolver and responder.

%package oomd
Summary:        A userspace out-of-memory (OOM) killer
Requires:       %{name}%{?_isa} = %{version}-%{release}
License:        LGPLv2+
Provides:       %{name}-oomd-defaults = %{version}-%{release}

%description oomd
systemd-oomd is a system service that uses cgroups-v2 and pressure stall
information (PSI) to monitor and take action on processes before an OOM
occurs in kernel space.

%package standalone-tmpfiles
Summary:       Standalone tmpfiles binary for use in non-systemd systems
RemovePathPostfixes: .standalone

%description standalone-tmpfiles
Standalone tmpfiles binary with no dependencies on the systemd-shared library
or other libraries from systemd-libs. This package conflicts with the main
systemd package and is meant for use in non-systemd systems.

%package standalone-sysusers
Summary:       Standalone sysusers binary for use in non-systemd systems
RemovePathPostfixes: .standalone

%description standalone-sysusers
Standalone sysusers binary with no dependencies on the systemd-shared library
or other libraries from systemd-libs. This package conflicts with the main
systemd package and is meant for use in non-systemd systems.

%prep
%autosetup -n %{?commit:%{name}%{?stable:-stable}-%{commit}}%{!?commit:%{name}%{?stable:-stable}-%{version_no_tilde}} -p1

%build
%define ntpvendor %(source /etc/os-release; echo ${ID})
%{!?ntpvendor: echo 'NTP vendor zone is not set!'; exit 1}

CONFIGURE_OPTS=(
        -Dmode=release
        -Dsysvinit-path=/etc/rc.d/init.d
        -Drc-local=/etc/rc.d/rc.local
        -Dntp-servers='0.%{ntpvendor}.pool.ntp.org 1.%{ntpvendor}.pool.ntp.org 2.%{ntpvendor}.pool.ntp.org 3.%{ntpvendor}.pool.ntp.org'
        -Ddns-servers=
        -Duser-path=/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin
        -Dservice-watchdog=3min
        -Ddev-kvm-mode=0666
        -Dkmod=true
        -Dxkbcommon=true
        -Dblkid=true
        -Dfdisk=true
        -Dseccomp=true
        -Dima=true
        -Dselinux=true
        -Dapparmor=false
        -Dpolkit=true
        -Dxz=true
        -Dzlib=true
        -Dbzip2=true
        -Dlz4=true
        -Dzstd=true
        -Dpam=true
        -Dacl=true
        -Dsmack=true
        -Dopenssl=true
        -Dcryptolib=openssl
        -Dp11kit=true
        -Dgcrypt=true
        -Daudit=true
        -Delfutils=true
%if %{without bootstrap}
        -Dlibcryptsetup=true
%else
        -Dlibcryptsetup=false
%endif
        -Delfutils=true
        -Dpwquality=false
        -Dqrencode=false
        -Dgnutls=true
        -Dmicrohttpd=true
        -Dlibidn2=true
        -Dlibiptc=false
        -Dlibcurl=true
        -Dlibfido2=false
        -Dgnu-efi=false
        -Dtpm=true
        -Dtpm2=true
        -Dhwdb=true
        -Dsysusers=true
        -Dstandalone-binaries=true
        -Ddefault-kill-user-processes=false
        -Dtests=unsafe
        -Dinstall-tests=false
        -Dtty-gid=5
        -Dusers-gid=100
        -Dnobody-user=nobody
        -Dnobody-group=nobody
        -Dcompat-mutable-uid-boundaries=true
        -Dsplit-usr=false
        -Dsplit-bin=true
%if %{with lto}
        -Db_lto=true
%else
        -Db_lto=false
%endif
        -Db_ndebug=false
        -Dman=true
        -Dversion-tag=%{version}-%{release}
%if 0%{?fedora}
        -Dfallback-hostname=fedora
%else
        -Dfallback-hostname=localhost
%endif
        -Ddefault-dnssec=no
        # https://bugzilla.redhat.com/show_bug.cgi?id=1867830
        -Ddefault-mdns=no
        -Ddefault-llmnr=resolve
        -Doomd=true
        -Dtimesyncd=false
        -Dhomed=false
        -Duserdb=false
        -Dportabled=false
        -Dnetworkd=false
        -Dsupport-url=https://access.redhat.com/support
)

%if %{without lto}
%global _lto_cflags %nil
%endif

%meson "${CONFIGURE_OPTS[@]}"

new_triggers=%{_vpath_builddir}/src/rpm/triggers.systemd.sh
if ! diff -u %{SOURCE1} ${new_triggers}; then
   echo -e "\n\n\nWARNING: triggers.systemd in Source1 is different!"
   echo -e "      cp $PWD/${new_triggers} %{SOURCE1}\n\n\n"
   sleep 5
fi

%meson_build

%install
%meson_install

# udev links
mkdir -p %{buildroot}/%{_sbindir}
ln -sf ../bin/udevadm %{buildroot}%{_sbindir}/udevadm

# Compatiblity and documentation files
touch %{buildroot}/etc/crypttab
chmod 600 %{buildroot}/etc/crypttab

# /etc/initab
install -Dm0644 -t %{buildroot}/etc/ %{SOURCE5}

# /etc/sysctl.conf compat
install -Dm0644 %{SOURCE6} %{buildroot}/etc/sysctl.conf
ln -s ../sysctl.conf %{buildroot}/etc/sysctl.d/99-sysctl.conf

# Make sure these directories are properly owned
mkdir -p %{buildroot}%{system_unit_dir}/basic.target.wants
mkdir -p %{buildroot}%{system_unit_dir}/default.target.wants
mkdir -p %{buildroot}%{system_unit_dir}/dbus.target.wants
mkdir -p %{buildroot}%{system_unit_dir}/syslog.target.wants
mkdir -p %{buildroot}/run
mkdir -p %{buildroot}%{_localstatedir}/log
touch %{buildroot}%{_localstatedir}/log/lastlog
chmod 0664 %{buildroot}%{_localstatedir}/log/lastlog
touch %{buildroot}/run/utmp
touch %{buildroot}%{_localstatedir}/log/{w,b}tmp

# Make sure the user generators dir exists too
mkdir -p %{buildroot}%{pkgdir}/system-generators
mkdir -p %{buildroot}%{pkgdir}/user-generators

# Create new-style configuration files so that we can ghost-own them
touch %{buildroot}%{_sysconfdir}/hostname
touch %{buildroot}%{_sysconfdir}/vconsole.conf
touch %{buildroot}%{_sysconfdir}/locale.conf
touch %{buildroot}%{_sysconfdir}/machine-id
touch %{buildroot}%{_sysconfdir}/machine-info
touch %{buildroot}%{_sysconfdir}/localtime
mkdir -p %{buildroot}%{_sysconfdir}/X11/xorg.conf.d
touch %{buildroot}%{_sysconfdir}/X11/xorg.conf.d/00-keyboard.conf

# Make sure the shutdown/sleep drop-in dirs exist
mkdir -p %{buildroot}%{pkgdir}/system-shutdown/
mkdir -p %{buildroot}%{pkgdir}/system-sleep/

# Make sure directories in /var exist
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/coredump
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/catalog
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/backlight
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/rfkill
mkdir -p %{buildroot}%{_localstatedir}/lib/systemd/linger
mkdir -p %{buildroot}%{_localstatedir}/lib/private
mkdir -p %{buildroot}%{_localstatedir}/log/private
mkdir -p %{buildroot}%{_localstatedir}/cache/private
mkdir -p %{buildroot}%{_localstatedir}/lib/private/systemd/journal-upload
ln -s ../private/systemd/journal-upload %{buildroot}%{_localstatedir}/lib/systemd/journal-upload
mkdir -p %{buildroot}%{_localstatedir}/log/journal
touch %{buildroot}%{_localstatedir}/lib/systemd/catalog/database
touch %{buildroot}%{_sysconfdir}/udev/hwdb.bin
touch %{buildroot}%{_localstatedir}/lib/systemd/random-seed
touch %{buildroot}%{_localstatedir}/lib/private/systemd/journal-upload/state

# Install rc.local
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/
install -m 0644 %{SOURCE25} %{buildroot}%{_sysconfdir}/rc.d/rc.local
ln -s rc.d/rc.local %{buildroot}%{_sysconfdir}/rc.local

# Install yum protection fragment
install -Dm0644 %{SOURCE4} %{buildroot}/etc/dnf/protected.d/systemd.conf

install -Dm0644 -t %{buildroot}/usr/lib/firewalld/services/ %{SOURCE7} %{SOURCE8}

# Restore systemd-user pam config from before "removal of Fedora-specific bits"
install -Dm0644 -t %{buildroot}/etc/pam.d/ %{SOURCE12}

# Install additional docs
# https://bugzilla.redhat.com/show_bug.cgi?id=1234951
install -Dm0644 -t %{buildroot}%{_pkgdocdir}/ %{SOURCE9}

# https://bugzilla.redhat.com/show_bug.cgi?id=1378974
install -Dm0644 -t %{buildroot}%{system_unit_dir}/systemd-udev-trigger.service.d/ %{SOURCE10}

# A temporary work-around for https://bugzilla.redhat.com/show_bug.cgi?id=1663040
mkdir -p %{buildroot}%{system_unit_dir}/systemd-hostnamed.service.d/
cat >%{buildroot}%{system_unit_dir}/systemd-hostnamed.service.d/disable-privatedevices.conf <<EOF
[Service]
PrivateDevices=no
EOF

install -Dm0755 -t %{buildroot}%{_prefix}/lib/kernel/install.d/ %{SOURCE11}

install -Dm0644 -t %{buildroot}%{_prefix}/lib/systemd/ %{SOURCE13}

install -D -t %{buildroot}/usr/lib/systemd/ %{SOURCE3}

# systemd-oomd default configuration
install -Dm0644 -t %{buildroot}%{_prefix}/lib/systemd/oomd.conf.d/ %{SOURCE14}
install -Dm0644 -t %{buildroot}%{system_unit_dir}/-.slice.d/ %{SOURCE15}
install -Dm0644 -t %{buildroot}%{system_unit_dir}/user@.service.d/ %{SOURCE16}

install -m 0644 -D -t %{buildroot}%{_rpmconfigdir}/macros.d/ %{SOURCE21}
install -m 0644 -D -t %{buildroot}%{_rpmconfigdir}/fileattrs/ %{SOURCE22}
install -m 0755 -D -t %{buildroot}%{_rpmconfigdir}/ %{SOURCE23}
install -m 0755 -D -t %{buildroot}%{_rpmconfigdir}/ %{SOURCE24}

%find_lang %{name}

# Split files in build root into rpms. See split-files.py for the
# rules towards the end, anything which is an exception needs a line
# here.
python3 %{SOURCE2} %buildroot <<EOF
%ghost %config(noreplace) /etc/crypttab
%ghost /etc/udev/hwdb.bin
/etc/inittab
/usr/lib/systemd/purge-nobody-user
%ghost %config(noreplace) /etc/vconsole.conf
%ghost %config(noreplace) /etc/X11/xorg.conf.d/00-keyboard.conf
%ghost %attr(0664,root,utmp) /run/utmp
%ghost %attr(0664,root,utmp) /var/log/wtmp
%ghost %attr(0600,root,utmp) /var/log/btmp
%ghost %attr(0664,root,utmp) %verify(not md5 size mtime) /var/log/lastlog
%ghost %config(noreplace) /etc/hostname
%ghost %config(noreplace) /etc/localtime
%ghost %config(noreplace) /etc/locale.conf
%ghost %config(noreplace) /etc/machine-id
%ghost %config(noreplace) /etc/machine-info
%config(noreplace) %{_sysconfdir}/rc.d/rc.local
%{_sysconfdir}/rc.local
%ghost %attr(0700,root,root) %dir /var/cache/private
%ghost %attr(0700,root,root) %dir /var/lib/private
%ghost %dir /var/lib/private/systemd
%ghost %dir /var/lib/private/systemd/journal-upload
%ghost /var/lib/private/systemd/journal-upload/state
%ghost %dir /var/lib/systemd/backlight
%ghost /var/lib/systemd/catalog/database
%ghost %dir /var/lib/systemd/coredump
%ghost /var/lib/systemd/journal-upload
%ghost %dir /var/lib/systemd/linger
%ghost /var/lib/systemd/random-seed
%ghost %dir /var/lib/systemd/rfkill
%ghost %dir /var/log/journal
%ghost %dir /var/log/journal/remote
%ghost %attr(0700,root,root) %dir /var/log/private
EOF

%check
%if %{with tests}
meson test -C %{_vpath_builddir} -t 6 --print-errorlogs
%endif

#############################################################################################

%include %{SOURCE1}

%pre
getent group cdrom &>/dev/null || groupadd -r -g 11 cdrom &>/dev/null || :
getent group utmp &>/dev/null || groupadd -r -g 22 utmp &>/dev/null || :
getent group tape &>/dev/null || groupadd -r -g 33 tape &>/dev/null || :
getent group dialout &>/dev/null || groupadd -r -g 18 dialout &>/dev/null || :
getent group input &>/dev/null || groupadd -r input &>/dev/null || :
getent group kvm &>/dev/null || groupadd -r -g 36 kvm &>/dev/null || :
getent group render &>/dev/null || groupadd -r render &>/dev/null || :
getent group systemd-journal &>/dev/null || groupadd -r -g 190 systemd-journal 2>&1 || :

getent group systemd-coredump &>/dev/null || groupadd -r systemd-coredump 2>&1 || :
getent passwd systemd-coredump &>/dev/null || useradd -r -l -g systemd-coredump -d / -s /sbin/nologin -c "systemd Core Dumper" systemd-coredump &>/dev/null || :


%post
systemd-machine-id-setup &>/dev/null || :

systemctl daemon-reexec &>/dev/null || {
  # systemd v239 had bug #9553 in D-Bus authentication of the private socket,
  # which was later fixed in v240 by #9625.
  #
  # The end result is that a `systemctl daemon-reexec` call as root will fail
  # when upgrading from systemd v239, which means the system will not start
  # running the new version of systemd after this post install script runs.
  #
  # To work around this issue, let's fall back to using a `kill -TERM 1` to
  # re-execute the daemon when the `systemctl daemon-reexec` call fails.
  #
  # In order to prevent issues when the reason why the daemon-reexec failed is
  # not the aforementioned bug, let's only use this fallback when:
  #   - we're upgrading this RPM package; and
  #   - we confirm that systemd is running as PID1 on this system.
  if [ $1 -gt 1 ] && [ -d /run/systemd/system ] ; then
    kill -TERM 1 &>/dev/null || :
  fi
}

if [ $1 -eq 1 ]; then
   [ -w %{_localstatedir} ] && journalctl --update-catalog || :
   systemd-tmpfiles --create &>/dev/null || :
fi

# Make sure new journal files will be owned by the "systemd-journal" group
machine_id=$(cat /etc/machine-id 2>/dev/null)
chgrp systemd-journal /{run,var}/log/journal/{,${machine_id}} &>/dev/null || :
chmod g+s /{run,var}/log/journal/{,${machine_id}} &>/dev/null || :

# Apply ACL to the journal directory
setfacl -Rnm g:wheel:rx,d:g:wheel:rx,g:adm:rx,d:g:adm:rx /var/log/journal/ &>/dev/null || :

[ $1 -eq 1 ] || exit 0

# We reset the enablement of all services upon initial installation
# https://bugzilla.redhat.com/show_bug.cgi?id=1118740#c23
# This will fix up enablement of any preset services that got installed
# before systemd due to rpm ordering problems:
# https://bugzilla.redhat.com/show_bug.cgi?id=1647172.
# We also do this for user units, see
# https://fedoraproject.org/wiki/Changes/Systemd_presets_for_user_units.
systemctl preset-all &>/dev/null || :
systemctl --global preset-all &>/dev/null || :

%postun
if [ $1 -eq 1 ]; then
   [ -w %{_localstatedir} ] && journalctl --update-catalog || :
   systemd-tmpfiles --create &>/dev/null || :
fi

%systemd_postun_with_restart systemd-timedated.service systemd-hostnamed.service systemd-journald.service systemd-localed.service

%post libs
%{?ldconfig}

function mod_nss() {
    if [ -f "$1" ] ; then
        # Add nss-systemd to passwd and group
        grep -E -q '^(passwd|group):.* systemd' "$1" ||
        sed -i.bak -r -e '
                s/^(passwd|group):(.*)/\1:\2 systemd/
                ' "$1" &>/dev/null || :
    fi
}

FILE="$(readlink /etc/nsswitch.conf || echo /etc/nsswitch.conf)"
if [ "$FILE" = "/etc/authselect/nsswitch.conf" ] && authselect check &>/dev/null; then
        mod_nss "/etc/authselect/user-nsswitch.conf"
        authselect apply-changes &> /dev/null || :
else
        mod_nss "$FILE"
        # also apply the same changes to user-nsswitch.conf to affect
        # possible future authselect configuration
        mod_nss "/etc/authselect/user-nsswitch.conf"
fi

# check if nobody or nfsnobody is defined
export SYSTEMD_NSS_BYPASS_SYNTHETIC=1
if getent passwd nfsnobody &>/dev/null; then
   test -f /etc/systemd/dont-synthesize-nobody || {
       echo 'Detected system with nfsnobody defined, creating /etc/systemd/dont-synthesize-nobody'
       mkdir -p /etc/systemd || :
       : >/etc/systemd/dont-synthesize-nobody || :
   }
elif getent passwd nobody 2>/dev/null | grep -v 'nobody:[x*]:65534:65534:.*:/:/sbin/nologin' &>/dev/null; then
   test -f /etc/systemd/dont-synthesize-nobody || {
       echo 'Detected system with incompatible nobody defined, creating /etc/systemd/dont-synthesize-nobody'
       mkdir -p /etc/systemd || :
       : >/etc/systemd/dont-synthesize-nobody || :
   }
fi

%{?ldconfig:%postun libs -p %ldconfig}

%global udev_services systemd-udev{d,-settle,-trigger}.service systemd-udevd-{control,kernel}.socket

%post udev
# Move old stuff around in /var/lib
mv %{_localstatedir}/lib/random-seed %{_localstatedir}/lib/systemd/random-seed &>/dev/null
mv %{_localstatedir}/lib/backlight %{_localstatedir}/lib/systemd/backlight &>/dev/null

udevadm hwdb --update &>/dev/null

%systemd_post %udev_services

# Try to save the random seed, but don't complain if /dev/urandom is unavailable
/usr/lib/systemd/systemd-random-seed save 2>&1 | \
    grep -v 'Failed to open /dev/urandom' || :

# Replace obsolete keymaps
# https://bugzilla.redhat.com/show_bug.cgi?id=1151958
grep -q -E '^KEYMAP="?fi-latin[19]"?' /etc/vconsole.conf 2>/dev/null &&
    sed -i.rpm.bak -r 's/^KEYMAP="?fi-latin[19]"?/KEYMAP="fi"/' /etc/vconsole.conf || :

%preun udev
%systemd_preun %udev_services

%postun udev
# Restart some services.
# Others are either oneshot services, or sockets, and restarting them causes issues (#1378974)
%systemd_postun_with_restart systemd-udevd.service

%pre journal-remote
getent group systemd-journal-remote &>/dev/null || groupadd -r systemd-journal-remote 2>&1 || :
getent passwd systemd-journal-remote &>/dev/null || useradd -r -l -g systemd-journal-remote -d %{_localstatedir}/log/journal/remote -s /sbin/nologin -c "Journal Remote" systemd-journal-remote &>/dev/null || :

%post journal-remote
%systemd_post systemd-journal-gatewayd.socket systemd-journal-gatewayd.service systemd-journal-remote.socket systemd-journal-remote.service systemd-journal-upload.service
%firewalld_reload

%preun journal-remote
%systemd_preun systemd-journal-gatewayd.socket systemd-journal-gatewayd.service systemd-journal-remote.socket systemd-journal-remote.service systemd-journal-upload.service
if [ $1 -eq 1 ] ; then
    if [ -f %{_localstatedir}/lib/systemd/journal-upload/state -a ! -L %{_localstatedir}/lib/systemd/journal-upload ] ; then
        mkdir -p %{_localstatedir}/lib/private/systemd/journal-upload
        mv %{_localstatedir}/lib/systemd/journal-upload/state %{_localstatedir}/lib/private/systemd/journal-upload/.
        rmdir %{_localstatedir}/lib/systemd/journal-upload || :
    fi
fi

%postun journal-remote
%systemd_postun_with_restart systemd-journal-gatewayd.service systemd-journal-remote.service systemd-journal-upload.service
%firewalld_reload

%pre resolved
getent group systemd-resolve &>/dev/null || groupadd -r -g 193 systemd-resolve 2>&1 || :
getent passwd systemd-resolve &>/dev/null || useradd -r -u 193 -l -g systemd-resolve -d / -s /sbin/nologin -c "systemd Resolver" systemd-resolve &>/dev/null || :

%preun resolved
%systemd_preun systemd-resolved.service

%post resolved
%systemd_post systemd-resolved.service

%postun resolved
%systemd_postun_with_restart systemd-resolved.service

%pre oomd
getent group systemd-oom &>/dev/null || groupadd -r systemd-oom 2>&1 || :
getent passwd systemd-oom &>/dev/null || useradd -r -l -g systemd-oom -d / -s /sbin/nologin -c "systemd Userspace OOM Killer" systemd-oom &>/dev/null || :

%preun oomd
%systemd_preun systemd-oomd.service

%post oomd
%systemd_post systemd-oomd.service

%postun oomd
%systemd_postun_with_restart systemd-oomd.service

%global _docdir_fmt %{name}

%files -f %{name}.lang -f .file-list-rest
%doc %{_pkgdocdir}
%exclude %{_pkgdocdir}/LICENSE.*
%license LICENSE.GPL2 LICENSE.LGPL2.1
%ghost %dir %attr(0755,-,-) /etc/systemd/system/basic.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/bluetooth.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/default.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/getty.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/graphical.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/local-fs.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/machines.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/multi-user.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/network-online.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/printer.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/remote-fs.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/sockets.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/sysinit.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/system-update.target.wants
%ghost %dir %attr(0755,-,-) /etc/systemd/system/timers.target.wants
%ghost %dir %attr(0755,-,-) /var/lib/rpm-state/systemd

%files libs -f .file-list-libs
%license LICENSE.LGPL2.1

%files pam -f .file-list-pam

%files rpm-macros -f .file-list-rpm-macros

%files devel -f .file-list-devel

%files udev -f .file-list-udev

%files container -f .file-list-container

%files journal-remote -f .file-list-remote

%files resolved -f .file-list-resolved

%files oomd -f .file-list-oomd

%files standalone-tmpfiles -f .file-list-standalone-tmpfiles

%files standalone-sysusers -f .file-list-standalone-sysusers

%changelog
* Fri Sep 23 2022 systemd maintenance team <systemd-maint@redhat.com> - 250-12
- core/load-fragment: move config_parse_sec_fix_0 to src/shared (#2100464)
- logind: add option to stop idle sessions after specified timeout (#2100464)
- tree-wide: fix typo (#2100464)
- test: several cleanups for TEST-35-LOGIN (#2100464)
- test: start test user session before idle action setting is changed (#2100464)
- test: ensure cleanup functions return success (#2100464)
- test: add test for org.freedesktop.login1.Session SetType (#2100464)
- test: add a simple test for list-users (#2100464)
- test: merge grep | awk calls (#2100464)
- test: wait for user service or slice to be finished (#2100464)
- test: terminate session and user on cleanup (#2100464)
- test: do not restart getty@tty2 automatically (#2100464)
- tests: add test for StopIdleSessionSec= option (#2100464)
- logind: schedule idle check full interval from now if we couldn't figure out atime timestamp (#2100464)

* Thu Aug 25 2022 systemd maintenance team <systemd-maint@redhat.com> - 250-11
- scope: allow unprivileged delegation on scopes (#2120604)
- udev/net_id: add "rhel-9.1" naming scheme (#2121144)

* Mon Aug 22 2022 systemd maintenance team <systemd-maint@redhat.com> - 250-10
- shared/install: fix crash when reenable is called without --root (#2120222)

* Thu Aug 18 2022 systemd maintenance team <systemd-maint@redhat.com> - 250-9
- Revert "shared/install: create relative symlinks for enablement and aliasing" (#2118668)
- glyph-util: add new glyphs for up/down arrows (#2118297)
- tree-wide: allow ASCII fallback for → in logs (#2118297)
- tree-wide: allow ASCII fallback for … in logs (#2118297)
- core: allow to set default timeout for devices (#2116681)
- man: document DefaultDeviceTimeoutSec= (#2116681)
- man: update dbus docs (#2116681)
- hwdb: 60-keyboard: Fix volume-button mapping on Asus TF103C (#2087778)
- hwdb: CH Pro Pedals not classified correctly due to no buttons (#2087778)
- hwdb: Add accel orientation quirk for the GPD Pocket 3 (#2087778)
- hostname: Allow overriding the chassis type from hwdb (#2087778)
- hwdb: Add Microsoft Surface Pro 1 chassis quirk (#2087778)
- hwdb: treat logitech craft keyboard as a keyboard (#2087778)
- test: frequency in mouse DPI is optional (#2087778)
- hwdb: add two Elecom trackballs (#2087778)
- hwdb: add new database file for PDA devices (#2087778)
- hwdb: add support for Surface Laptop 2 & 3 (#22303) (#2087778)
- hwdb: add HP calculators (#2087778)
- hwbd: 60-sensor.hwdb: Add Pipo W2Pro (#2087778)
- hwdb: 60-keyboard: Support the buttons on CZC P10T tablet (#2087778)
- hwdb: add CST Laser Trackball (#22583) (#2087778)
- hwdb: Force release calculator key on all HP OMEN laptops (#2087778)
- Add support for NEC VersaPro VG-S (#2087778)
- Fix mic mute on Acer TravelMate B311-31 (#22677) (#2087778)
- Add AV production controllers to hwdb and add uaccess (#2087778)
- hwdb: Add AV production access to Elgado Stream Deck devices (#2087778)
- Add HP Elitebook 2760p support (#22766) (#2087778)
- hwdb: Add mic mute key mapping for HP Elite x360 (#2087778)
- hwdb: fix parser to work with newer pyparsing (#2087778)
- hwdb: update for v251 (#2087778)
- hwdb: update autosuspend entries (#2087778)
- hwdb: drop boilerplate about match patterns being unstable (#2087778)
- hwdb: Update 60-keyboard.hwdb (#23074) (#2087778)
- hwdb: 60-keyboard: Add Acer Aspire One AO532h keymappings (#2087778)
- hwdb 60-keyboard Add HP/Compaq KBR0133 (#2087778)
- hwdb: add resolutions for the Vaio FE14 touchpad (#23136) (#2087778)
- hwdb: Remap micmute to f20 for ASUS WMI hotkeys (#2087778)
- hwdb: Fix rotation for HP Pro Tablet 408 G1 (#2087778)
- hwdb: add keyboard mapping for HP ProBook 11G2 (#2087778)
- hwdb: make sure "ninja update-hwdb" works on f35 (#2087778)
- hwbd: run "update-hwdb" for v251-rc2 (#2087778)
- hwdb: run "ninja update-hwdb-autosuspend" for v251-rc2 (#2087778)
- Fix orientation detection for Asus Transformer T100TAF, copied T100TA rule (#2087778)
- Fix orientation detection for HP Pavilion X2 10-k010nr (#2087778)
- fix typo (#2087778)
- Adding a description of the keyboard shortcut Fn+F12 for the HP EliteBook 845 G7 device. (#23253) (#2087778)
- hwdb: run "update-hwdb" (#2087778)
- hwdb: add rammus accelerometer support (#2087778)
- Add support to set autosuspend delay via hwdb (#2087778)
- Set autosuspend delay for Fibocom LG850-GL (#2087778)
- Add HUION Inspiroy H420X to hwdb (#2087778)
- hwdb: run 'update-hwdb' for v251-rc3 (#2087778)
- hwdb: add touchpad parameters for Lenovo T15g Gen1 (#23373) (#2087778)
-  hwdb: Add accel orientation for the I15-TG (#2087778)
- hwdb: fix accelerometer mount matrix for Aquarius NS483 (#2087778)
- hwdb: Add Google Hangouts Meet speakermic (#2087778)
- hwdb: update via ninja -C build update-hwdb (#2087778)
- hwdb: Add Google Meet speakermic (#2087778)
- hwdb: Add accel orientation quirk for the Aya Neo Next (#2087778)
- hwdb: Add HP Dev One (#2087778)
- hwdb: analyzers: remove generic "STM Device in DFU Mode" (#2087778)
- hwdb: Add Lenovo ThinkPad C13 Yoga (#2087778)
- Fix automatic screen rotation for Asus Transformer T100TAM (#2087778)
- hwdb: Add Acer Aspire A317-33 (#24050) (#2087778)
- Add ACCEL_MOUNT_MATRIX for OXP Mini (#2087778)
- Added DERE DBook D10 (#24173) (#2087778)
- hwdb: analyzers: Clarify the type of devices we want listed (#2087778)
- hwdb: Add Greaseweazle "drives" to the list of analyzers (#2087778)
- hwdb: Apply existing accel orientation quirk to all Chromebooks (#2087778)

* Wed Jul 20 2022 systemd maintenance team <systemd-maint@redhat.com> - 250-8
- core: shorten long unit names that are based on paths and append path hash at the end (#2083493)
- tests: add test case for long unit names (#2083493)
- tests: reflect that we can now handle devices with very long sysfs paths (#2083493)
- test: extend the "hashed" unit names coverage a bit (#2083493)
- Revert "kernel-install: also remove modules.builtin.alias.bin" (#2065061)
- Revert "kernel-install: prefer /boot over /boot/efi for $BOOT_ROOT" (#2065061)
- kernel-install: 50-depmod: port to /bin/sh (#2065061)
- kernel-install: 90-loaderentry: port to /bin/sh (#2065061)
- kernel-install: fix shellcheck (#2065061)
- kernel-install: port to /bin/sh (#2065061)
- kernel-install: 90-loaderentry: error out on nonexistent initrds instead of swallowing them quietly (#2065061)
- kernel-install: don't pull out KERNEL_IMAGE (#2065061)
- kernel-install: prefer /boot over /boot/efi for $BOOT_ROOT (#2065061)
- kernel-install: also remove modules.builtin.alias.bin (#2065061)
- kernel-install: add new variable $KERNEL_INSTALL_INITRD_GENERATOR (#2065061)
- kernel-install: k-i already creates $ENTRY_DIR_ABS, no need to do it again (#2065061)
- kernel-install: prefix errors with "Error:", exit immediately (#2065061)
- kernel-install: add "$KERNEL_INSTALL_STAGING_AREA" directory (#2065061)
- kernel-install: add missing log line (#2065061)
- kernel-install: don't try to persist used machine ID locally (#2065061)
- kernel-install: add a new $ENTRY_TOKEN variable for naming boot entries (#2065061)
- kernel-install: only generate systemd.boot_id= in kernel command line if used for naming the boot loader spec files/dirs (#2065061)
- kernel-install: search harder for kernel image/initrd drop-in dir (#2065061)
- kernel-install: add new "inspect" verb, showing paths and parameters we discovered (#2065061)
- ci(Mergify): configuration update (#2087652)
- ci(Mergify): fix copy&paste bug (#2087652)
- shared: Fix memory leak in bus_append_execute_property() (#2087652)
- fuzz: no longer skip empty files (#2087652)
- networkctl: open the bus just once (#2087652)
- json: align table (#2087652)
- fuzz-json: optionally allow logging and output (#2087652)
- shared/json: reduce scope of variables (#2087652)
- fuzz-json: also do sorting and normalizing and other easy calls (#2087652)
- shared/json: wrap long comments (#2087652)
- shared/json: fix memory leak on failed normalization (#2087652)
- shared/json: add helper to ref first, unref second (#2087652)
- basic/alloc-util: remove unnecessary parens (#2087652)
- fuzz-json: also try self-merge operations (#2087652)
- shared/json: fix another memleak in normalization (#2087652)
- shared/json: fix memleak in sort (#2087652)
- execute: fix resource leak (#2087652)
- tests: ignore dbus-broker-launcher (#2087652)
- core/timer: fix memleak (#2087652)
- timedatectl: fix a memory leak (#2087652)
- test: fix file descriptor leak in test-psi-util (#2087652)
- test: fix file descriptor leak in test-tmpfiles.c (#2087652)
- test: fix file descriptor leak in test-fs-util (#2087652)
- test: fix file descriptor leak in test-oomd-util (#2087652)
- test: fix file descriptor leak in test-catalog (#2087652)
- test: make masking of supplementary services configurable (#2087652)
- test: fuzz our dbus interfaces with dfuzzer (#2087652)
- test: skip TEST-21-DFUZZER without ASan (#2087652)
- core: annotate Reexecute() as NoReply (#2087652)
- test: always force a new image for dfuzzer (#2087652)
- test: make dfuzzer less verbose (#2087652)
- test: drop the at_exit() coredump check (#2087652)
- test: make the shutdown routine a bit more "robust" (#2087652)
- tree-wide: drop manually-crafted message for missing variables (#2087652)
- test: allow overriding $QEMU_MEM when running w/ ASan (#2087652)
- test: don't test buses we don't ship (#2087652)
- shutdown: get only active md arrays. (#2047682)
- bus: Use OrderedSet for introspection (#2068131)
- logind-session-dbus: allow to set display name via dbus (#2100340)
- ci: limit which env variables we pass through `sudo` (#2087652)
- ci(Mergify): Add `ci-waived` logic (#2087652)
- json: use unsigned for refernce counter (#2087652)
- macro: check over flow in reference counter (#2087652)
- sd-bus: fix reference counter to be incremented (#2087652)
- sd-bus: introduce ref/unref function for track_item (#2087652)
- sd-bus: do not read unused value (#2087652)
- sd-bus: do not return negative errno when unknown name is specified (#2087652)
- sd-bus: use hashmap_contains() and drop unnecessary cast (#2087652)
- test: shorten code a bit (#2087652)
- test: add several tests for track item (#2087652)
- core/slice: make slice_freezer_action() return 0 if freezing state is unchanged (#2087652)
- core/unit: fix use-after-free (#2087652)
- core/timer: fix potential use-after-free (#2087652)
- core: command argument can be longer than PATH_MAX (#2073994)
- shared/install: consistently use 'lp' as the name for the LookupPaths instance (#2082131)
- shared/specifier: treat NULL the same as "" (#2082131)
- shared/install: do not print aliases longer than UNIT_NAME_MAX (#2082131)
- shared/install-printf: drop now-unused install_path_printf() (#2082131)
- strv: declare iterator of FOREACH_STRING() in the loop (#2082131)
- basic/unit-file: split out the subroutine for symlink verification (#2082131)
- basic/stat-util: add null_or_empty_path_with_root() (#2082131)
- shared/install: reuse the standard symlink verification subroutine (#2082131)
- shared/install: add a bit more quoting (#2082131)
- test: add test for systemctl link & enable (#2082131)
- tests: add helper for creating tempfiles with content (#2082131)
- man: clarify the descriptions of aliases and linked unit files (#2082131)
- basic: add new variable $SYSTEMD_OS_RELEASE to override location of os-release (#2082131)
- test-os-util: add basic tests for os-release parsing (#2082131)
- basic/env-file: make load-env-file deduplicate entries with the same key (#2082131)
- man/os-release: add a note about repeating entries (#2082131)
- shared/specifier: clarify and add test for missing data (#2082131)
- shared/specifier: provide proper error messages when specifiers fail to read files (#2082131)
- shared/install: provide proper error messages when invalid specifiers are used (#2082131)
- shared/install: move scope into InstallContext (#2082131)
- shared/specifier: fix %u/%U/%g/%G when called as unprivileged user (#2082131)
- shared/install: simplify unit_file_dump_changes() (#2082131)
- shared/install: propagate errors about invalid aliases and such too (#2082131)
- shared/install: return failure when enablement fails, but process as much as possible (#2082131)
- systemctl: fix silent failure when --root is not found (#2082131)
- shared/install: also check for self-aliases during installation and ignore them (#2082131)
- docs: Correct WantedBy= regarding template units (#2082131)
- man: fix invalid description of template handling in WantedBy= (#2082131)
- shared/install: drop unnecessary casts (#2082131)
- strv: make iterator in STRV_FOREACH() declaread in the loop (#2082131)
- core: ExecContext::restrict_filesystems is set of string (#2082131)
- install: when linking a file, create the link first or abort (#2082131)
- shared/install: split unit_file_{disable,enable}() so _reenable doesn't do setup twice (#2082131)
- shared/install: fix reenable on linked unit files (#2082131)
- test-systemctl-enable: extend the test for repeated WantedBy/RequiredBy (#2082131)
- shared/install: when we fail to chase a symlink, show some logs (#2082131)
- shared/install: do not try to resolve symlinks outside of root directory (#2082131)
- test-systemctl-enable: enhance the test for unit file linking (#2082131)
- shared/install: skip unnecessary chasing of symlinks in disable (#2082131)
- shared/install: also remove symlinks like .wants/foo@one.service → ../foo@one.service (#2082131)
- shared/install: create relative symlinks for enablement and aliasing (#2082131)
- shared/install: when looking for symlinks in .wants/.requires, ignore symlink target (#2082131)
- shared/install: stop passing duplicate root argument to install_name_printf() (#2082131)
- basic/unit-file: reverse negative conditional (#2082131)
- shared/install: split UNIT_FILE_SYMLINK into two states (#2082131)
- shared/install: fix handling of a linked unit file (#2082131)
- test-systemctl-enable: make shellcheck happy (#2082131)
- shared/install: when creating symlinks, accept different but equivalent symlinks (#2082131)
- test-systemctl-enable: use magic syntax to allow inverted tests (#2082131)
- test-systemctl-enable: also use freshly-built systemd-id128 (#2082131)
- test-systemctl-enable: disable the test for %a for now (#2082131)
- Rename UnitFileScope to LookupScope (#2082131)
- core: handle lookup paths being symlinks (#2082131)
- shared/install: use correct cleanup function (#2082131)
- udev/net_id: avoid slot based names only for single function devices (#2073003)
- test: import logind test from debian/ubuntu test suite (#2087652)
- test: drop redundant IMAGE_NAME= (#2087652)
- test: import timedated test from debian/ubuntu test suite (#2087652)
- test: introduce assert_not_in() helper function (#2087652)
- test: drop unnecessary --no-pager option (#2087652)
- test: support debian/ubuntu specific timezone config file (#2087652)
- test: import hostnamed tests from debian/ubuntu test suite (#2087652)
- locale-util: fix memleak on failure (#2087652)
- locale-util: check if enumerated locales are valid (#2087652)
- locale-util: align locale entries (#2087652)
- core: inline an iterator variable (#2087652)
- locale-setup: merge locale handling in PID1 and localed (#2087652)
- locale: rename keymap-util.[ch] -> localed-util.[ch] (#2087652)
- test: add one more path to search keymaps (#2087652)
- test: introduce inst_recursive() helper function (#2087652)
- hmac/sha256: move size define to sha256.h (#2087652)
- tpm2: support policies with PIN (#2087652)
- cryptenroll: add support for TPM2 pin (#2087652)
- cryptsetup: add support for TPM2 pin (#2087652)
- cryptsetup: add libcryptsetup TPM2 PIN support (#2087652)
- cryptenroll: add TPM2 PIN documentation (#2087652)
- cryptsetup: add manual TPM2 PIN configuration (#2087652)
- cryptenroll: add tests for TPM2 unlocking (#2087652)
- env-util: replace unsetenv_erase() by new getenv_steal_erase() helper (#2087652)
- test: install libxkbcommon and x11 keymaps (#2087652)
- test: install C.UTF-8 and English locales (#2087652)
- test: import localed tests from debian/ubuntu test suite (#2087652)
- unit: check for mount rate limiting before checking active state (#2087652)
- tests: make sure we delay running mount start jobs when /p/s/mountinfo is rate limited (#2087652)
- test: insert space in for loop (#2087652)
- test: move "do" at the end of line (#2087652)
- test: use trap RETURN (#2087652)
- test: ignore the error about our own libraries missing during image creation (#2087652)
- test: wrap binaries using systemd DSOs when running w/ ASan (#2087652)
- test: set $ASAN_RT_PATH along with $LD_PRELOAD to the ASan runtime DSO (#2087652)
- test: drop all LD_PRELOAD-related ASan workarounds (#2087652)
- test: don't wrap binaries built with ASan (#2087652)
- test: send stdout/stderr of testsuite units to journal & console (#2087652)
- test: make the busy loop in TEST-02 less verbose (#2087652)
- test: always wrap useradd/userdel when running w/ ASan (#2087652)
- test: don't flush debug logs to the console (#2087652)
- test: fix a couple of issues found by shellcheck (#2087652)
- test: pass the initdir to check_result_{qemu,nspawn} hooks (#2087652)
- test: run the custom check hooks before common checks (#2087652)
- test: check journal directly instead of capturing console output (#2087652)
- test: use saved process PID instead of %% (#2087652)
- test: account for ADDR_NO_RANDOMIZE if it's set (#2087652)
- fuzz-bcd: silence warning about always-true comparison (#2087652)
- test: disable test_ntp on RHEL (#2087652)
- core: do not filter out systemd.unit= and run-level specifier from kernel command line (#2087652)
- test: add a simple test for daemon-reexec (#2087652)
- test: install /usr/libexec/vi as well (#2087652)
- test: resize the terminal automagically with INTERACTIVE_DEBUG=yes (#2087652)
- test: create an ASan wrapper for `getent` and `su` (#2087652)
- test: mark partition bootable (#2087652)
- test: bump the data partition size if we don't strip binaries (#2087652)
- test: use PBKDF2 with capped iterations instead of Argon2 (#2087652)
- locale: drop unnecessary allocation (#2087652)

* Wed Apr 20 2022 systemd maintenance team <systemd-maint@redhat.com> - 250-7
- test: check systemd RPM macros (#2017035)
- test: do not assume x86-64 arch in TEST-58-REPART (#2017035)
- tests: add repart tests for block devices with 1024, 2048, 4096 byte sector sizes (#2017035)
- test: accept both unpadded and padded partition sizes (#2017035)
- test: lvm 2.03.15 dropped the static autoactivation (#2017035)
- test: accept GC'ed units in newer LVM (#2017035)
- shared: Add more dlopen() tests (#2017035)
- systemctl: Show how long a service ran for after it exited in status output (#2017035)
- time-util: introduce TIMESTAMP_UNIX (#2017035)
- systemctl,man: update docs for `--timestamp=` (#2017035)
- systemctl: make `--timestamp=` affect the `show` verb as well (#2017035)
- tests: allow running all the services with SYSTEMD_LOG_LEVEL (#2017035)
- coredump: raise the coredump save size on 64bit systems to 32G (and lower it to 1G on 32bit systems) (#2017035)
- repart: fix sector size handling (#2017035)
- mkdir: allow to create directory whose path contains symlink (#2017035)
- mkdir: CHASE_NONEXISTENT cannot used in chase_symlinks_and_stat() (#2017035)
- meson: move efi file lists closer to where they are used (#2017035)
- meson: move efi summary() section to src/boot/efi (#2017035)
- meson: report SBAT settings (#2017035)
- boot: Build BCD parser only on arches supported by Windows (#2017035)
- meson: Remove efi-cc option (#2017035)
- meson: Get objcopy location from compiler (#2017035)
- meson: Use files() for source lists for boot and fundamental (#2017035)
- meson: Use files() for tests (#2017035)
- tests: add fuzz-bcd (#2017035)
- meson: Use files() for fuzzers (#2017035)
- meson: Add check argument to remaining run_command() calls (#2017035)
- meson: Use echo to list files (#2017035)
- test: add a test for mkdir_p() (#2017035)
- util: another set of CVE-2021-4034 assert()s (#2017035)
- basic: update CIFS magic (#2017035)
- shared: be extra paranoid and check if argc > 0 (#2017035)
- core: check if argc > 0 and argv[0] is set (#2017035)
- core: check argc/argv uncoditionally (#2017035)
- test: temporary workaround for #21819 (#2017035)
- test: don't leak local variable to outer scopes (#2017035)
- tree-wide: don't use strjoina() on getenv() values (#2017035)
- man: clarify Environmentfile format (#2017035)
- test-load-fragment: add a basic test for config_parse_unit_env_file() (#2017035)
- core/execute: use _cleanup_ in exec_context_load_environment() (#2017035)
- test-env-file: add tests for quoting in env files (#2017035)

* Wed Feb 23 2022 systemd maintenance team <systemd-maint@redhat.com> - 250-4
- udev/net-setup-link: change the default MACAddressPolicy to "none" (#2009237)
- man: mention System Administrator's Guide in systemctl manpage (#1982596)
- Net naming scheme for RHEL-9.0 (#2052106)
- core: decrease log level of messages about use of KillMode=none (#2013213)
- ci: replace apt-key with signed-by (#2013213)
- ci: fix clang-13 installation (#2013213)

* Tue Feb 08 2022 systemd maintenance team <systemd-maint@redhat.com> - 250-3
- Treat EPERM as "not available" too (#2017035)
- test: copy portable profiles into the image if they don't exist there (#2017035)
- test: introduce `get_cgroup_hierarchy() helper (#2047768)
- test: require unified cgroup hierarchy for TEST-56 (#2047768)
- tests: rework test macros to not take code as parameters (#2017035)
- test: allow to set NULL to intro or outro (#2017035)

* Tue Feb 01 2022 Michal Sekletar <msekleta@redhat.com> - 250-2
- spec: make sure version string starts with version number (#2049054)

* Mon Jan 31 2022 Jan Macku <jamacku@redhat.com> - 250-1
- Rebase to v250 (#2047768)

* Thu Nov 18 2021 systemd maintenance team <systemd-maint@redhat.com> - 249-9
- test: don't install test-network-generator-conversion.sh w/o networkd (#2017035)
- meson.build: change operator combining bools from + to and (#2017035)
- openssl-util: use EVP API to get RSA bits (#2016042)
- procfs-util: fix confusion wrt. quantity limit and maximum value (#2017035)
- test-process-util: also add EROFS to the list of "good" errors (#2017035)
- ci: use C9S chroots in Packit (#2017035)
- test-mountpointutil-util: do not assert in test_mnt_id() (#2017035)
- core/mount: add implicit unit dependencies even if when mount unit is generated from /proc/self/mountinfo (#2019468)
- Drop Patch9001 - https://github.com/systemd/systemd/pull/17050 - Replaced by Patch0046

* Tue Oct 12 2021 systemd maintenance team <systemd-maint@redhat.com> - 249-8
- Really don't enable systemd-journald-audit.socket (#1973856)
- rules: add elevator= kernel command line parameter (#2003002)
- boot: don't build bootctl when -Dgnu-efi=false is set (#2003130)
- unit: install the systemd-bless-boot.service only if we have gnu-efi (#2003130)
- units: don't enable tmp.mount statically in local-fs.target (#2000927)
- pid1: bump DefaultTasksMax to 80% of the kernel pid.max value (#2003031)
- sd-device: introduce device_has_devlink() (#2005024)
- udev-node: split out permission handling from udev_node_add() (#2005024)
- udev-node: stack directory must exist when adding device node symlink (#2005024)
- udev-node: save information about device node and priority in symlink (#2005024)
- udev-node: always update timestamp of stack directory (#2005024)
- udev-node: assume no new claim to a symlink if /run/udev/links is not updated (#2005024)
- udev-node: always atomically create symlink to device node (#2005024)
- udev-node: check stack directory change even if devlink is removed (#2005024)
- udev-node: shorten code a bit and update log message (#2005024)
- udev-node: add random delay on conflict in updating device node symlink (#2005024)
- udev-node: drop redundant trial of devlink creation (#2005024)
- udev-node: simplify the example of race (#2005024)
- udev-node: do not ignore unexpected errors on removing symlink in stack directory (#2005024)
- basic/time-util: introduce FORMAT_TIMESPAN (#2005024)
- udev/net-setup-link: change the default MACAddressPolicy to "none" (#2009237)
- set core ulimit to 0 like on RHEL-7 (#1998509)

* Fri Aug 20 2021 systemd maintenance team <systemd-maint@redhat.com> - 249-4
- Revert "udev: remove WAIT_FOR key" (#1982666)

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com>
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Fri Aug 06 2021 systemd maintenance team <systemd-maint@redhat.com> - 249-2
- basic/unit-name: do not use strdupa() on a path (#1984299)
- basic/unit-name: adjust comments (#1984299)
- tmpfiles: don't create resolv.conf -> stub-resolv.conf symlink (#1989472)
- Copy 40-redhat.rules from RHEL-8 (#1978639)
- Avoid /tmp being mounted as tmpfs without the user's will (#1959826)
- unit: don't add Requires for tmp.mount (#1619292)
- units: add [Install] section to tmp.mount (#1959826)
- rc-local: order after network-online.target (#1954429)
- ci: drop CIs irrelevant for downstream (#1960703)
- ci: reconfigure Packit for RHEL 9 (#1960703)
- ci: run unit tests on z-stream branches as well (#1960703)
- Check return value of pam_get_item/pam_get_data functions (#1973210)
- random-util: increase random seed size to 1024 (#1982603)
- journal: don't enable systemd-journald-audit.socket by default (#1973856)
- journald.conf: don't touch current audit settings (#1973856)

* Mon Jul 12 2021  <msekleta@redhat.com> - 249-1
- Rebase to v249 (#1981276)

* Thu Jun 17 2021 systemd maintenance team <systemd-maint@redhat.com> - 248-7
- core: allow omitting second part of LoadCredentials= argument (#1949568)

* Tue Jun 15 2021 Mohan Boddu <mboddu@redhat.com> - 248-6
- Rebuilt for RHEL 9 BETA for openssl 3.0 (#1971065)

* Mon May 17 2021 systemd maintenance team <systemd-maint@redhat.com> - 248-5
- Revert "rfkill: fix the format string to prevent compilation error" (#1931710)
- Revert "rfkill: don't compare values of different signedness" (#1931710)
- rfkill: add some casts to silence -Werror=sign-compare (#1931710)

* Fri May 14 2021 systemd maintenance team <systemd-maint@redhat.com> - 248-4
- logind: set RemoveIPC to false by default (#1959836)

* Fri May 14 2021 systemd maintenance team <systemd-maint@redhat.com> - 248-3
- rfkill: don't compare values of different signedness (#1931710)
- rfkill: fix the format string to prevent compilation error (#1931710)

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com>
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Mar 31 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 248-1
- Latest upstream release, see
  https://github.com/systemd/systemd/blob/v248/NEWS.
- The changes since -rc4 are rather small, various fixes all over the place.
  A fix to how systemd-oomd selects a candidate to kill, and more debug logging
  to make this more transparent.

* Tue Mar 30 2021 Anita Zhang <the.anitazha@gmail.com> - 248~rc4-6
- Increase oomd user memory pressure limit to 50% (#1941170)

* Fri Mar 26 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 248~rc4-5
- Do not preset systemd-networkd.service and systemd-networkd-wait-online.service
  on upgrades from before systemd-networkd was split out (#1943263)
- In nsswitch.conf, move nss-myhostname to the front, before nss-mdns4 (#1943199)

* Wed Mar 24 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 248~rc4-4
- Revert patch that seems to cause problems with dns resolution
  (see comments on https://bodhi.fedoraproject.org/updates/FEDORA-2021-1c1a870ceb)

* Mon Mar 22 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 248~rc4-3
- Fix hang when processing timers during DST switch in Europe/Dublin timezone (#1941335)
- Fix returning combined IPv4/IPv6 responses from systemd-resolved cache (#1940715)
  (But note that the disablement of caching added previously is
  retained until we can do more testing.)
- Minor fix to interface naming by udev
- Fix for systemd-repart --size

* Fri Mar 19 2021 Adam Williamson <awilliam@redhat.com> - 248~rc4-2
- Disable resolved cache via config snippet (#1940715)

* Thu Mar 18 2021 Yu Watanabe <yuwatana@redhat.com> - 248~rc4-1
- Latest upstream prelease, see
  https://github.com/systemd/systemd/blob/v248-rc4/NEWS.
- A bunch of documentation updates, correctness fixes, and systemd-networkd
  features.
- Resolves #1933137, #1935084, #1933873, #1931181, #1933335, #1935062, #1927148.

* Tue Mar 16 2021 Adam Williamson <awilliam@redhat.com> - 248~rc2-8
- Drop the resolved cache disablement config snippet

* Tue Mar 16 2021 Adam Williamson <awilliam@redhat.com> - 248~rc2-7
- Backport PR #19009 to fix CNAME redirect resolving some more (#1933433)

* Fri Mar 12 2021 Adam Williamson <awilliam@redhat.com> - 248~rc2-6
- Disable resolved cache via config snippet (#1933433)

* Thu Mar 11 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 248~rc2-5
- Fix crash in pid1 during daemon-reexec (#1931034)

* Fri Mar 05 2021 Adam Williamson <awilliam@redhat.com> - 248~rc2-3
- Fix stub resolver CNAME chain resolving (#1933433)

* Mon Mar 01 2021 Josh Boyer <jwboyer@fedoraproject.org> - 248~rc2-2
- Don't set the fallback hostname to Fedora on non-Fedora OSes

* Tue Feb 23 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 248~rc2-1
- Latest upstream prelease, just a bunch of small fixes.
- Fixes #1931957.

* Tue Feb 23 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 248~rc1-2
- Rebuild with the newest scriptlets

* Tue Feb 23 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 248~rc1-1
- Latest upstream prerelease, see
  https://github.com/systemd/systemd/blob/v248-rc1/NEWS.
- Fixes #1614751 by only restarting services at the end of transcation.
  Various packages need to be rebuilt to have the updated macros.
- Fixes #1879028, though probably not completely.
- Fixes #1925805, #1928235.

* Wed Feb 17 2021 Michel Alexandre Salim <salimma@fedoraproject.org> - 247.3-3
- Increase oomd user memory pressure limit to 10% (#1929856)

* Fri Feb  5 2021 Anita Zhang <the.anitazha@gmail.com> - 247.3-2
- Changes for https://fedoraproject.org/wiki/Changes/EnableSystemdOomd.
- Backports consist primarily of PR #18361, #18444, and #18401 (plus some
  additional ones to handle merge conflicts).
- Create systemd-oomd-defaults subpackage to install unit drop-ins that will
  configure systemd-oomd to monitor and act.

* Tue Feb  2 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 247.3-1
- Minor stable release
- Fixes #1895937, #1813219, #1903106.

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Wed Jan 13 2021 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 247.2-2
- Fix bfq patch again (#1813219)

* Wed Dec 23 2020 Jonathan Underwood <jonathan.underwood@gmail.com> - 247.2-2
- Add patch to enable crypttab to support disabling of luks read and
  write workqueues (corresponding to
  https://github.com/systemd/systemd/pull/18062/).

* Wed Dec 16 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 247.2-1
- Minor stable release
- Fixes #1908071.

* Tue Dec  8 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 247.1-3
- Rebuild with fallback hostname change reverted.

* Fri Dec 04 2020 Bastien Nocera <bnocera@redhat.com> - 247.1-2
- Unset fallback-hostname as plenty of applications expected localhost
  to mean "default hostname" without ever standardising it (#1892235)

* Tue Dec  1 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 247.1-1
- Latest stable release
- Fixes #1902819.
- Files to configure networking with systemd-networkd in a VM or container are
  moved to systemd-networkd subpackage. (They were previously in the -container
  subpackage, which is for container/VM management.)

* Thu Nov 26 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 247-1
- Update to the latest version
- #1900878 should be fixed

* Tue Oct 20 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 247~rc2
- New upstream pre-release. See
  https://github.com/systemd/systemd/blob/v247-rc1/NEWS.
  Many smaller and bigger improvements and features are introduced.
  (#1885101, #1890632, #1879216)

  A backwards-incompatible change affects PCI network devices which
  are connected through a bridge which is itself associated with a
  slot. When more than one device was associated with the same slot,
  one of the devices would pseudo-randomly get named after the slot.
  That name is now not generated at all. This changed behaviour is
  causes the net naming scheme to be changed to "v247". To restore
  previous behaviour, specify net.naming-scheme=v245.

  systemd-oomd is built, but should not be considered "production
  ready" at this point. Testing and bug reports are welcome.

* Wed Sep 30 2020 Dusty Mabe <dusty@dustymabe.com> - 246.6-3
- Try to make files in subpackages (especially the networkd subpackage)
  more appropriate.

* Thu Sep 24 2020 Filipe Brandenburger <filbranden@gmail.com> - 246.6-2
- Build a package with standalone binaries for non-systemd systems.
  For now, only systemd-sysusers is included.

* Thu Sep 24 2020 Christian Glombek <lorbus@fedoraproject.org> - 246.6-2
- Split out networkd sub-package and add to main package as recommended dependency

* Sun Sep 20 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 246.6-1
- Update to latest stable release (various minor fixes: manager,
  networking, bootct, kernel-install, systemd-dissect, systemd-homed,
  fstab-generator, documentation) (#1876905)
- Do not fail in test because of kernel bug (#1803070)

* Sun Sep 13 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 246.5-1
- Update to latest stable release (a bunch of small network-related
  fixes in systemd-networkd and socket handling, documentation updates,
  a bunch of fixes for error handling).
- Also remove existing file when creating /etc/resolv.conf symlink
  upon installation (#1873856 again)

* Wed Sep  2 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 246.4-1
- Update to latest stable version: a rework of how the unit cache mtime works
  (hopefully #1872068, #1871327, #1867930), plus various fixes to
  systemd-resolved, systemd-dissect, systemd-analyze, systemd-ask-password-agent,
  systemd-networkd, systemd-homed, systemd-machine-id-setup, presets for
  instantiated units, documentation and shell completions.
- Create /etc/resolv.conf symlink upon installation (#1873856)
- Move nss-mdns before nss-resolve in /etc/nsswitch.conf and disable
  mdns by default in systemd-resolved (#1867830)

* Wed Aug 26 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 246.3-1
- Update to bugfix version (some networkd fixes, minor documentation
  fixes, relax handling of various error conditions, other fixlets for
  bugs without bugzilla numbers).

* Mon Aug 17 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 246.2-1
- A few minor bugfixes
- Adjust seccomp filter for kernel 5.8 and glibc 2.32 (#1869030)
- Create /etc/resolv.conf symlink on upgrade (#1867865)

* Fri Aug  7 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 246.1-1
- A few minor bugfixes
- Remove /etc/resolv.conf on upgrades (if managed by NetworkManager), so
  that systemd-resolved can take over the management of the symlink.

* Thu Jul 30 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 246-1
- Update to released version. Only some minor bugfixes since the pre-release.

* Sun Jul 26 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 246~rc2-2
- Make /tmp be 50% of RAM again (#1856514)
- Re-run 'systemctl preset systemd-resolved' on upgrades.
  /etc/resolv.conf is not modified, by a hint is emitted if it is
  managed by NetworkManager.

* Fri Jul 24 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 246~rc2-1
- New pre-release with incremental fixes
  (#1856037, #1858845, #1856122, #1857783)
- Enable systemd-resolved (with DNSSEC disabled by default, and LLMNR
  and mDNS support in resolve-only mode by default).
  See https://fedoraproject.org/wiki/Changes/systemd-resolved.

* Thu Jul  9 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 246~rc1-1
- New upstream release, see
  https://raw.githubusercontent.com/systemd/systemd/v246-rc1/NEWS.

  This release includes many new unit settings, related inter alia to
  cgroupsv2 freezer support and cpu affinity, encryption and verification.
  systemd-networkd has a ton of new functionality and many other tools gained
  smaller enhancements. systemd-homed gained FIDO2 support.

  Documentation has been significantly improved: sd-bus and sd-hwdb
  libraries are now fully documented; man pages have been added for
  the D-BUS APIs of systemd daemons and various new interfaces.

  Closes #1392925, #1790972, #1197886, #1525593.

* Wed Jun 24 2020 Bastien Nocera <bnocera@redhat.com> - 245.6-3
- Set fallback-hostname to fedora so that unset hostnames are still
  recognisable (#1392925)

* Tue Jun  2 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 245.6-2
- Add self-obsoletes to fix upgrades from F31

* Sun May 31 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 245.6-1
- Update to latest stable version (some documentation updates, minor
  memory correctness issues) (#1815605, #1827467, #1842067)

* Tue Apr 21 2020 Björn Esser <besser82@fedoraproject.org> - 245.5-2
- Add explicit BuildRequires: acl
- Bootstrapping for json-c SONAME bump

* Fri Apr 17 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 245.5-1
- Update to latest stable version (#1819313, #1815412, #1800875)

* Thu Apr 16 2020 Björn Esser <besser82@fedoraproject.org> - 245.4-2
- Add bootstrap option to break circular deps on cryptsetup

* Wed Apr  1 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 245.4-1
- Update to latest stable version (#1814454)

* Thu Mar 26 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 245.3-1
- Update to latest stable version (no issue that got reported in bugzilla)

* Wed Mar 18 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 245.2-1
- Update to latest stable version (a few bug fixes for random things) (#1798776)

* Fri Mar  6 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 245-1
- Update to latest version (#1807485)

* Wed Feb 26 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 245~rc2-1
- Modify the downstream udev rule to use bfq to only apply to disks (#1803500)
- "Upgrade" dependency on kbd package from Recommends to Requires (#1408878)
- Move systemd-bless-boot.service and systemd-boot-system-token.service to
  systemd-udev subpackage (#1807462)
- Move a bunch of other services to systemd-udev:
  systemd-pstore.service, all fsck-related functionality,
  systemd-volatile-root.service, systemd-verity-setup.service, and a few
  other related files.
- Fix daemon-reload rule to not kill non-systemd pid1 (#1803240)
- Fix namespace-related failure when starting systemd-homed (#1807465) and
  group lookup failure in nss_systemd (#1809147)
- Drop autogenerated BOOT_IMAGE= parameter from stored kernel command lines
  (#1716164)
- Don't require /proc to be mounted for systemd-sysusers to work (#1807768)

* Fri Feb 21 2020 Filipe Brandenburger <filbranden@gmail.com> - 245~rc1-4
- Update daemon-reexec fallback to check whether the system is booted with
  systemd as PID 1 and check whether we're upgrading before using kill -TERM
  on PID 1 (#1803240)

* Tue Feb 18 2020 Adam Williamson <awilliam@redhat.com> - 245~rc1-3
- Revert 097537f0 to fix plymouth etc. running when they shouldn't (#1803293)

* Fri Feb  7 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 245~rc1-2
- Add default 'disable *' preset for user units (#1792474, #1468501),
  see https://fedoraproject.org/wiki/Changes/Systemd_presets_for_user_units.
- Add macro to generate "compat" scriptlets based off sysusers.d format
  and autogenerate user() and group() virtual provides (#1792462),
  see https://fedoraproject.org/wiki/Changes/Adopting_sysusers.d_format.
- Revert patch to udev rules causing regression with usb hubs (#1800820).

* Wed Feb  5 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 245~rc1-1
- New upstream release, see
  https://raw.githubusercontent.com/systemd/systemd/v245-rc1/NEWS.

  This release includes completely new functionality: systemd-repart,
  systemd-homed, user reconds in json, and multi-instantiable
  journald, and a partial rework of internal communcation to use
  varlink, and bunch of more incremental changes.

  The "predictable" interface name naming scheme is changed,
  net.naming-scheme= can be used to undo the change. The change applies
  to container interface names on the host.

- Fixes #1774242, #1787089, #1798414/CVE-2020-1712.

* Fri Jan 31 2020 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sat Dec 21 2019  <zbyszek@nano-f31> - 244.1-2
- Disable service watchdogs (for systemd units)

* Sun Dec 15 2019  <zbyszek@nano-f31> - 244.1-1
- Update to latest stable batch (systemd-networkd fixups, better
  support for seccomp on s390x, minor cleanups to documentation).
- Drop patch to revert addition of NoNewPrivileges to systemd units

* Fri Nov 29 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 244-1
- Update to latest version. Just minor bugs fixed since the pre-release.

* Fri Nov 22 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 244~rc1-1
- Update to latest pre-release version,
  see https://github.com/systemd/systemd/blob/master/NEWS#L3.
  Biggest items: cgroups v2 cpuset controller, fido_id builtin in udev,
  systemd-networkd does not create a default route for link local addressing,
  systemd-networkd supports dynamic reconfiguration and a bunch of new settings.
  Network files support matching on WLAN SSID and BSSID.
- Better error messages when preset/enable/disable are used with a glob (#1763488)
- u2f-hidraw-policy package is obsoleted (#1753381)

* Tue Nov 19 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 243.4
- Latest bugfix release. Systemd-stable snapshots will now be numbered.
- Fix broken PrivateDevices filter on big-endian, s390x in particular (#1769148)
- systemd-modules-load.service should only warn, not fail, on error (#1254340)
- Fix incorrect certificate validation with DNS over TLS (#1771725, #1771726,
  CVE-2018-21029)
- Fix regression with crypttab keys with colons
- Various memleaks and minor memory access issues, warning adjustments

* Fri Oct 18 2019 Adam Williamson <awilliam@redhat.com> - 243-4.gitef67743
- Backport PR #13792 to fix nomodeset+BIOS CanGraphical bug (#1728240)

* Thu Oct 10 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 243-3.gitef67743
- Various minor documentation and error message cleanups
- Do not use cgroup v1 hierarchy in nspawn on groups v2 (#1756143)

* Sat Sep 21 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 243-2.gitfab6f01
- Backport a bunch of patches (memory access issues, improvements to error
  reporting and handling in networkd, some misleading man page contents #1751363)
- Fix permissions on static nodes (#1740664)
- Make systemd-networks follow the RFC for DHPCv6 and radv timeouts
- Fix one crash in systemd-resolved (#1703598)
- Make journal catalog creation reproducible (avoid unordered hashmap use)
- Mark the accelerometer in HP laptops as part of the laptop base
- Fix relabeling of directories with relabel-extra.d/
- Fix potential stuck noop jobs in pid1
- Obsolete timedatex package (#1735584)

* Tue Sep  3 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 243-1
- Update to latest release
- Emission of Session property-changed notifications from logind is fixed
  (this was breaking the switching of sessions to and from gnome).
- Security issue: unprivileged users were allowed to change DNS
  servers configured in systemd-resolved. Now proper polkit authorization
  is required.

* Mon Aug 26 2019 Adam Williamson <awilliam@redhat.com> - 243~rc2-2
- Backport PR #13406 to solve PATH ordering issue (#1744059)

* Thu Aug 22 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 243~rc2-1
- Update to latest pre-release. Fixes #1740113, #1717712.
- The default scheduler for disks is set to BFQ (1738828)
- The default cgroup hierarchy is set to unified (cgroups v2) (#1732114).
  Use systemd.unified-cgroup-hierarchy=0 on the kernel command line to revert.
  See https://fedoraproject.org/wiki/Changes/CGroupsV2.

* Wed Aug 07 2019 Adam Williamson <awilliam@redhat.com> - 243~rc1-2
- Backport PR #1737362 so we own /etc/systemd/system again (#1737362)

* Tue Jul 30 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 243~rc1-1
- Update to latest version (#1715699, #1696373, #1711065, #1718192)

* Sat Jul 27 2019 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sat Jul 20 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 242-6.git9d34e79
- Ignore bad rdrand output on AMD CPUs (#1729268)
- A bunch of backported patches from upstream: documentation, memory
  access fixups, command output tweaks (#1708996)

* Tue Jun 25 2019 Björn Esser <besser82@fedoraproject.org>- 242-5.git7a6d834
- Rebuilt (libqrencode.so.4)

* Tue Jun 25 2019 Miro Hrončok <mhroncok@redhat.com>- 242-4.git7a6d834
- Rebuilt for iptables update (libip4tc.so.2)

* Fri Apr 26 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 242-3.git7a6d834
- Add symbol to mark vtable format changes (anything using sd_add_object_vtable
  or sd_add_fallback_vtable needs to be rebuilt)
- Fix wireguard ListenPort handling in systemd-networkd
- Fix hang in flush_accept (#1702358)
- Fix handling of RUN keys in udevd
- Some documentation and shell completion updates and minor fixes

* Tue Apr 16 2019 Adam Williamson <awilliam@redhat.com> - 242-2
- Rebuild with Meson fix for #1699099

* Thu Apr 11 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 242-1
- Update to latest release
- Make scriptlet failure non-fatal

* Tue Apr  9 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 242~rc4-1
- Update to latest prerelease

* Thu Apr  4 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 242~rc3-1
- Update to latest prerelease

* Wed Apr  3 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 242~rc2-1
- Update to the latest prerelease.
- The bug reported on latest update that systemd-resolved and systemd-networkd are
  re-enabled after upgrade is fixed.

* Fri Mar 29 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 241-4.gitcbf14c9
- Backport various patches from the v241..v242 range:
  kernel-install will not create the boot loader entry automatically (#1648907),
  various bash completion improvements (#1183769),
  memory leaks and such (#1685286).

* Thu Mar 14 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 241-3.gitc1f8ff8
- Declare hyperv and framebuffer devices master-of-seat again (#1683197)

* Wed Feb 20 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 241-2.gita09c170
- Prevent buffer overread in systemd-udevd
- Properly validate dbus paths received over dbus (#1678394, CVE-2019-6454)

* Sat Feb  9 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 241~rc2-2
- Turn LTO back on

* Tue Feb  5 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 241~rc2-1
- Update to latest release -rc2

* Sun Feb 03 2019 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sun Jan 27 2019 Yu Watanabe <watanabe.yu@gmail.com> - 241~rc1-2
- Backport a patch for kernel-install

* Sat Jan 26 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 241~rc1-1
- Update to latest release -rc1

* Tue Jan 15 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 240-6.gitf02b547
- Add a work-around for #1663040

* Mon Jan 14 2019 Björn Esser <besser82@fedoraproject.org>
- Rebuilt for libcrypt.so.2 (#1666033)

* Fri Jan 11 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 240-4.gitf02b547
- Add a work-around for selinux issue on live images (#1663040)

* Fri Jan 11 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 240-3.gitf02b547
- systemd-journald and systemd-journal-remote reject entries which
  contain too many fields (CVE-2018-16865, #1664973) and set limits on the
  process' command line length (CVE-2018-16864, #1664972)
- $DBUS_SESSION_BUS_ADDRESS is again exported by pam_systemd (#1662857)
- A fix for systemd-udevd crash (#1662303)

* Sat Dec 22 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 240-2
- Add two more patches that revert recent udev changes

* Fri Dec 21 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 240-1
- Update to latest release
  See https://github.com/systemd/systemd/blob/master/NEWS for the list of changes.

* Mon Dec 17 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 239-10.git9f3aed1
- Hibernation checks for resume= are rescinded (#1645870)
- Various patches:
  - memory issues in logind, networkd, journald (#1653068), sd-device, etc.
  - Adaptations for newer meson, lz4, kernel
  - Fixes for misleading bugs in documentation
- net.ipv4.conf.all.rp_filter is changed from 1 to 2

* Thu Nov 29 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl>
- Adjust scriptlets to modify /etc/authselect/user-nsswitch.conf
  (see https://github.com/pbrezina/authselect/issues/77)
- Drop old scriptlets for nsswitch.conf modifications for nss-mymachines and nss-resolve

* Sun Nov 18 2018 Alejandro Domínguez Muñoz <adomu@net-c.com>
- Remove link creation for rsyslog.service

* Thu Nov  8 2018 Adam Williamson <awilliam@redhat.com> - 239-9.git9f3aed1
- Go back to using systemctl preset-all in %%post (#1647172, #1118740)

* Mon Nov  5 2018 Adam Williamson <awilliam@redhat.com> - 239-8.git9f3aed1
- Requires(post) openssl-libs to fix live image build machine-id issue
  See: https://pagure.io/dusty/failed-composes/issue/960

* Mon Nov  5 2018 Yu Watanabe <watanabe.yu@gmail.com>
- Set proper attributes to private directories

* Fri Nov  2 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 239-7.git9f3aed1
- Split out the rpm macros into systemd-rpm-macros subpackage (#1645298)

* Sun Oct 28 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 239-6.git9f3aed1
- Fix a local vulnerability from a race condition in chown-recursive (CVE-2018-15687, #1639076)
- Fix a local vulnerability from invalid handling of long lines in state deserialization (CVE-2018-15686, #1639071)
- Fix a remote vulnerability in DHCPv6 in systemd-networkd (CVE-2018-15688, #1639067)
- The DHCP server is started only when link is UP
- DHCPv6 prefix delegation is improved
- Downgrade logging of various messages and add loging in other places
- Many many fixes in error handling and minor memory leaks and such
- Fix typos and omissions in documentation
- Typo in %%_environmnentdir rpm macro is fixed (with backwards compatiblity preserved)
- Matching by MACAddress= in systemd-networkd is fixed
- Creation of user runtime directories is improved, and the user
  manager is only stopped after 10 s after the user logs out (#1642460 and other bugs)
- systemd units systemd-timesyncd, systemd-resolved, systemd-networkd are switched back to use DynamicUser=0
- Aliases are now resolved when loading modules from pid1. This is a (redundant) fix for a brief kernel regression.
- "systemctl --wait start" exits immediately if no valid units are named
- zram devices are not considered as candidates for hibernation
- ECN is not requested for both in- and out-going connections (the sysctl overide for net.ipv4.tcp_ecn is removed)
- Various smaller improvements to unit ordering and dependencies
- generators are now called with the manager's environment
- Handling of invalid (intentionally corrupt) dbus messages is improved, fixing potential local DOS avenues
- The target of symlinks links in .wants/ and .requires/ is now ignored. This fixes an issue where
  the unit file would sometimes be loaded from such a symlink, leading to non-deterministic unit contents.
- Filtering of kernel threads is improved. This fixes an issues with newer kernels where hybrid kernel/user
  threads are used by bpfilter.
- "noresume" can be used on the kernel command line to force normal boot even if a hibernation images is present
- Hibernation is not advertised if resume= is not present on the kernenl command line
- Hibernation/Suspend/... modes can be disabled using AllowSuspend=,
  AllowHibernation=, AllowSuspendThenHibernate=, AllowHybridSleep=
- LOGO= and DOCUMENTATION_URL= are documented for the os-release file
- The hashmap mempool is now only used internally in systemd, and is disabled for external users of the systemd libraries
- Additional state is serialized/deserialized when logind is restarted, fixing the handling of user objects
- Catalog entries for the journal are improved (#1639482)
- If suspend fails, the post-suspend hooks are still called.
- Various build issues on less-common architectures are fixed

* Wed Oct  3 2018 Jan Synáček <jsynacek@redhat.com> - 239-5
- Fix meson using -Ddebug, which results in FTBFS
- Fix line_begins() to accept word matching full string (#1631840)

* Mon Sep 10 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 239-4
- Move /etc/yum/protected.d/systemd.conf to /etc/dnf/ (#1626969)

* Wed Jul 18 2018 Terje Rosten <terje.rosten@ntnu.no> - 239-3
- Ignore return value from systemd-binfmt in scriptlet (#1565425)

* Sun Jul 15 2018 Filipe Brandenburger <filbranden@gmail.com>
- Override systemd-user PAM config in install and not prep

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jun 25 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl>
- Rebuild for Python 3.7 again

* Fri Jun 22 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 239-1
- Update to latest version, mostly bug fixes and new functionality,
  very little breaking changes. See
  https://github.com/systemd/systemd/blob/v239/NEWS for details.

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com>
- Rebuilt for Python 3.7

* Fri May 11 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 238-8.git0e0aa59
- Backport a number of patches (documentation, hwdb updates)
- Fixes for tmpfiles 'e' entries
- systemd-networkd crashes
- XEN virtualization detection on hyper-v
- Avoid relabelling /sys/fs/cgroup if not needed (#1576240)

* Wed Apr 18 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 238-7.fc28.1
- Allow fake Delegate= setting on slices (#1568594)

* Wed Mar 28 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 238-7
- Move udev transfiletriggers to the right package, fix quoting

* Tue Mar 27 2018 Colin Walters <walters@verbum.org> - 238-6
- Use shell for triggers; see https://github.com/systemd/systemd/pull/8550
  This fixes compatibility with rpm-ostree.

* Tue Mar 20 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 238-5
- Backport patch to revert inadvertent change of "predictable" interface name (#1558027)

* Fri Mar 16 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 238-4
- Do not close dbus connection during dbus reload call (#1554578)

* Wed Mar  7 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 238-3
- Revert the patches for GRUB BootLoaderSpec support
- Add patch for /etc/machine-id creation (#1552843)

* Tue Mar  6 2018 Yu Watanabe <watanabe.yu@gmail.com> - 238-2
- Fix transfiletrigger script (#1551793)

* Mon Mar  5 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 238-1
- Update to latest version
- This fixes a hard-to-trigger potential vulnerability (CVE-2018-6954)
- New transfiletriggers are installed for udev hwdb and rules, the journal
  catalog, sysctl.d, binfmt.d, sysusers.d, tmpfiles.d.

* Tue Feb 27 2018 Javier Martinez Canillas <javierm@redhat.com> - 237-7.git84c8da5
- Add patch to install kernel images for GRUB BootLoaderSpec support

* Sat Feb 24 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 237-6.git84c8da5
- Create /etc/systemd in %%post libs if necessary (#1548607)

* Fri Feb 23 2018 Adam Williamson <awilliam@redhat.com> - 237-5.git84c8da5
- Use : not touch to create file in -libs %%post

* Thu Feb 22 2018 Patrick Uiterwijk <patrick@puiterwijk.org> - 237-4.git84c8da5
- Add coreutils dep for systemd-libs %%post
- Add patch to typecast USB IDs to avoid compile failure

* Wed Feb 21 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 237-3.git84c8da5
- Update some patches for test skipping that were updated upstream
  before merging
- Add /usr/lib/systemd/purge-nobody-user — a script to check if nobody is defined
  correctly and possibly replace existing mappings

* Tue Feb 20 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 237-2.gitdff4849
- Backport a bunch of patches, most notably for the journal and various
  memory issues. Some minor build fixes.
- Switch to new ldconfig macros that do nothing in F28+
- /etc/systemd/dont-synthesize-nobody is created in %%post if nfsnobody
  or nobody users are defined (#1537262)

* Fri Feb  9 2018 Zbigniew Jędrzejeweski-Szmek <zbyszek@in.waw.pl> - 237-1.git78bd769
- Update to first stable snapshot (various minor memory leaks and misaccesses,
  some documentation bugs, build fixes).

* Sun Jan 28 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 237-1
- Update to latest version

* Sun Jan 21 2018 Björn Esser <besser82@fedoraproject.org> - 236-4.git3e14c4c
- Add patch to include <crypt.h> if needed

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 236-3.git3e14c4c
- Rebuilt for switch to libxcrypt

* Thu Jan 11 2018 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 236-2.git23e14c4
- Backport a bunch of bugfixes from upstream (#1531502, #1531381, #1526621
  various memory corruptions in systemd-networkd)
- /dev/kvm is marked as a static node which fixes permissions on s390x
  and ppc64 (#1532382)

* Fri Dec 15 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 236-1
- Update to latest version

* Mon Dec 11 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 235-5.git4a0e928
- Update to latest git snapshot, do not build for realz
- Switch to libidn2 again (#1449145)

* Tue Nov 07 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 235-4
- Rebuild for cryptsetup-2.0.0-0.2.fc28

* Wed Oct 25 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 235-3
- Backport a bunch of patches, including LP#172535

* Wed Oct 18 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 235-2
- Patches for cryptsetup _netdev

* Fri Oct  6 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 235-1
- Update to latest version

* Tue Sep 26 2017 Nathaniel McCallum <npmccallum@redhat.com> - 234-8
- Backport /etc/crypttab _netdev feature from upstream

* Thu Sep 21 2017 Michal Sekletar <msekleta@redhat.com> - 234-7
- Make sure to remove all device units sharing the same sysfs path (#1475570)

* Mon Sep 18 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 234-6
- Bump xslt recursion limit for libxslt-1.30

* Mon Jul 31 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 234-5
- Backport more patches (#1476005, hopefully #1462378)

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org>
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 17 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 234-3
- Fix x-systemd.timeout=0 in /etc/fstab (#1462378)
- Minor patches (memleaks, --help fixes, seccomp on arm64)

* Thu Jul 13 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 234-2
- Create kvm group (#1431876)

* Thu Jul 13 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 234-1
- Latest release

* Sat Jul  1 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 233-7.git74d8f1c
- Update to snapshot
- Build with meson again

* Tue Jun 27 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 233-6
- Fix an out-of-bounds write in systemd-resolved (CVE-2017-9445)

* Fri Jun 16 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 233-5.gitec36d05
- Update to snapshot version, build with meson

* Thu Jun 15 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 233-4
- Backport a bunch of small fixes (memleaks, wrong format strings,
  man page clarifications, shell completion)
- Fix systemd-resolved crash on crafted DNS packet (CVE-2017-9217, #1455493)
- Fix systemd-vconsole-setup.service error on systems with no VGA console (#1272686)
- Drop soft-static uid for systemd-journal-gateway
- Use ID from /etc/os-release as ntpvendor

* Thu Mar 16 2017 Michal Sekletar <msekleta@redhat.com> - 233-3
- Backport bugfixes from upstream
- Don't return error when machinectl couldn't figure out container IP addresses (#1419501)

* Thu Mar  2 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 233-2
- Fix installation conflict with polkit

* Thu Mar  2 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 233-1
- New upstream release (#1416201, #1405439, #1420753, many others)
- New systemd-tests subpackage with "installed tests"

* Thu Feb 16 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 232-15
- Add %%ghost %%dir entries for .wants dirs of our targets (#1422894)

* Tue Feb 14 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 232-14
- Ignore the hwdb parser test

* Tue Feb 14 2017 Jan Synáček <jsynacek@redhat.com> - 232-14
- machinectl fails when virtual machine is running (#1419501)

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 232-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 31 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 232-12
- Backport patch for initrd-switch-root.service getting killed (#1414904)
- Fix sd-journal-gatewayd -D, --trust, and COREDUMP_CONTAINER_CMDLINE
  extraction by sd-coredump.

* Sun Jan 29 2017 zbyszek <zbyszek@in.waw.pl> - 232-11
- Backport a number of patches (#1411299, #1413075, #1415745,
                                ##1415358, #1416588, #1408884)
- Fix various memleaks and unitialized variable access
- Shell completion enhancements
- Enable TPM logging by default (#1411156)
- Update hwdb (#1270124)

* Thu Jan 19 2017 Adam Williamson <awilliam@redhat.com> - 232-10
- Backport fix for boot failure in initrd-switch-root (#1414904)

* Wed Jan 18 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 232-9
- Add fake dependency on systemd-pam to systemd-devel to ensure systemd-pam
  is available as multilib (#1414153)

* Tue Jan 17 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 232-8
- Fix buildsystem to check for lz4 correctly (#1404406)

* Wed Jan 11 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 232-7
- Various small tweaks to scriplets

* Sat Jan 07 2017 Kevin Fenzi <kevin@scrye.com> - 232-6
- Fix scriptlets to never fail in libs post

* Fri Jan 06 2017 Kevin Fenzi <kevin@scrye.com> - 232-5
- Add patch from Michal Schmidt to avoid process substitution (#1392236)

* Sun Nov  6 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 232-4
- Rebuild (#1392236)

* Fri Nov  4 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 232-3
- Make /etc/dbus-1/system.d directory non-%%ghost

* Fri Nov  4 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 232-2
- Fix kernel-install (#1391829)
- Restore previous systemd-user PAM config (#1391836)
- Move journal-upload.conf.5 from systemd main to journal-remote subpackage (#1391833)
- Fix permissions on /var/lib/systemd/journal-upload (#1262665)

* Thu Nov  3 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 232-1
- Update to latest version (#998615, #1181922, #1374371, #1390704, #1384150, #1287161)
- Add %%{_isa} to Provides on arch-full packages (#1387912)
- Create systemd-coredump user in %%pre (#1309574)
- Replace grubby patch with a short-circuiting install.d "plugin"
- Enable nss-systemd in the passwd, group lines in nsswith.conf
- Add [!UNAVAIL=return] fallback after nss-resolve in hosts line in nsswith.conf
- Move systemd-nspawn man pages to the right subpackage (#1391703)

* Tue Oct 18 2016 Jan Synáček <jsynacek@redhat.com> - 231-11
- SPC - Cannot restart host operating from container (#1384523)

* Sun Oct  9 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 231-10
- Do not recreate /var/log/journal on upgrades (#1383066)
- Move nss-myhostname provides to systemd-libs (#1383271)

* Fri Oct  7 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 231-9
- Fix systemctl set-default (#1374371)
- Prevent systemd-udev-trigger.service from restarting (follow-up for #1378974)

* Tue Oct  4 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 231-8
- Apply fix for #1378974

* Mon Oct  3 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 231-7
- Apply patches properly

* Thu Sep 29 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 231-6
- Better fix for (#1380286)

* Thu Sep 29 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 231-5
- Denial-of-service bug against pid1 (#1380286)

* Thu Aug 25 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 231-4
- Fix preset-all (#1363858)
- Fix issue with daemon-reload messing up graphics (#1367766)
- A few other bugfixes

* Wed Aug 03 2016 Adam Williamson <awilliam@redhat.com> - 231-3
- Revert preset-all change, it broke stuff (#1363858)

* Wed Jul 27 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@bupkis> - 231-2
- Call preset-all on initial installation (#1118740)
- Fix botched Recommends for libxkbcommon

* Tue Jul 26 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@bupkis> - 231-1
- Update to latest version

* Wed Jun  8 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 230-3
- Update to latest git snapshot (fixes for systemctl set-default,
  polkit lingering policy, reversal of the framebuffer rules,
  unaligned access fixes, fix for StartupBlockIOWeight-over-dbus).
  Those changes are interspersed with other changes and new features
  (mostly in lldp, networkd, and nspawn). Some of those new features
  might not work, but I think that existing functionality should not
  be broken, so it seems worthwile to update to the snapshot.

* Sat May 21 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@bupkis> - 230-2
- Remove systemd-compat-libs on upgrade

* Sat May 21 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@bupkis> - 230-1
- New version
- Drop compat-libs
- Require libxkbcommon explictly, since the automatic dependency will
  not be generated anymore

* Tue Apr 26 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@bupkis> - 229-15
- Remove duplicated entries in -container %%files (#1330395)

* Fri Apr 22 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 229-14
- Move installation of udev services to udev subpackage (#1329023)

* Mon Apr 18 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 229-13
- Split out systemd-pam subpackage (#1327402)

* Mon Apr 18 2016 Harald Hoyer <harald@redhat.com> - 229-12
- move more binaries and services from the main package to subpackages

* Mon Apr 18 2016 Harald Hoyer <harald@redhat.com> - 229-11
- move more binaries and services from the main package to subpackages

* Mon Apr 18 2016 Harald Hoyer <harald@redhat.com> - 229-10
- move device dependant stuff to the udev subpackage

* Tue Mar 22 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 229-9
- Add myhostname to /etc/nsswitch.conf (#1318303)

* Mon Mar 21 2016 Harald Hoyer <harald@redhat.com> - 229-8
- fixed kernel-install for copying files for grubby
Resolves: rhbz#1299019

* Thu Mar 17 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 229-7
- Moar patches (#1316964, #1317928)
- Move vconsole-setup and tmpfiles-setup-dev bits to systemd-udev
- Protect systemd-udev from deinstallation

* Fri Mar 11 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 229-6
- Create /etc/resolv.conf symlink from systemd-resolved (#1313085)

* Fri Mar  4 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 229-5
- Split out systemd-container subpackage (#1163412)
- Split out system-udev subpackage
- Add various bugfix patches, incl. a tentative fix for #1308771

* Tue Mar  1 2016 Peter Robinson <pbrobinson@fedoraproject.org> 229-4
- Power64 and s390(x) now have libseccomp support
- aarch64 has gnu-efi

* Tue Feb 23 2016 Jan Synáček <jsynacek@redhat.com> - 229-3
- Fix build failures on ppc64 (#1310800)

* Tue Feb 16 2016 Dennis Gilmore <dennis@ausil.us> - 229-2
- revert: fixed kernel-install for copying files for grubby
Resolves: rhbz#1299019
- this causes the dtb files to not get installed at all and the fdtdir
- line in extlinux.conf to not get updated correctly

* Thu Feb 11 2016 Michal Sekletar <msekleta@redhat.com> - 229-1
- New upstream release

* Thu Feb 11 2016 Harald Hoyer <harald@redhat.com> - 228-10.gite35a787
- fixed kernel-install for copying files for grubby
Resolves: rhbz#1299019

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 228-9.gite35a787
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 27 2016 Peter Robinson <pbrobinson@fedoraproject.org> 228-8.gite35a787
- Rebuild for binutils on aarch64 fix

* Fri Jan 08 2016 Dan Horák <dan[at]danny.cz> - 228-7.gite35a787
- apply the conflict with fedora-release only in Fedora

* Thu Dec 10 2015 Jan Synáček <jsynacek@redhat.com> - 228-6.gite35a787
- Fix rawhide build failures on ppc64 (#1286249)

* Sun Nov 29 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 228-6.gite35a787
- Create /etc/systemd/network (#1286397)

* Thu Nov 26 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 228-5.gite35a787
- Do not install nss modules by default

* Tue Nov 24 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 228-4.gite35a787
- Update to latest upstream git: there is a bunch of fixes
  (nss-mymachines overflow bug, networkd fixes, more completions are
  properly installed), mixed with some new resolved features.
- Rework file triggers so that they always run before daemons are restarted

* Thu Nov 19 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 228-3
- Enable rpm file triggers for daemon-reload

* Thu Nov 19 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 228-2
- Fix version number in obsoleted package name (#1283452)

* Wed Nov 18 2015 Kay Sievers <kay@redhat.com> - 228-1
- New upstream release

* Thu Nov 12 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 227-7
- Rename journal-gateway subpackage to journal-remote
- Ignore the access mode on /var/log/journal (#1048424)
- Do not assume fstab is present (#1281606)

* Wed Nov 11 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 227-6
- Rebuilt for https://fedoraproject.org/wiki/Changes/python3.5

* Tue Nov 10 2015 Lukáš Nykrýn <lnykryn@redhat.com> - 227-5
- Rebuild for libmicrohttpd soname bump

* Fri Nov 06 2015 Robert Kuska <rkuska@redhat.com> - 227-4
- Rebuilt for Python3.5 rebuild

* Wed Nov  4 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 227-3
- Fix syntax in kernel-install (#1277264)

* Tue Nov 03 2015 Michal Schmidt <mschmidt@redhat.com> - 227-2
- Rebuild for libmicrohttpd soname bump.

* Wed Oct  7 2015 Kay Sievers <kay@redhat.com> - 227-1
- New upstream release

* Fri Sep 18 2015 Jan Synáček <jsynacek@redhat.com> - 226-3
- user systemd-journal-upload should be in systemd-journal group (#1262743)

* Fri Sep 18 2015 Kay Sievers <kay@redhat.com> - 226-2
- Add selinux to  system-user PAM config

* Tue Sep  8 2015 Kay Sievers <kay@redhat.com> - 226-1
- New upstream release

* Thu Aug 27 2015 Kay Sievers <kay@redhat.com> - 225-1
- New upstream release

* Fri Jul 31 2015 Kay Sievers <kay@redhat.com> - 224-1
- New upstream release

* Wed Jul 29 2015 Kay Sievers <kay@redhat.com> - 223-2
- update to git snapshot

* Wed Jul 29 2015 Kay Sievers <kay@redhat.com> - 223-1
- New upstream release

* Thu Jul  9 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 222-2
- Remove python subpackages (python-systemd in now standalone)

* Tue Jul  7 2015 Kay Sievers <kay@redhat.com> - 222-1
- New upstream release

* Mon Jul  6 2015 Kay Sievers <kay@redhat.com> - 221-5.git619b80a
- update to git snapshot

* Mon Jul  6 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@laptop> - 221-4.git604f02a
- Add example file with yama config (#1234951)

* Sun Jul 5 2015 Kay Sievers <kay@redhat.com> - 221-3.git604f02a
- update to git snapshot

* Mon Jun 22 2015 Kay Sievers <kay@redhat.com> - 221-2
- build systemd-boot EFI tools

* Fri Jun 19 2015 Lennart Poettering <lpoetter@redhat.com> - 221-1
- New upstream release
- Undoes botched translation check, should be reinstated later?

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 220-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 11 2015 Peter Robinson <pbrobinson@fedoraproject.org> 220-9
- The gold linker is now fixed on aarch64

* Tue Jun  9 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 220-8
- Remove gudev which is now provided as separate package (libgudev)
- Fix for spurious selinux denials (#1224211)
- Udev change events (#1225905)
- Patches for some potential crashes
- ProtectSystem=yes does not touch /home
- Man page fixes, hwdb updates, shell completion updates
- Restored persistent device symlinks for bcache, xen block devices
- Tag all DRM cards as master-of-seat

* Tue Jun 09 2015 Harald Hoyer <harald@redhat.com> 220-7
- fix udev block device watch

* Tue Jun 09 2015 Harald Hoyer <harald@redhat.com> 220-6
- add support for network disk encryption

* Sun Jun  7 2015 Peter Robinson <pbrobinson@fedoraproject.org> 220-5
- Disable gold on aarch64 until it's fixed (tracked in rhbz #1225156)

* Sat May 30 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 220-4
- systemd-devel should require systemd-libs, not the main package (#1226301)
- Check for botched translations (#1226566)
- Make /etc/udev/hwdb.d part of the rpm (#1226379)

* Thu May 28 2015 Richard W.M. Jones <rjones@redhat.com> - 220-3
- Add patch to fix udev --daemon not cleaning child processes
  (upstream commit 86c3bece38bcf5).

* Wed May 27 2015 Richard W.M. Jones <rjones@redhat.com> - 220-2
- Add patch to fix udev --daemon crash (upstream commit 040e689654ef08).

* Thu May 21 2015 Lennart Poettering <lpoetter@redhat.com> - 220-1
- New upstream release
- Drop /etc/mtab hack, as that's apparently fixed in mock now (#1116158)
- Remove ghosting for /etc/systemd/system/runlevel*.target, these
  targets are not configurable anymore in systemd upstream
- Drop work-around for #1002806, since this is solved upstream now

* Wed May 20 2015 Dennis Gilmore <dennis@ausil.us> - 219-15
- fix up the conflicts version for fedora-release

* Wed May 20 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 219-14
- Remove presets (#1221340)
- Fix (potential) crash and memory leak in timedated, locking failure
  in systemd-nspawn, crash in resolved.
- journalctl --list-boots should be faster
- zsh completions are improved
- various ommissions in docs are corrected (#1147651)
- VARIANT and VARIANT_ID fields in os-release are documented
- systemd-fsck-root.service is generated in the initramfs (#1201979, #1107818)
- systemd-tmpfiles should behave better on read-only file systems (#1207083)

* Wed Apr 29 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 219-13
- Patches for some outstanding annoyances
- Small keyboard hwdb updates

* Wed Apr  8 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 219-12
- Tighten requirements between subpackages (#1207381).

* Sun Mar 22 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 219-11
- Move all parts systemd-journal-{remote,upload} to
  systemd-journal-gatewayd subpackage (#1193143).
- Create /var/lib/systemd/journal-upload directory (#1193145).
- Cut out lots of stupid messages at debug level which were obscuring more
  important stuff.
- Apply "tentative" state for devices only when they are added, not removed.
- Ignore invalid swap pri= settings (#1204336)
- Fix SELinux check for timedated operations to enable/disable ntp (#1014315)
- Fix comparing of filesystem paths (#1184016)

* Sat Mar 14 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 219-10
- Fixes for bugs 1186018, 1195294, 1185604, 1196452.
- Hardware database update.
- Documentation fixes.
- A fix for journalctl performance regression.
- Fix detection of inability to open files in journalctl.
- Detect SuperH architecture properly.
- The first of duplicate lines in tmpfiles wins again.
- Do vconsole setup after loading vconsole driver, not fbcon.
- Fix problem where some units were restarted during systemd reexec.
- Fix race in udevadm settle tripping up NetworkManager.
- Downgrade various log messages.
- Fix issue where journal-remote would process some messages with a delay.
- GPT /srv partition autodiscovery is fixed.
- Reconfigure old Finnish keymaps in post (#1151958)

* Tue Mar 10 2015 Jan Synáček <jsynacek@redhat.com> - 219-9
- Buttons on Lenovo X6* tablets broken (#1198939)

* Tue Mar  3 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 219-8
- Reworked device handling (#1195761)
- ACL handling fixes (with a script in %%post)
- Various log messages downgraded (#1184712)
- Allow PIE on s390 again (#1197721)

* Wed Feb 25 2015 Michal Schmidt <mschmidt@redhat.com> - 219-7
- arm: reenable lto. gcc-5.0.0-0.16 fixed the crash (#1193212)

* Tue Feb 24 2015 Colin Walters <walters@redhat.com> - 219-6
- Revert patch that breaks Atomic/OSTree (#1195761)

* Fri Feb 20 2015 Michal Schmidt <mschmidt@redhat.com> - 219-5
- Undo the resolv.conf workaround, Aim for a proper fix in Rawhide.

* Fri Feb 20 2015 Michal Schmidt <mschmidt@redhat.com> - 219-4
- Revive fedora-disable-resolv.conf-symlink.patch to unbreak composes.

* Wed Feb 18 2015 Michal Schmidt <mschmidt@redhat.com> - 219-3
- arm: disabling gold did not help; disable lto instead (#1193212)

* Tue Feb 17 2015 Peter Jones <pjones@redhat.com> - 219-2
- Update 90-default.present for dbxtool.

* Mon Feb 16 2015 Lennart Poettering <lpoetter@redhat.com> - 219-1
- New upstream release
- This removes the sysctl/bridge hack, a different solution needs to be found for this (see #634736)
- This removes the /etc/resolv.conf hack, anaconda needs to fix their handling of /etc/resolv.conf as symlink
- This enables "%%check"
- disable gold on arm, as that is broken (see #1193212)

* Mon Feb 16 2015 Peter Robinson <pbrobinson@fedoraproject.org> 218-6
- aarch64 now has seccomp support

* Thu Feb 05 2015 Michal Schmidt <mschmidt@redhat.com> - 218-5
- Don't overwrite systemd.macros with unrelated Source file.

* Thu Feb  5 2015 Jan Synáček <jsynacek@redhat.com> - 218-4
- Add a touchpad hwdb (#1189319)

* Thu Jan 15 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 218-4
- Enable xkbcommon dependency to allow checking of keymaps
- Fix permissions of /var/log/journal (#1048424)
- Enable timedatex in presets (#1187072)
- Disable rpcbind in presets (#1099595)

* Wed Jan  7 2015 Jan Synáček <jsynacek@redhat.com> - 218-3
- RFE: journal: automatically rotate the file if it is unlinked (#1171719)

* Mon Jan 05 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 218-3
- Add firewall description files (#1176626)

* Thu Dec 18 2014 Jan Synáček <jsynacek@redhat.com> - 218-2
- systemd-nspawn doesn't work on s390/s390x (#1175394)

* Wed Dec 10 2014 Lennart Poettering <lpoetter@redhat.com> - 218-1
- New upstream release
- Enable "nss-mymachines" in /etc/nsswitch.conf

* Thu Nov 06 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 217-4
- Change libgudev1 to only require systemd-libs (#727499), there's
  no need to require full systemd stack.
- Fixes for bugs #1159448, #1152220, #1158035.
- Bash completions updates to allow propose more units for start/restart,
  and completions for set-default,get-default.
- Again allow systemctl enable of instances.
- Hardware database update and fixes.
- Udev crash on invalid options and kernel commandline timeout parsing are fixed.
- Add "embedded" chassis type.
- Sync before 'reboot -f'.
- Fix restarting of timer units.

* Wed Nov 05 2014 Michal Schmidt <mschmidt@redhat.com> - 217-3
- Fix hanging journal flush (#1159641)

* Fri Oct 31 2014 Michal Schmidt <mschmidt@redhat.com> - 217-2
- Fix ordering cycles involving systemd-journal-flush.service and
  remote-fs.target (#1159117)

* Tue Oct 28 2014 Lennart Poettering <lpoetter@redhat.com> - 217-1
- New upstream release

* Fri Oct 17 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 216-12
- Drop PackageKit.service from presets (#1154126)

* Mon Oct 13 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 216-11
- Conflict with old versions of initscripts (#1152183)
- Remove obsolete Finnish keymap (#1151958)

* Fri Oct 10 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 216-10
- Fix a problem with voluntary daemon exits and some other bugs
  (#1150477, #1095962, #1150289)

* Fri Oct 03 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 216-9
- Update to latest git, but without the readahead removal patch
  (#1114786, #634736)

* Wed Oct 01 2014 Kay Sievers <kay@redhat.com> - 216-8
- revert "don't reset selinux context during CHANGE events"

* Wed Oct 01 2014 Lukáš Nykrýn <lnykryn@redhat.com> - 216-7
- add temporary workaround for #1147910
- don't reset selinux context during CHANGE events

* Wed Sep 10 2014 Michal Schmidt <mschmidt@redhat.com> - 216-6
- Update timesyncd with patches to avoid hitting NTP pool too often.

* Tue Sep 09 2014 Michal Schmidt <mschmidt@redhat.com> - 216-5
- Use common CONFIGURE_OPTS for build2 and build3.
- Configure timesyncd with NTP servers from Fedora/RHEL vendor zone.

* Wed Sep 03 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 216-4
- Move config files for sd-j-remote/upload to sd-journal-gateway subpackage (#1136580)

* Thu Aug 28 2014 Peter Robinson <pbrobinson@fedoraproject.org> 216-3
- Drop no LTO build option for aarch64/s390 now it's fixed in binutils (RHBZ 1091611)

* Thu Aug 21 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 216-2
- Re-add patch to disable resolve.conf symlink (#1043119)

* Wed Aug 20 2014 Lennart Poettering <lpoetter@redhat.com> - 216-1
- New upstream release

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 215-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug 13 2014 Dan Horák <dan[at]danny.cz> 215-11
- disable LTO also on s390(x)

* Sat Aug 09 2014 Harald Hoyer <harald@redhat.com> 215-10
- fixed PPC64LE

* Wed Aug  6 2014 Tom Callaway <spot@fedoraproject.org> - 215-9
- fix license handling

* Wed Jul 30 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 215-8
- Create systemd-journal-remote and systemd-journal-upload users (#1118907)

* Thu Jul 24 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 215-7
- Split out systemd-compat-libs subpackage

* Tue Jul 22 2014 Kalev Lember <kalevlember@gmail.com> - 215-6
- Rebuilt for gobject-introspection 1.41.4

* Mon Jul 21 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 215-5
- Fix SELinux context of /etc/passwd-, /etc/group-, /etc/.updated (#1121806)
- Add missing BR so gnutls and elfutils are used

* Sat Jul 19 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 215-4
- Various man page updates
- Static device node logic is conditionalized on CAP_SYS_MODULES instead of CAP_MKNOD
  for better behaviour in containers
- Some small networkd link handling fixes
- vconsole-setup runs setfont before loadkeys (https://bugs.freedesktop.org/show_bug.cgi?id=80685)
- New systemd-escape tool
- XZ compression settings are tweaked to greatly improve journald performance
- "watch" is accepted as chassis type
- Various sysusers fixes, most importantly correct selinux labels
- systemd-timesyncd bug fix (https://bugs.freedesktop.org/show_bug.cgi?id=80932)
- Shell completion improvements
- New udev tag ID_SOFTWARE_RADIO can be used to instruct logind to allow user access
- XEN and s390 virtualization is properly detected

* Mon Jul 07 2014 Colin Walters <walters@redhat.com> - 215-3
- Add patch to disable resolve.conf symlink (#1043119)

* Sun Jul 06 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 215-2
- Move systemd-journal-remote to systemd-journal-gateway package (#1114688)
- Disable /etc/mtab handling temporarily (#1116158)

* Thu Jul 03 2014 Lennart Poettering <lpoetter@redhat.com> - 215-1
- New upstream release
- Enable coredump logic (which abrt would normally override)

* Sun Jun 29 2014 Peter Robinson <pbrobinson@fedoraproject.org> 214-5
- On aarch64 disable LTO as it still has issues on that arch

* Thu Jun 26 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 214-4
- Bugfixes (#996133, #1112908)

* Mon Jun 23 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 214-3
- Actually create input group (#1054549)

* Sun Jun 22 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 214-2
- Do not restart systemd-logind on upgrades (#1110697)
- Add some patches (#1081429, #1054549, #1108568, #928962)

* Wed Jun 11 2014 Lennart Poettering <lpoetter@redhat.com> - 214-1
- New upstream release
- Get rid of "floppy" group, since udev uses "disk" now
- Reenable LTO

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 213-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 28 2014 Kay Sievers <kay@redhat.com> - 213-3
- fix systemd-timesync user creation

* Wed May 28 2014 Michal Sekletar <msekleta@redhat.com> - 213-2
- Create temporary files after installation (#1101983)
- Add sysstat-collect.timer, sysstat-summary.timer to preset policy (#1101621)

* Wed May 28 2014 Kay Sievers <kay@redhat.com> - 213-1
- New upstream release

* Tue May 27 2014 Kalev Lember <kalevlember@gmail.com> - 212-6
- Rebuilt for https://fedoraproject.org/wiki/Changes/Python_3.4

* Fri May 23 2014 Adam Williamson <awilliam@redhat.com> - 212-5
- revert change from 212-4, causes boot fail on single CPU boxes (RHBZ 1095891)

* Wed May 07 2014 Kay Sievers <kay@redhat.com> - 212-4
- add netns udev workaround

* Wed May 07 2014 Michal Sekletar <msekleta@redhat.com> - 212-3
- enable uuidd.socket by default (#1095353)

* Sat Apr 26 2014 Peter Robinson <pbrobinson@fedoraproject.org> 212-2
- Disable building with -flto for the moment due to gcc 4.9 issues (RHBZ 1091611)

* Tue Mar 25 2014 Lennart Poettering <lpoetter@redhat.com> - 212-1
- New upstream release

* Mon Mar 17 2014 Peter Robinson <pbrobinson@fedoraproject.org> 211-2
- Explicitly define which upstream platforms support libseccomp

* Tue Mar 11 2014 Lennart Poettering <lpoetter@redhat.com> - 211-1
- New upstream release

* Mon Mar 10 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 210-8
- Fix logind unpriviledged reboot issue and a few other minor fixes
- Limit generator execution time
- Recognize buttonless joystick types

* Fri Mar 07 2014 Karsten Hopp <karsten@redhat.com> 210-7
- ppc64le needs link warnings disabled, too

* Fri Mar 07 2014 Karsten Hopp <karsten@redhat.com> 210-6
- move ifarch ppc64le to correct place (libseccomp req)

* Fri Mar 07 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 210-5
- Bugfixes: #1047568, #1047039, #1071128, #1073402
- Bash completions for more systemd tools
- Bluetooth database update
- Manpage fixes

* Thu Mar 06 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 210-4
- Apply work-around for ppc64le too (#1073647).

* Sat Mar 01 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 210-3
- Backport a few patches, add completion for systemd-nspawn.

* Fri Feb 28 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 210-3
- Apply work-arounds for ppc/ppc64 for bugs 1071278 and 1071284

* Mon Feb 24 2014 Lennart Poettering <lpoetter@redhat.com> - 210-2
- Check more services against preset list and enable by default

* Mon Feb 24 2014 Lennart Poettering <lpoetter@redhat.com> - 210-1
- new upstream release

* Sun Feb 23 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 209-2.gitf01de96
- Enable dnssec-triggerd.service by default (#1060754)

* Sun Feb 23 2014 Kay Sievers <kay@redhat.com> - 209-2.gitf01de96
- git snapshot to sort out ARM build issues

* Thu Feb 20 2014 Lennart Poettering <lpoetter@redhat.com> - 209-1
- new upstream release

* Tue Feb 18 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 208-15
- Make gpsd lazily activated (#1066421)

* Mon Feb 17 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 208-14
- Back out patch which causes user manager to be destroyed when unneeded
  and spams logs (#1053315)

* Sun Feb 16 2014 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 208-13
- A different fix for #1023820 taken from Mageia
- Backported fix for #997031
- Hardward database updates, man pages improvements, a few small memory
  leaks, utf-8 correctness and completion fixes
- Support for key-slot option in crypttab

* Sat Jan 25 2014 Ville Skyttä <ville.skytta@iki.fi> - 208-12
- Own the %%{_prefix}/lib/kernel(/*) and %%{_datadir}/zsh(/*) dirs.

* Tue Dec 03 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 208-11
- Backport a few fixes, relevant documentation updates, and HWDB changes
  (#1051797, #1051768, #1047335, #1047304, #1047186, #1045849, #1043304,
   #1043212, #1039351, #1031325, #1023820, #1017509, #953077)
- Flip journalctl to --full by default (#984758)

* Tue Dec 03 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 208-9
- Apply two patches for #1026860

* Tue Dec 03 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 208-8
- Bump release to stay ahead of f20

* Tue Dec 03 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 208-7
- Backport patches (#1023041, #1036845, #1006386?)
- HWDB update
- Some small new features: nspawn --drop-capability=, running PID 1 under
  valgrind, "yearly" and "annually" in calendar specifications
- Some small documentation and logging updates

* Tue Nov 19 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 208-6
- Bump release to stay ahead of f20

* Tue Nov 19 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 208-5
- Use unit name in PrivateTmp= directories (#957439)
- Update manual pages, completion scripts, and hardware database
- Configurable Timeouts/Restarts default values
- Support printing of timestamps on the console
- Fix some corner cases in detecting when writing to the console is safe
- Python API: convert keyword values to string, fix sd_is_booted() wrapper
- Do not tread missing /sbin/fsck.btrfs as an error (#1015467)
- Allow masking of fsck units
- Advertise hibernation to swap files
- Fix SO_REUSEPORT settings
- Prefer converted xkb keymaps to legacy keymaps (#981805, #1026872)
- Make use of newer kmod
- Assorted bugfixes: #1017161, #967521, #988883, #1027478, #821723, #1014303

* Tue Oct 22 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 208-4
- Add temporary fix for #1002806

* Mon Oct 21 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 208-3
- Backport a bunch of fixes and hwdb updates

* Wed Oct 2 2013 Lennart Poettering <lpoetter@redhat.com> - 208-2
- Move old random seed and backlight files into the right place

* Wed Oct 2 2013 Lennart Poettering <lpoetter@redhat.com> - 208-1
- New upstream release

* Thu Sep 26 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> 207-5
- Do not create /var/var/... dirs

* Wed Sep 18 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> 207-4
- Fix policykit authentication
- Resolves: rhbz#1006680

* Tue Sep 17 2013 Harald Hoyer <harald@redhat.com> 207-3
- fixed login
- Resolves: rhbz#1005233

* Mon Sep 16 2013 Harald Hoyer <harald@redhat.com> 207-2
- add some upstream fixes for 207
- fixed swap activation
- Resolves: rhbz#1008604

* Fri Sep 13 2013 Lennart Poettering <lpoetter@redhat.com> - 207-1
- New upstream release

* Fri Sep 06 2013 Harald Hoyer <harald@redhat.com> 206-11
- support "debug" kernel command line parameter
- journald: fix fd leak in journal_file_empty
- journald: fix vacuuming of archived journals
- libudev: enumerate - do not try to match against an empty subsystem
- cgtop: fixup the online help
- libudev: fix memleak when enumerating childs

* Wed Sep 04 2013 Harald Hoyer <harald@redhat.com> 206-10
- Do not require grubby, lorax now takes care of grubby
- cherry-picked a lot of patches from upstream

* Tue Aug 27 2013 Dennis Gilmore <dennis@ausil.us> - 206-9
- Require grubby, Fedora installs require grubby,
- kernel-install took over from new-kernel-pkg
- without the Requires we are unable to compose Fedora
- everyone else says that since kernel-install took over
- it is responsible for ensuring that grubby is in place
- this is really what we want for Fedora

* Tue Aug 27 2013 Kay Sievers <kay@redhat.com> - 206-8
- Revert "Require grubby its needed by kernel-install"

* Mon Aug 26 2013 Dennis Gilmore <dennis@ausil.us> 206-7
- Require grubby its needed by kernel-install

* Thu Aug 22 2013 Harald Hoyer <harald@redhat.com> 206-6
- kernel-install now understands kernel flavors like PAE

* Tue Aug 20 2013 Rex Dieter <rdieter@fedoraproject.org> - 206-5
- add sddm.service to preset file (#998978)

* Fri Aug 16 2013 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 206-4
- Filter out provides for private python modules.
- Add requires on kmod >= 14 (#990994).

* Sun Aug 11 2013 Zbigniew Jedrzejewski-Szmek <zbyszek@in.waw.pl> - 206-3
- New systemd-python3 package (#976427).
- Add ownership of a few directories that we create (#894202).

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 206-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Jul 23 2013 Kay Sievers <kay@redhat.com> - 206-1
- New upstream release
  Resolves (#984152)

* Wed Jul  3 2013 Lennart Poettering <lpoetter@redhat.com> - 205-1
- New upstream release

* Wed Jun 26 2013 Michal Schmidt <mschmidt@redhat.com> 204-10
- Split systemd-journal-gateway subpackage (#908081).

* Mon Jun 24 2013 Michal Schmidt <mschmidt@redhat.com> 204-9
- Rename nm_dispatcher to NetworkManager-dispatcher in default preset (#977433)

* Fri Jun 14 2013 Harald Hoyer <harald@redhat.com> 204-8
- fix, which helps to sucessfully browse journals with
  duplicated seqnums

* Fri Jun 14 2013 Harald Hoyer <harald@redhat.com> 204-7
- fix duplicate message ID bug
Resolves: rhbz#974132

* Thu Jun 06 2013 Harald Hoyer <harald@redhat.com> 204-6
- introduce 99-default-disable.preset

* Thu Jun  6 2013 Lennart Poettering <lpoetter@redhat.com> - 204-5
- Rename 90-display-manager.preset to 85-display-manager.preset so that it actually takes precedence over 90-default.preset's "disable *" line (#903690)

* Tue May 28 2013 Harald Hoyer <harald@redhat.com> 204-4
- Fix kernel-install (#965897)

* Wed May 22 2013 Kay Sievers <kay@redhat.com> - 204-3
- Fix kernel-install (#965897)

* Thu May  9 2013 Lennart Poettering <lpoetter@redhat.com> - 204-2
- New upstream release
- disable isdn by default (#959793)

* Tue May 07 2013 Harald Hoyer <harald@redhat.com> 203-2
- forward port kernel-install-grubby.patch

* Tue May  7 2013 Lennart Poettering <lpoetter@redhat.com> - 203-1
- New upstream release

* Wed Apr 24 2013 Harald Hoyer <harald@redhat.com> 202-3
- fix ENOENT for getaddrinfo
- Resolves: rhbz#954012 rhbz#956035
- crypt-setup-generator: correctly check return of strdup
- logind-dbus: initialize result variable
- prevent library underlinking

* Fri Apr 19 2013 Harald Hoyer <harald@redhat.com> 202-2
- nspawn create empty /etc/resolv.conf if necessary
- python wrapper: add sd_journal_add_conjunction()
- fix s390 booting
- Resolves: rhbz#953217

* Thu Apr 18 2013 Lennart Poettering <lpoetter@redhat.com> - 202-1
- New upstream release

* Tue Apr 09 2013 Michal Schmidt <mschmidt@redhat.com> - 201-2
- Automatically discover whether to run autoreconf and add autotools and git
  BuildRequires based on the presence of patches to be applied.
- Use find -delete.

* Mon Apr  8 2013 Lennart Poettering <lpoetter@redhat.com> - 201-1
- New upstream release

* Mon Apr  8 2013 Lennart Poettering <lpoetter@redhat.com> - 200-4
- Update preset file

* Fri Mar 29 2013 Lennart Poettering <lpoetter@redhat.com> - 200-3
- Remove NetworkManager-wait-online.service from presets file again, it should default to off

* Fri Mar 29 2013 Lennart Poettering <lpoetter@redhat.com> - 200-2
- New upstream release

* Tue Mar 26 2013 Lennart Poettering <lpoetter@redhat.com> - 199-2
- Add NetworkManager-wait-online.service to the presets file

* Tue Mar 26 2013 Lennart Poettering <lpoetter@redhat.com> - 199-1
- New upstream release

* Mon Mar 18 2013 Michal Schmidt <mschmidt@redhat.com> 198-7
- Drop /usr/s?bin/ prefixes.

* Fri Mar 15 2013 Harald Hoyer <harald@redhat.com> 198-6
- run autogen to pickup all changes

* Fri Mar 15 2013 Harald Hoyer <harald@redhat.com> 198-5
- do not mount anything, when not running as pid 1
- add initrd.target for systemd in the initrd

* Wed Mar 13 2013 Harald Hoyer <harald@redhat.com> 198-4
- fix switch-root and local-fs.target problem
- patch kernel-install to use grubby, if available

* Fri Mar 08 2013 Harald Hoyer <harald@redhat.com> 198-3
- add Conflict with dracut < 026 because of the new switch-root isolate

* Thu Mar  7 2013 Lennart Poettering <lpoetter@redhat.com> - 198-2
- Create required users

* Thu Mar 7 2013 Lennart Poettering <lpoetter@redhat.com> - 198-1
- New release
- Enable journal persistancy by default

* Sun Feb 10 2013 Peter Robinson <pbrobinson@fedoraproject.org> 197-3
- Bump for ARM

* Fri Jan 18 2013 Michal Schmidt <mschmidt@redhat.com> - 197-2
- Added qemu-guest-agent.service to presets (Lennart, #885406).
- Add missing pygobject3-base to systemd-analyze deps (Lennart).
- Do not require hwdata, it is all in the hwdb now (Kay).
- Drop dependency on dbus-python.

* Tue Jan  8 2013 Lennart Poettering <lpoetter@redhat.com> - 197-1
- New upstream release

* Mon Dec 10 2012 Michal Schmidt <mschmidt@redhat.com> - 196-4
- Enable rngd.service by default (#857765).

* Mon Dec 10 2012 Michal Schmidt <mschmidt@redhat.com> - 196-3
- Disable hardening on s390(x) because PIE is broken there and produces
  text relocations with __thread (#868839).

* Wed Dec 05 2012 Michal Schmidt <mschmidt@redhat.com> - 196-2
- added spice-vdagentd.service to presets (Lennart, #876237)
- BR cryptsetup-devel instead of the legacy cryptsetup-luks-devel provide name
  (requested by Milan Brož).
- verbose make to see the actual build flags

* Wed Nov 21 2012 Lennart Poettering <lpoetter@redhat.com> - 196-1
- New upstream release

* Tue Nov 20 2012 Lennart Poettering <lpoetter@redhat.com> - 195-8
- https://bugzilla.redhat.com/show_bug.cgi?id=873459
- https://bugzilla.redhat.com/show_bug.cgi?id=878093

* Thu Nov 15 2012 Michal Schmidt <mschmidt@redhat.com> - 195-7
- Revert udev killing cgroup patch for F18 Beta.
- https://bugzilla.redhat.com/show_bug.cgi?id=873576

* Fri Nov 09 2012 Michal Schmidt <mschmidt@redhat.com> - 195-6
- Fix cyclical dep between systemd and systemd-libs.
- Avoid broken build of test-journal-syslog.
- https://bugzilla.redhat.com/show_bug.cgi?id=873387
- https://bugzilla.redhat.com/show_bug.cgi?id=872638

* Thu Oct 25 2012 Kay Sievers <kay@redhat.com> - 195-5
- require 'sed', limit HOSTNAME= match

* Wed Oct 24 2012 Michal Schmidt <mschmidt@redhat.com> - 195-4
- add dmraid-activation.service to the default preset
- add yum protected.d fragment
- https://bugzilla.redhat.com/show_bug.cgi?id=869619
- https://bugzilla.redhat.com/show_bug.cgi?id=869717

* Wed Oct 24 2012 Kay Sievers <kay@redhat.com> - 195-3
- Migrate /etc/sysconfig/ i18n, keyboard, network files/variables to
  systemd native files

* Tue Oct 23 2012 Lennart Poettering <lpoetter@redhat.com> - 195-2
- Provide syslog because the journal is fine as a syslog implementation

* Tue Oct 23 2012 Lennart Poettering <lpoetter@redhat.com> - 195-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=831665
- https://bugzilla.redhat.com/show_bug.cgi?id=847720
- https://bugzilla.redhat.com/show_bug.cgi?id=858693
- https://bugzilla.redhat.com/show_bug.cgi?id=863481
- https://bugzilla.redhat.com/show_bug.cgi?id=864629
- https://bugzilla.redhat.com/show_bug.cgi?id=864672
- https://bugzilla.redhat.com/show_bug.cgi?id=864674
- https://bugzilla.redhat.com/show_bug.cgi?id=865128
- https://bugzilla.redhat.com/show_bug.cgi?id=866346
- https://bugzilla.redhat.com/show_bug.cgi?id=867407
- https://bugzilla.redhat.com/show_bug.cgi?id=868603

* Wed Oct 10 2012 Michal Schmidt <mschmidt@redhat.com> - 194-2
- Add scriptlets for migration away from systemd-timedated-ntp.target

* Wed Oct  3 2012 Lennart Poettering <lpoetter@redhat.com> - 194-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=859614
- https://bugzilla.redhat.com/show_bug.cgi?id=859655

* Fri Sep 28 2012 Lennart Poettering <lpoetter@redhat.com> - 193-1
- New upstream release

* Tue Sep 25 2012 Lennart Poettering <lpoetter@redhat.com> - 192-1
- New upstream release

* Fri Sep 21 2012 Lennart Poettering <lpoetter@redhat.com> - 191-2
- Fix journal mmap header prototype definition to fix compilation on 32bit

* Fri Sep 21 2012 Lennart Poettering <lpoetter@redhat.com> - 191-1
- New upstream release
- Enable all display managers by default, as discussed with Adam Williamson

* Thu Sep 20 2012 Lennart Poettering <lpoetter@redhat.com> - 190-1
- New upstream release
- Take possession of /etc/localtime, and remove /etc/sysconfig/clock
- https://bugzilla.redhat.com/show_bug.cgi?id=858780
- https://bugzilla.redhat.com/show_bug.cgi?id=858787
- https://bugzilla.redhat.com/show_bug.cgi?id=858771
- https://bugzilla.redhat.com/show_bug.cgi?id=858754
- https://bugzilla.redhat.com/show_bug.cgi?id=858746
- https://bugzilla.redhat.com/show_bug.cgi?id=858266
- https://bugzilla.redhat.com/show_bug.cgi?id=858224
- https://bugzilla.redhat.com/show_bug.cgi?id=857670
- https://bugzilla.redhat.com/show_bug.cgi?id=856975
- https://bugzilla.redhat.com/show_bug.cgi?id=855863
- https://bugzilla.redhat.com/show_bug.cgi?id=851970
- https://bugzilla.redhat.com/show_bug.cgi?id=851275
- https://bugzilla.redhat.com/show_bug.cgi?id=851131
- https://bugzilla.redhat.com/show_bug.cgi?id=847472
- https://bugzilla.redhat.com/show_bug.cgi?id=847207
- https://bugzilla.redhat.com/show_bug.cgi?id=846483
- https://bugzilla.redhat.com/show_bug.cgi?id=846085
- https://bugzilla.redhat.com/show_bug.cgi?id=845973
- https://bugzilla.redhat.com/show_bug.cgi?id=845194
- https://bugzilla.redhat.com/show_bug.cgi?id=845028
- https://bugzilla.redhat.com/show_bug.cgi?id=844630
- https://bugzilla.redhat.com/show_bug.cgi?id=839736
- https://bugzilla.redhat.com/show_bug.cgi?id=835848
- https://bugzilla.redhat.com/show_bug.cgi?id=831740
- https://bugzilla.redhat.com/show_bug.cgi?id=823485
- https://bugzilla.redhat.com/show_bug.cgi?id=821813
- https://bugzilla.redhat.com/show_bug.cgi?id=807886
- https://bugzilla.redhat.com/show_bug.cgi?id=802198
- https://bugzilla.redhat.com/show_bug.cgi?id=767795
- https://bugzilla.redhat.com/show_bug.cgi?id=767561
- https://bugzilla.redhat.com/show_bug.cgi?id=752774
- https://bugzilla.redhat.com/show_bug.cgi?id=732874
- https://bugzilla.redhat.com/show_bug.cgi?id=858735

* Thu Sep 13 2012 Lennart Poettering <lpoetter@redhat.com> - 189-4
- Don't pull in pkg-config as dep
- https://bugzilla.redhat.com/show_bug.cgi?id=852828

* Wed Sep 12 2012 Lennart Poettering <lpoetter@redhat.com> - 189-3
- Update preset policy
- Rename preset policy file from 99-default.preset to 90-default.preset so that people can order their own stuff after the Fedora default policy if they wish

* Thu Aug 23 2012 Lennart Poettering <lpoetter@redhat.com> - 189-2
- Update preset policy
- https://bugzilla.redhat.com/show_bug.cgi?id=850814

* Thu Aug 23 2012 Lennart Poettering <lpoetter@redhat.com> - 189-1
- New upstream release

* Thu Aug 16 2012 Ray Strode <rstrode@redhat.com> 188-4
- more scriptlet fixes
  (move dm migration logic to %%posttrans so the service
   files it's looking for are available at the time
   the logic is run)

* Sat Aug 11 2012 Lennart Poettering <lpoetter@redhat.com> - 188-3
- Remount file systems MS_PRIVATE before switching roots
- https://bugzilla.redhat.com/show_bug.cgi?id=847418

* Wed Aug 08 2012 Rex Dieter <rdieter@fedoraproject.org> - 188-2
- fix scriptlets

* Wed Aug  8 2012 Lennart Poettering <lpoetter@redhat.com> - 188-1
- New upstream release
- Enable gdm and avahi by default via the preset file
- Convert /etc/sysconfig/desktop to display-manager.service symlink
- Enable hardened build

* Mon Jul 30 2012 Kay Sievers <kay@redhat.com> - 187-3
- Obsolete: system-setup-keyboard

* Wed Jul 25 2012 Kalev Lember <kalevlember@gmail.com> - 187-2
- Run ldconfig for the new -libs subpackage

* Thu Jul 19 2012 Lennart Poettering <lpoetter@redhat.com> - 187-1
- New upstream release

* Mon Jul 09 2012 Harald Hoyer <harald@redhat.com> 186-2
- fixed dracut conflict version

* Tue Jul  3 2012 Lennart Poettering <lpoetter@redhat.com> - 186-1
- New upstream release

* Fri Jun 22 2012 Nils Philippsen <nils@redhat.com> - 185-7.gite7aee75
- add obsoletes/conflicts so multilib systemd -> systemd-libs updates work

* Thu Jun 14 2012 Michal Schmidt <mschmidt@redhat.com> - 185-6.gite7aee75
- Update to current git

* Wed Jun 06 2012 Kay Sievers - 185-5.gita2368a3
- disable plymouth in configure, to drop the .wants/ symlinks

* Wed Jun 06 2012 Michal Schmidt <mschmidt@redhat.com> - 185-4.gita2368a3
- Update to current git snapshot
  - Add systemd-readahead-analyze
  - Drop upstream patch
- Split systemd-libs
- Drop duplicate doc files
- Fixed License headers of subpackages

* Wed Jun 06 2012 Ray Strode <rstrode@redhat.com> - 185-3
- Drop plymouth files
- Conflict with old plymouth

* Tue Jun 05 2012 Kay Sievers - 185-2
- selinux udev labeling fix
- conflict with older dracut versions for new udev file names

* Mon Jun 04 2012 Kay Sievers - 185-1
- New upstream release
  - udev selinux labeling fixes
  - new man pages
  - systemctl help <unit name>

* Thu May 31 2012 Lennart Poettering <lpoetter@redhat.com> - 184-1
- New upstream release

* Thu May 24 2012 Kay Sievers <kay@redhat.com> - 183-1
- New upstream release including udev merge.

* Wed Mar 28 2012 Michal Schmidt <mschmidt@redhat.com> - 44-4
- Add triggers from Bill Nottingham to correct the damage done by
  the obsoleted systemd-units's preun scriptlet (#807457).

* Mon Mar 26 2012 Dennis Gilmore <dennis@ausil.us> - 44-3
- apply patch from upstream so we can build systemd on arm and ppc
- and likely the rest of the secondary arches

* Tue Mar 20 2012 Michal Schmidt <mschmidt@redhat.com> - 44-2
- Don't build the gtk parts anymore. They're moving into systemd-ui.
- Remove a dead patch file.

* Fri Mar 16 2012 Lennart Poettering <lpoetter@redhat.com> - 44-1
- New upstream release
- Closes #798760, #784921, #783134, #768523, #781735

* Mon Feb 27 2012 Dennis Gilmore <dennis@ausil.us> - 43-2
- don't conflict with fedora-release systemd never actually provided
- /etc/os-release so there is no actual conflict

* Wed Feb 15 2012 Lennart Poettering <lpoetter@redhat.com> - 43-1
- New upstream release
- Closes #789758, #790260, #790522

* Sat Feb 11 2012 Lennart Poettering <lpoetter@redhat.com> - 42-1
- New upstream release
- Save a bit of entropy during system installation (#789407)
- Don't own /etc/os-release anymore, leave that to fedora-release

* Thu Feb  9 2012 Adam Williamson <awilliam@redhat.com> - 41-2
- rebuild for fixed binutils

* Thu Feb  9 2012 Lennart Poettering <lpoetter@redhat.com> - 41-1
- New upstream release

* Tue Feb  7 2012 Lennart Poettering <lpoetter@redhat.com> - 40-1
- New upstream release

* Thu Jan 26 2012 Kay Sievers <kay@redhat.com> - 39-3
- provide /sbin/shutdown

* Wed Jan 25 2012 Harald Hoyer <harald@redhat.com> 39-2
- increment release

* Wed Jan 25 2012 Kay Sievers <kay@redhat.com> - 39-1.1
- install everything in /usr
  https://fedoraproject.org/wiki/Features/UsrMove

* Wed Jan 25 2012 Lennart Poettering <lpoetter@redhat.com> - 39-1
- New upstream release

* Sun Jan 22 2012 Michal Schmidt <mschmidt@redhat.com> - 38-6.git9fa2f41
- Update to a current git snapshot.
- Resolves: #781657

* Sun Jan 22 2012 Michal Schmidt <mschmidt@redhat.com> - 38-5
- Build against libgee06. Reenable gtk tools.
- Delete unused patches.
- Add easy building of git snapshots.
- Remove legacy spec file elements.
- Don't mention implicit BuildRequires.
- Configure with --disable-static.
- Merge -units into the main package.
- Move section 3 manpages to -devel.
- Fix unowned directory.
- Run ldconfig in scriptlets.
- Split systemd-analyze to a subpackage.

* Sat Jan 21 2012 Dan Horák <dan[at]danny.cz> - 38-4
- fix build on big-endians

* Wed Jan 11 2012 Lennart Poettering <lpoetter@redhat.com> - 38-3
- Disable building of gtk tools for now

* Wed Jan 11 2012 Lennart Poettering <lpoetter@redhat.com> - 38-2
- Fix a few (build) dependencies

* Wed Jan 11 2012 Lennart Poettering <lpoetter@redhat.com> - 38-1
- New upstream release

* Tue Nov 15 2011 Michal Schmidt <mschmidt@redhat.com> - 37-4
- Run authconfig if /etc/pam.d/system-auth is not a symlink.
- Resolves: #753160

* Wed Nov 02 2011 Michal Schmidt <mschmidt@redhat.com> - 37-3
- Fix remote-fs-pre.target and its ordering.
- Resolves: #749940

* Wed Oct 19 2011 Michal Schmidt <mschmidt@redhat.com> - 37-2
- A couple of fixes from upstream:
- Fix a regression in bash-completion reported in Bodhi.
- Fix a crash in isolating.
- Resolves: #717325

* Tue Oct 11 2011 Lennart Poettering <lpoetter@redhat.com> - 37-1
- New upstream release
- Resolves: #744726, #718464, #713567, #713707, #736756

* Thu Sep 29 2011 Michal Schmidt <mschmidt@redhat.com> - 36-5
- Undo the workaround. Kay says it does not belong in systemd.
- Unresolves: #741655

* Thu Sep 29 2011 Michal Schmidt <mschmidt@redhat.com> - 36-4
- Workaround for the crypto-on-lvm-on-crypto disk layout
- Resolves: #741655

* Sun Sep 25 2011 Michal Schmidt <mschmidt@redhat.com> - 36-3
- Revert an upstream patch that caused ordering cycles
- Resolves: #741078

* Fri Sep 23 2011 Lennart Poettering <lpoetter@redhat.com> - 36-2
- Add /etc/timezone to ghosted files

* Fri Sep 23 2011 Lennart Poettering <lpoetter@redhat.com> - 36-1
- New upstream release
- Resolves: #735013, #736360, #737047, #737509, #710487, #713384

* Thu Sep  1 2011 Lennart Poettering <lpoetter@redhat.com> - 35-1
- New upstream release
- Update post scripts
- Resolves: #726683, #713384, #698198, #722803, #727315, #729997, #733706, #734611

* Thu Aug 25 2011 Lennart Poettering <lpoetter@redhat.com> - 34-1
- New upstream release

* Fri Aug 19 2011 Harald Hoyer <harald@redhat.com> 33-2
- fix ABRT on service file reloading
- Resolves: rhbz#732020

* Wed Aug  3 2011 Lennart Poettering <lpoetter@redhat.com> - 33-1
- New upstream release

* Fri Jul 29 2011 Lennart Poettering <lpoetter@redhat.com> - 32-1
- New upstream release

* Wed Jul 27 2011 Lennart Poettering <lpoetter@redhat.com> - 31-2
- Fix access mode of modprobe file, restart logind after upgrade

* Wed Jul 27 2011 Lennart Poettering <lpoetter@redhat.com> - 31-1
- New upstream release

* Wed Jul 13 2011 Lennart Poettering <lpoetter@redhat.com> - 30-1
- New upstream release

* Thu Jun 16 2011 Lennart Poettering <lpoetter@redhat.com> - 29-1
- New upstream release

* Mon Jun 13 2011 Michal Schmidt <mschmidt@redhat.com> - 28-4
- Apply patches from current upstream.
- Fixes memory size detection on 32-bit with >4GB RAM (BZ712341)

* Wed Jun 08 2011 Michal Schmidt <mschmidt@redhat.com> - 28-3
- Apply patches from current upstream
- https://bugzilla.redhat.com/show_bug.cgi?id=709909
- https://bugzilla.redhat.com/show_bug.cgi?id=710839
- https://bugzilla.redhat.com/show_bug.cgi?id=711015

* Sat May 28 2011 Lennart Poettering <lpoetter@redhat.com> - 28-2
- Pull in nss-myhostname

* Thu May 26 2011 Lennart Poettering <lpoetter@redhat.com> - 28-1
- New upstream release

* Wed May 25 2011 Lennart Poettering <lpoetter@redhat.com> - 26-2
- Bugfix release
- https://bugzilla.redhat.com/show_bug.cgi?id=707507
- https://bugzilla.redhat.com/show_bug.cgi?id=707483
- https://bugzilla.redhat.com/show_bug.cgi?id=705427
- https://bugzilla.redhat.com/show_bug.cgi?id=707577

* Sat Apr 30 2011 Lennart Poettering <lpoetter@redhat.com> - 26-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=699394
- https://bugzilla.redhat.com/show_bug.cgi?id=698198
- https://bugzilla.redhat.com/show_bug.cgi?id=698674
- https://bugzilla.redhat.com/show_bug.cgi?id=699114
- https://bugzilla.redhat.com/show_bug.cgi?id=699128

* Thu Apr 21 2011 Lennart Poettering <lpoetter@redhat.com> - 25-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=694788
- https://bugzilla.redhat.com/show_bug.cgi?id=694321
- https://bugzilla.redhat.com/show_bug.cgi?id=690253
- https://bugzilla.redhat.com/show_bug.cgi?id=688661
- https://bugzilla.redhat.com/show_bug.cgi?id=682662
- https://bugzilla.redhat.com/show_bug.cgi?id=678555
- https://bugzilla.redhat.com/show_bug.cgi?id=628004

* Wed Apr  6 2011 Lennart Poettering <lpoetter@redhat.com> - 24-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=694079
- https://bugzilla.redhat.com/show_bug.cgi?id=693289
- https://bugzilla.redhat.com/show_bug.cgi?id=693274
- https://bugzilla.redhat.com/show_bug.cgi?id=693161

* Tue Apr  5 2011 Lennart Poettering <lpoetter@redhat.com> - 23-1
- New upstream release
- Include systemd-sysv-convert

* Fri Apr  1 2011 Lennart Poettering <lpoetter@redhat.com> - 22-1
- New upstream release

* Wed Mar 30 2011 Lennart Poettering <lpoetter@redhat.com> - 21-2
- The quota services are now pulled in by mount points, hence no need to enable them explicitly

* Tue Mar 29 2011 Lennart Poettering <lpoetter@redhat.com> - 21-1
- New upstream release

* Mon Mar 28 2011 Matthias Clasen <mclasen@redhat.com> - 20-2
- Apply upstream patch to not send untranslated messages to plymouth

* Tue Mar  8 2011 Lennart Poettering <lpoetter@redhat.com> - 20-1
- New upstream release

* Tue Mar  1 2011 Lennart Poettering <lpoetter@redhat.com> - 19-1
- New upstream release

* Wed Feb 16 2011 Lennart Poettering <lpoetter@redhat.com> - 18-1
- New upstream release

* Mon Feb 14 2011 Bill Nottingham <notting@redhat.com> - 17-6
- bump upstart obsoletes (#676815)

* Wed Feb  9 2011 Tom Callaway <spot@fedoraproject.org> - 17-5
- add macros.systemd file for %%{_unitdir}

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 17-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Feb  9 2011 Lennart Poettering <lpoetter@redhat.com> - 17-3
- Fix popen() of systemctl, #674916

* Mon Feb  7 2011 Bill Nottingham <notting@redhat.com> - 17-2
- add epoch to readahead obsolete

* Sat Jan 22 2011 Lennart Poettering <lpoetter@redhat.com> - 17-1
- New upstream release

* Tue Jan 18 2011 Lennart Poettering <lpoetter@redhat.com> - 16-2
- Drop console.conf again, since it is not shipped in pamtmp.conf

* Sat Jan  8 2011 Lennart Poettering <lpoetter@redhat.com> - 16-1
- New upstream release

* Thu Nov 25 2010 Lennart Poettering <lpoetter@redhat.com> - 15-1
- New upstream release

* Thu Nov 25 2010 Lennart Poettering <lpoetter@redhat.com> - 14-1
- Upstream update
- Enable hwclock-load by default
- Obsolete readahead
- Enable /var/run and /var/lock on tmpfs

* Fri Nov 19 2010 Lennart Poettering <lpoetter@redhat.com> - 13-1
- new upstream release

* Wed Nov 17 2010 Bill Nottingham <notting@redhat.com> 12-3
- Fix clash

* Wed Nov 17 2010 Lennart Poettering <lpoetter@redhat.com> - 12-2
- Don't clash with initscripts for now, so that we don't break the builders

* Wed Nov 17 2010 Lennart Poettering <lpoetter@redhat.com> - 12-1
- New upstream release

* Fri Nov 12 2010 Matthias Clasen <mclasen@redhat.com> - 11-2
- Rebuild with newer vala, libnotify

* Thu Oct  7 2010 Lennart Poettering <lpoetter@redhat.com> - 11-1
- New upstream release

* Wed Sep 29 2010 Jesse Keating <jkeating@redhat.com> - 10-6
- Rebuilt for gcc bug 634757

* Thu Sep 23 2010 Bill Nottingham <notting@redhat.com> - 10-5
- merge -sysvinit into main package

* Mon Sep 20 2010 Bill Nottingham <notting@redhat.com> - 10-4
- obsolete upstart-sysvinit too

* Fri Sep 17 2010 Bill Nottingham <notting@redhat.com> - 10-3
- Drop upstart requires

* Tue Sep 14 2010 Lennart Poettering <lpoetter@redhat.com> - 10-2
- Enable audit
- https://bugzilla.redhat.com/show_bug.cgi?id=633771

* Tue Sep 14 2010 Lennart Poettering <lpoetter@redhat.com> - 10-1
- New upstream release
- https://bugzilla.redhat.com/show_bug.cgi?id=630401
- https://bugzilla.redhat.com/show_bug.cgi?id=630225
- https://bugzilla.redhat.com/show_bug.cgi?id=626966
- https://bugzilla.redhat.com/show_bug.cgi?id=623456

* Fri Sep  3 2010 Bill Nottingham <notting@redhat.com> - 9-3
- move fedora-specific units to initscripts; require newer version thereof

* Fri Sep  3 2010 Lennart Poettering <lpoetter@redhat.com> - 9-2
- Add missing tarball

* Fri Sep  3 2010 Lennart Poettering <lpoetter@redhat.com> - 9-1
- New upstream version
- Closes 501720, 614619, 621290, 626443, 626477, 627014, 627785, 628913

* Fri Aug 27 2010 Lennart Poettering <lpoetter@redhat.com> - 8-3
- Reexecute after installation, take ownership of /var/run/user
- https://bugzilla.redhat.com/show_bug.cgi?id=627457
- https://bugzilla.redhat.com/show_bug.cgi?id=627634

* Thu Aug 26 2010 Lennart Poettering <lpoetter@redhat.com> - 8-2
- Properly create default.target link

* Wed Aug 25 2010 Lennart Poettering <lpoetter@redhat.com> - 8-1
- New upstream release

* Thu Aug 12 2010 Lennart Poettering <lpoetter@redhat.com> - 7-3
- Fix https://bugzilla.redhat.com/show_bug.cgi?id=623561

* Thu Aug 12 2010 Lennart Poettering <lpoetter@redhat.com> - 7-2
- Fix https://bugzilla.redhat.com/show_bug.cgi?id=623430

* Tue Aug 10 2010 Lennart Poettering <lpoetter@redhat.com> - 7-1
- New upstream release

* Fri Aug  6 2010 Lennart Poettering <lpoetter@redhat.com> - 6-2
- properly hide output on package installation
- pull in coreutils during package installtion

* Fri Aug  6 2010 Lennart Poettering <lpoetter@redhat.com> - 6-1
- New upstream release
- Fixes #621200

* Wed Aug  4 2010 Lennart Poettering <lpoetter@redhat.com> - 5-2
- Add tarball

* Wed Aug  4 2010 Lennart Poettering <lpoetter@redhat.com> - 5-1
- Prepare release 5

* Tue Jul 27 2010 Bill Nottingham <notting@redhat.com> - 4-4
- Add 'sysvinit-userspace' provide to -sysvinit package to fix upgrade/install (#618537)

* Sat Jul 24 2010 Lennart Poettering <lpoetter@redhat.com> - 4-3
- Add libselinux to build dependencies

* Sat Jul 24 2010 Lennart Poettering <lpoetter@redhat.com> - 4-2
- Use the right tarball

* Sat Jul 24 2010 Lennart Poettering <lpoetter@redhat.com> - 4-1
- New upstream release, and make default

* Tue Jul 13 2010 Lennart Poettering <lpoetter@redhat.com> - 3-3
- Used wrong tarball

* Tue Jul 13 2010 Lennart Poettering <lpoetter@redhat.com> - 3-2
- Own /cgroup jointly with libcgroup, since we don't dpend on it anymore

* Tue Jul 13 2010 Lennart Poettering <lpoetter@redhat.com> - 3-1
- New upstream release

* Fri Jul 9 2010 Lennart Poettering <lpoetter@redhat.com> - 2-0
- New upstream release

* Wed Jul 7 2010 Lennart Poettering <lpoetter@redhat.com> - 1-0
- First upstream release

* Tue Jun 29 2010 Lennart Poettering <lpoetter@redhat.com> - 0-0.7.20100629git4176e5
- New snapshot
- Split off -units package where other packages can depend on without pulling in the whole of systemd

* Tue Jun 22 2010 Lennart Poettering <lpoetter@redhat.com> - 0-0.6.20100622gita3723b
- Add missing libtool dependency.

* Tue Jun 22 2010 Lennart Poettering <lpoetter@redhat.com> - 0-0.5.20100622gita3723b
- Update snapshot

* Mon Jun 14 2010 Rahul Sundaram <sundaram@fedoraproject.org> - 0-0.4.20100614git393024
- Pull the latest snapshot that fixes a segfault. Resolves rhbz#603231

* Fri Jun 11 2010 Rahul Sundaram <sundaram@fedoraproject.org> - 0-0.3.20100610git2f198e
- More minor fixes as per review

* Thu Jun 10 2010 Rahul Sundaram <sundaram@fedoraproject.org> - 0-0.2.20100610git2f198e
- Spec improvements from David Hollis

* Wed Jun 09 2010 Rahul Sundaram <sundaram@fedoraproject.org> - 0-0.1.20090609git2f198e
- Address review comments

* Tue Jun 01 2010 Rahul Sundaram <sundaram@fedoraproject.org> - 0-0.0.git2010-06-02
- Initial spec (adopted from Kay Sievers)
