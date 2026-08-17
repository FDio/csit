# Copyright (c) 2026 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Host Stack util library."""

import json
import re
from time import sleep

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.DUTSetup import DUTSetup
from resources.libraries.python.model.ExportResult import (
    export_hoststack_results,
)
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import exec_cmd, exec_cmd_no_error
from resources.libraries.python.topology import Topology


class HoststackUtil:
    """Utilities for Host Stack tests."""

    @staticmethod
    def _get_ldpreload_path(node):
        """Return the absolute path to VCL LD_PRELOAD library.

        If Constants override the path, return that.
        Otherwise return the default pattern, with arch value from topology.

        :param node: Topology node to decide architecture.
        :type node: dict
        :returns: Path to correct VCL preload library.
        :rtype: str
        """
        if ret := Constants.VCL_LDPRELOAD_LIBRARY:
            return ret
        arch = Topology.get_node_arch(node)
        return f"/usr/lib/{arch}-linux-gnu/libvcl_ldpreload.so"

    @staticmethod
    def get_iperf3_command(iperf3_attributes, node):
        """Construct the iperf3 command using the specified attributes.

        :param iperf3_attributes: iperf3 test program attributes.
        :param node: Topology node (architecture implies ldpreload path).
        :type iperf3_attributes: dict
        :type node: dict
        :returns: Command line components of the iperf3 command
            'env_vars' - environment variables
            'name' - program name
            'args' - command arguments.
        :rtype: dict
        """
        iperf3_cmd = {}
        iperf3_cmd["env_vars"] = (
            f"VCL_CONFIG={Constants.REMOTE_FW_DIR}/"
            f"{Constants.RESOURCES_TPL_VCL}/"
            f"{iperf3_attributes['vcl_config']}"
        )
        if iperf3_attributes["ld_preload"]:
            ldpreload = HoststackUtil._get_ldpreload_path(node)
            iperf3_cmd["env_vars"] += f" LD_PRELOAD={ldpreload}"
        if iperf3_attributes["transparent_tls"]:
            iperf3_cmd["env_vars"] += " LDP_ENV_TLS_TRANS=1"

        json_results = " --json" if iperf3_attributes["json"] else ""
        ip_address = (
            f" {iperf3_attributes['ip_address']}"
            if "ip_address" in iperf3_attributes
            else ""
        )
        iperf3_cmd["name"] = "iperf3"
        iperf3_cmd["args"] = (
            f"--{iperf3_attributes['role']}{ip_address} "
            f"--interval 0{json_results} "
            f"--version{iperf3_attributes['ip_version']}"
        )

        if iperf3_attributes["role"] == "server":
            iperf3_cmd["args"] += " --one-off"
        else:
            iperf3_cmd["args"] += " --get-server-output"
            if "parallel" in iperf3_attributes:
                iperf3_cmd[
                    "args"
                ] += f" --parallel {iperf3_attributes['parallel']}"
            if "time" in iperf3_attributes:
                iperf3_cmd["args"] += f" --time {iperf3_attributes['time']}"
            if iperf3_attributes["udp"]:
                iperf3_cmd["args"] += " --udp"
                iperf3_cmd[
                    "args"
                ] += f" --bandwidth {iperf3_attributes['bandwidth']}"
            if iperf3_attributes["length"] > 0:
                iperf3_cmd[
                    "args"
                ] += f" --length {iperf3_attributes['length']}"
        return iperf3_cmd

    @staticmethod
    def get_vperf_command(vperf_attributes):
        """Construct the vperf_client / vperf_server command line.

        :param vperf_attributes: vperf program attributes.
        :type vperf_attributes: dict
        :returns: Command line components of the vperf_client/server
            command:
            'env_vars' - environment variables
            'name'     - program name (vperf_client or vperf_server)
            'args'     - command arguments.
        :rtype: dict
        """
        role = vperf_attributes["role"]
        env_vars = (
            f"VCL_VPP_SAPI_SOCKET={vperf_attributes['app_api_socket']}"
        )
        if vperf_attributes.get("vcl_config"):
            env_vars = (
                f"VCL_CONFIG={Constants.REMOTE_FW_DIR}/"
                f"{Constants.RESOURCES_TPL_VCL}/"
                f"{vperf_attributes['vcl_config']} {env_vars}"
            )
        vperf_cmd = {
            "env_vars": env_vars,
            "name": f"vperf_{role}",
            "args": "",
        }

        if role == "client":
            if vperf_attributes.get("bytes"):
                # Use -b <total-bytes> instead of -N <num-writes> so that the
                # test duration is bounded by total data, not by write count.
                vperf_cmd["args"] += (
                    f" -b {vperf_attributes['bytes']}"
                )
            elif vperf_attributes.get("num_writes"):
                vperf_cmd["args"] += (
                    f" -N {vperf_attributes['num_writes']}"
                )
                if vperf_attributes.get("tx_buff"):
                    vperf_cmd["args"] += (
                        f" -T {vperf_attributes['tx_buff']}"
                    )
                if vperf_attributes.get("rx_buff"):
                    vperf_cmd["args"] += (
                        f" -R {vperf_attributes['rx_buff']}"
                    )
            if vperf_attributes.get("uni_direct"):
                vperf_cmd["args"] += " -U"
            elif vperf_attributes.get("bi_direct"):
                vperf_cmd["args"] += " -B"
            # -s <total_sessions> = nclients * quic_streams
            # -q <quic_streams>   = streams per session
            # e.g. 10 clients x 10 streams -> -s 100 -q 10
            nclients = int(vperf_attributes.get("nclients", 1))
            quic_streams = int(vperf_attributes.get("quic_streams", 1))
            total_sessions = nclients * quic_streams
            if total_sessions > 1:
                vperf_cmd["args"] += f" -s {total_sessions} -q {quic_streams}"
            # Always exit after the test run so the process does not block
            # on user input (vtc_read_user_input) after completion.
            vperf_cmd["args"] += " -X"

        if vperf_attributes.get("print_stats"):
            vperf_cmd["args"] += " -S"

        if vperf_attributes.get("protocol"):
            vperf_cmd["args"] += f" -p {vperf_attributes['protocol']}"

        if role == "server":
            # -w <N> is only valid for N > 1; without it, the server uses
            # a single worker by default.
            if vperf_attributes.get("cpu_cnt", 1) > 1:
                vperf_cmd["args"] += (
                    f" -w {vperf_attributes['cpu_cnt']}"
                )
            vperf_cmd["args"] += f" {vperf_attributes['port']}"
        else:
            vperf_cmd["args"] += (
                f" {vperf_attributes['ip4_addr']} "
                f"{vperf_attributes['port']}"
            )
        return vperf_cmd

    @staticmethod
    def set_hoststack_quic_fifo_size(node, fifo_size):
        """Set the QUIC protocol fifo size.

        :param node: Node to set the QUIC fifo size on.
        :param fifo_size: fifo size, passed to the quic set fifo-size command.
        :type node: dict
        :type fifo_size: str
        """
        cmd = f"quic set fifo-size {fifo_size}"
        PapiSocketExecutor.run_cli_cmd(node, cmd)

    @staticmethod
    def set_hoststack_quic_crypto_engine(
        node, quic_crypto_engine, fail_on_error=False
    ):
        """Set the Hoststack QUIC crypto engine on node

        :param node: Node to enable/disable HostStack.
        :param quic_crypto_engine: type of crypto engine
        :type node: dict
        :type quic_crypto_engine: str
        """
        vpp_crypto_engines = {"openssl", "native", "ipsecmb"}
        if quic_crypto_engine == "nocrypto":
            logger.trace("No QUIC crypto engine.")
            return

        if quic_crypto_engine in vpp_crypto_engines:
            cmds = [
                "quic set crypto api vpp",
                f"set crypto handler aes-128-gcm {quic_crypto_engine}",
                f"set crypto handler aes-256-gcm {quic_crypto_engine}",
            ]
        elif quic_crypto_engine == "picotls":
            cmds = ["quic set crypto api picotls"]
        else:
            raise ValueError(f"Unknown QUIC crypto_engine {quic_crypto_engine}")

        for cmd in cmds:
            try:
                PapiSocketExecutor.run_cli_cmd(node, cmd)
            except AssertionError:
                if fail_on_error:
                    raise

    @staticmethod
    def _get_hoststack_test_program_logs(node, program_name):
        """Get HostStack test program stdout log.

        :param node: DUT node.
        :param program_name: test program.
        :type node: dict
        :type program_name: str
        """
        cmd = f"sh -c 'cat /tmp/{program_name}_stdout.log'"
        stdout_log, _ = exec_cmd_no_error(
            node,
            cmd,
            sudo=True,
            message=f"Get {program_name} stdout log failed!",
        )

        cmd = f"sh -c 'cat /tmp/{program_name}_stderr.log'"
        stderr_log, _ = exec_cmd_no_error(
            node,
            cmd,
            sudo=True,
            message=f"Get {program_name} stderr log failed!",
        )

        return stdout_log, stderr_log

    @staticmethod
    def get_hoststack_test_program_logs(node, program):
        """Get HostStack test program stdout log.

        :param node: DUT node.
        :param program: test program.
        :type node: dict
        :type program: dict
        """
        program_name = program["name"]
        program_stdout_log, program_stderr_log = (
            HoststackUtil._get_hoststack_test_program_logs(node, program_name)
        )
        if len(program_stdout_log) == 0 and len(program_stderr_log) == 0:
            logger.trace(f"Retrying {program_name} log retrieval")
            program_stdout_log, program_stderr_log = (
                HoststackUtil._get_hoststack_test_program_logs(
                    node, program_name
                )
            )
        return program_stdout_log, program_stderr_log

    @staticmethod
    def get_nginx_command(nginx_attributes, nginx_version, nginx_ins_dir, node):
        """Construct the NGINX command using the specified attributes.

        :param nginx_attributes: NGINX test program attributes.
        :param nginx_version: NGINX version.
        :param nginx_ins_dir: NGINX install dir.
        :param node: Topology node (architecture implies ldpreload path).
        :type nginx_attributes: dict
        :type nginx_version: str
        :type nginx_ins_dir: str
        :type node: dict
        :returns: Command line components of the NGINX command
            'env_vars' - environment variables
            'name' - program name
            'args' - command arguments.
            'path' - program path.
        :rtype: dict
        """
        nginx_cmd = dict()
        nginx_cmd["env_vars"] = (
            f"VCL_CONFIG={Constants.REMOTE_FW_DIR}/"
            f"{Constants.RESOURCES_TPL_VCL}/"
            f"{nginx_attributes['vcl_config']}"
        )
        if nginx_attributes["ld_preload"]:
            ldpreload = HoststackUtil._get_ldpreload_path(node)
            nginx_cmd["env_vars"] += f" LD_PRELOAD={ldpreload}"
        if nginx_attributes["transparent_tls"]:
            nginx_cmd["env_vars"] += " LDP_ENV_TLS_TRANS=1"

        nginx_cmd["name"] = "nginx"
        nginx_cmd["path"] = f"{nginx_ins_dir}nginx-{nginx_version}/sbin/"
        nginx_cmd["args"] = (
            f"-c {nginx_ins_dir}/" f"nginx-{nginx_version}/conf/nginx.conf"
        )
        return nginx_cmd

    @staticmethod
    def start_hoststack_test_program(node, namespace, core_list, program):
        """Start the specified HostStack test program.

        :param node: DUT node.
        :param namespace: Net Namespace to run program in.
        :param core_list: List of cpu's to pass to taskset to pin the test
            program to a different set of cores on the same numa node as VPP.
        :param program: Test program.
        :type node: dict
        :type namespace: str
        :type core_list: str
        :type program: dict
        :returns: Process ID
        :rtype: int
        :raises RuntimeError: If node subtype is not a DUT or startup failed.
        """
        if node["type"] != "DUT":
            raise RuntimeError("Node type is not a DUT!")

        program_name = program["name"]
        DUTSetup.kill_program(node, program_name, namespace)

        if namespace == "default":
            shell_cmd = "sh -c"
        else:
            shell_cmd = f"ip netns exec {namespace} sh -c"

        env_vars = f"{program['env_vars']} " if "env_vars" in program else ""
        args = program["args"]
        program_path = program.get("path", "")
        # NGINX handles its own affinity via `worker_cpu_affinity`.
        # Everything else must be pinned via taskset to the caller-
        # provided core_list (already on the NIC's NUMA in
        # hoststack.robot), otherwise on isolcpus-heavy CI hosts the
        # scheduler lands them cross-socket vs VPP + NIC.
        # vperf uses VCL (user-space TCP over shared-mem FIFOs) and
        # must NOT be `chrt -r 99`: on isolcpus + nohz_full the RT
        # bandwidth throttle (sched_rt_runtime_us) preempts it
        # periodically, collapsing TCP cwnd (visible as sawtooth
        # 44 -> ~1 Gbps in the vperf output).  iperf3 uses kernel
        # sockets and does benefit from SCHED_FIFO 99.
        taskset_cmd = ""
        if program_name == "nginx":
            taskset_cmd = ""
        elif program_name in ("vperf_client", "vperf_server"):
            taskset_cmd = f"taskset --cpu-list {core_list} "
        else:
            taskset_cmd = f"taskset --cpu-list {core_list} chrt -r 99 "
        cmd = (
            f"nohup {taskset_cmd}{shell_cmd} '{env_vars} "
            f"{program_path}{program_name} {args} >/tmp/{program_name}_"
            f"stdout.log 2>/tmp/{program_name}_stderr.log &'"
        )
        try:
            exec_cmd_no_error(node, cmd, sudo=True)
            return DUTSetup.get_pid(node, program_name)[0]
        except RuntimeError:
            stdout_log, stderr_log = (
                HoststackUtil.get_hoststack_test_program_logs(node, program)
            )
            raise RuntimeError(
                f"Start {program_name} failed!\nSTDERR:\n"
                f"{stderr_log}\nSTDOUT:\n{stdout_log}"
            )
        return None

    @staticmethod
    def stop_hoststack_test_program(node, program, pid):
        """Stop the specified Hoststack test program.

        :param node: DUT node.
        :param program: Test program.
        :param pid: Process ID of test program.
        :type node: dict
        :type program: dict
        :type pid: int
        """
        program_name = program["name"]
        if program_name == "nginx":
            cmd = "nginx -s quit"
            errmsg = "Quit nginx failed!"
        else:
            cmd = (
                f'if [ -n "$(ps {pid} | grep {program_name})" ] ; '
                f"then kill -s SIGTERM {pid}; fi"
            )
            errmsg = f"Kill {program_name} ({pid}) failed!"

        exec_cmd_no_error(node, cmd, message=errmsg, sudo=True)

    @staticmethod
    def sleep_for_hoststack_test_duration(sleep_time):
        """Wait for the HostStack test program process to complete.

        :param sleep_time: waiting stecific time.
        """
        logger.info(f"Sleeping for {sleep_time} seconds")
        sleep(sleep_time + 1)

    @staticmethod
    def _sample_system_metrics(node, tag):
        """Runtime snapshot of the load-time signals not covered by the
        one-shot environment baseline: for each core >= 25% busy, log
        its **delivered** frequency (APERF/MPERF delta, matches
        turbostat's Bzy_MHz) alongside the P-state driver's requested
        frequency, its NUMA/package id, the top process(es) landed on
        it; plus a compact CPU package temperature line and a
        hugepages usage line.

        Static info (arch, top-N process table, ``free -h``, full CPU
        temperature enumeration) is intentionally omitted -- it lives
        in :meth:`_log_environment_baseline`.  APERF/MPERF is x86-only
        and requires ``msr-tools`` (``rdmsr``) plus the ``msr`` kernel
        module; if either is missing (e.g. on ARM DUTs) the ``actual``
        column is simply left off.

        :param node: DUT node to sample.
        :param tag: Free-form label included in the log (e.g. program name).
        :type node: dict
        :type tag: str
        """
        busy_threshold = 25.0
        max_busy_reported = 24

        # /proc/stat delta over 1s + APERF/MPERF delta over the same
        # window (only if rdmsr is installed).  Everything in a single
        # SSH round-trip so we don't drift.
        stat_cmd = (
            "sh -c \""
            "grep '^cpu[0-9]' /proc/stat > /tmp/_hs_stat1; "
            "have=0; "
            "modprobe msr 2>/dev/null; "
            "command -v rdmsr >/dev/null 2>&1 && have=1; "
            "if [ \\$have -eq 1 ]; then "
            "  rdmsr -a 0xE8 > /tmp/_hs_aperf1 2>/dev/null || "
            "    : > /tmp/_hs_aperf1; "
            "  rdmsr -a 0xE7 > /tmp/_hs_mperf1 2>/dev/null || "
            "    : > /tmp/_hs_mperf1; "
            "fi; "
            "sleep 1; "
            "grep '^cpu[0-9]' /proc/stat > /tmp/_hs_stat2; "
            "if [ \\$have -eq 1 ]; then "
            "  rdmsr -a 0xE8 > /tmp/_hs_aperf2 2>/dev/null || "
            "    : > /tmp/_hs_aperf2; "
            "  rdmsr -a 0xE7 > /tmp/_hs_mperf2 2>/dev/null || "
            "    : > /tmp/_hs_mperf2; "
            "fi; "
            "echo === STAT ===; "
            "paste /tmp/_hs_stat1 /tmp/_hs_stat2; "
            "echo === MSR ===; "
            "[ \\$have -eq 1 ] && paste /tmp/_hs_aperf1 "
            "/tmp/_hs_mperf1 /tmp/_hs_aperf2 /tmp/_hs_mperf2\""
        )
        try:
            _, stat_out, _ = exec_cmd(node, stat_cmd, sudo=True)
        except Exception:  # pylint: disable=broad-except
            stat_out = ""

        # Split into STAT and MSR sections.
        stat_lines, msr_lines = [], []
        section = None
        for line in (stat_out or "").splitlines():
            s = line.strip()
            if s == "=== STAT ===":
                section = "stat"
                continue
            if s == "=== MSR ===":
                section = "msr"
                continue
            if section == "stat":
                stat_lines.append(line)
            elif section == "msr":
                msr_lines.append(line)

        busy_cores = []
        for line in stat_lines:
            parts = line.split()
            # 8 fields per sample (name + user nice system idle iowait
            # irq softirq); paste joins them side by side -> 16 fields.
            if len(parts) < 16 or not parts[0].startswith("cpu"):
                continue
            try:
                core = parts[0]
                u1, n1, s1, i1, w1, q1, x1 = map(int, parts[1:8])
                u2, n2, s2, i2, w2, q2, x2 = map(int, parts[9:16])
                total1 = u1 + n1 + s1 + i1 + w1 + q1 + x1
                total2 = u2 + n2 + s2 + i2 + w2 + q2 + x2
                idle_delta = (i2 + w2) - (i1 + w1)
                delta = total2 - total1
                if delta <= 0:
                    continue
                usage = 100.0 * (delta - idle_delta) / delta
                if usage >= busy_threshold:
                    busy_cores.append((core, usage))
            except (ValueError, IndexError):
                continue

        # APERF/MPERF -> delivered MHz per CPU. rdmsr -a emits one hex
        # value per online CPU in ascending index order, so line index
        # == cpu index.  MSRs are 64-bit; mask to handle wrap (in 1s at
        # a few GHz there is no wrap in practice).
        core_actual_mhz = {}
        for cpu_i, line in enumerate(msr_lines):
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                a1 = int(parts[0], 16)
                m1 = int(parts[1], 16)
                a2 = int(parts[2], 16)
                m2 = int(parts[3], 16)
            except ValueError:
                continue
            da = (a2 - a1) & 0xFFFFFFFFFFFFFFFF
            dm = (m2 - m1) & 0xFFFFFFFFFFFFFFFF
            if dm == 0:
                continue
            # ~1s window -> ΔAPERF / 1e6 = delivered MHz. Small sleep
            # drift is negligible for "at turbo or at base" decisions.
            core_actual_mhz[cpu_i] = int(da // 1_000_000)

        # Per-CPU topology + requested (P-state) frequency, one call.
        topo_cmd = (
            "sh -c '"
            "for c in /sys/devices/system/cpu/cpu[0-9]*; do "
            "n=${c##*/cpu}; "
            "pkg=$(cat $c/topology/physical_package_id 2>/dev/null); "
            "numa=$(basename $(readlink -f $c/node* 2>/dev/null) 2>/dev/null); "
            "f=$(cat $c/cpufreq/scaling_cur_freq 2>/dev/null); "
            "echo \"$n pkg=$pkg node=$numa freq_khz=$f\"; "
            "done'"
        )
        try:
            _, topo_out, _ = exec_cmd(node, topo_cmd)
        except Exception:  # pylint: disable=broad-except
            topo_out = ""
        core_topo = {}
        for line in (topo_out or "").splitlines():
            parts = line.split()
            if not parts:
                continue
            try:
                core_i = int(parts[0])
            except ValueError:
                continue
            d = {}
            for tok in parts[1:]:
                if "=" in tok:
                    k, v = tok.split("=", 1)
                    d[k] = v
            core_topo[core_i] = d

        # ps table is parsed to attach processes to busy cores; not
        # printed in full.
        try:
            _, ps_out, _ = exec_cmd(
                node,
                "sh -c 'ps -eo pid,psr,pcpu,comm --sort=-pcpu | head -40'",
            )
        except Exception:  # pylint: disable=broad-except
            ps_out = ""
        core_to_procs = {}
        for line in (ps_out or "").splitlines()[1:]:
            fields = line.split(None, 3)
            if len(fields) < 4:
                continue
            pid, psr, pcpu, comm = fields
            try:
                psr_i = int(psr)
            except ValueError:
                continue
            core_to_procs.setdefault(psr_i, []).append(
                f"pid={pid} %cpu={pcpu} {comm}"
            )

        # Package-level CPU temps only.  Intel: coretemp Package id N.
        # AMD: k10temp Tctl / Tccd*.  ARM: fall back to thermal_zone
        # types that look CPU/SoC related.
        temp_cmd = (
            "sh -c '"
            "matched=0; "
            "for h in /sys/class/hwmon/hwmon*; do "
            "  n=$(cat $h/name 2>/dev/null); "
            "  case \"$n\" in coretemp|k10temp|zenpower) ;; *) continue ;; esac; "
            "  for t in $h/temp*_input; do "
            "    [ -r \"$t\" ] || continue; "
            "    lbl=$(cat ${t%_input}_label 2>/dev/null); "
            "    case \"$lbl\" in Package*|Tctl*|Tccd*) ;; *) continue ;; esac; "
            "    v=$(cat $t 2>/dev/null); "
            "    [ -n \"$v\" ] && "
            "      awk -v n=\"$n\" -v l=\"$lbl\" -v v=\"$v\" "
            "        \"BEGIN{printf \\\"%s/%s=%.1fC \\\", n, l, v/1000}\" && "
            "    matched=1; "
            "  done; "
            "done; "
            "if [ $matched -eq 0 ]; then "
            "  for z in /sys/class/thermal/thermal_zone*; do "
            "    y=$(cat $z/type 2>/dev/null); "
            "    case \"$y\" in cpu*|CPU*|soc*|SoC*|TSKN*|package*|x86_pkg_temp) ;; "
            "      *) continue ;; esac; "
            "    v=$(cat $z/temp 2>/dev/null); "
            "    [ -n \"$v\" ] && "
            "      awk -v y=\"$y\" -v v=\"$v\" "
            "        \"BEGIN{printf \\\"%s=%.1fC \\\", y, v/1000}\"; "
            "  done; "
            "fi; echo'"
        )
        try:
            _, temp_out, _ = exec_cmd(node, temp_cmd)
        except Exception:  # pylint: disable=broad-except
            temp_out = ""

        huge_cmd = (
            "sh -c 'grep -E "
            "\"^(HugePages_(Total|Free|Rsvd|Surp)|Hugepagesize)\" "
            "/proc/meminfo | awk \"{printf \\\"%s=%s%s \\\", "
            "\\$1, \\$2, (\\$3?\\$3:\\\"\\\")}\" && echo'"
        )
        try:
            _, huge_out, _ = exec_cmd(node, huge_cmd)
        except Exception:  # pylint: disable=broad-except
            huge_out = ""

        host = node.get("host", "?")
        lines = [f"Runtime metrics [{tag}] on {host}:"]
        if busy_cores:
            busy_cores.sort(key=lambda x: -x[1])
            shown = busy_cores[:max_busy_reported]
            hidden = len(busy_cores) - len(shown)
            has_actual = any(
                core_actual_mhz.get(
                    int(c.replace("cpu", "")) if c.startswith("cpu") else -1
                ) is not None
                for c, _ in shown
            )
            legend = "req = P-state target"
            if has_actual:
                legend += ", actual = APERF/MPERF delivered"
            lines.append(
                f"Busy>={busy_threshold:.0f}% "
                f"({len(shown)}/{len(busy_cores)}) [{legend}]:"
            )
            for core, usage in shown:
                try:
                    core_i = int(core.replace("cpu", ""))
                except ValueError:
                    core_i = -1
                d = core_topo.get(core_i, {})
                pkg = d.get("pkg", "?")
                numa = d.get("node", "?")
                req_khz = d.get("freq_khz", "")
                try:
                    req_str = f"req={int(req_khz) // 1000}MHz"
                except ValueError:
                    req_str = "req=?"
                actual = core_actual_mhz.get(core_i)
                act_str = (
                    f" actual={actual}MHz" if actual is not None else ""
                )
                procs = core_to_procs.get(core_i, [])
                procs_str = "; ".join(procs) if procs else "-"
                lines.append(
                    f"  {core} {usage:5.1f}% pkg={pkg} {numa} "
                    f"{req_str}{act_str} -> {procs_str}"
                )
            if hidden > 0:
                lines.append(f"  ... {hidden} more cores omitted")
        else:
            lines.append(f"Busy>={busy_threshold:.0f}%: none")
        lines.append(f"CPU pkg temps: {(temp_out or '').strip() or '-'}")
        lines.append(f"Hugepages: {(huge_out or '').strip() or '-'}")
        logger.trace("\n".join(lines))

    @staticmethod
    def _snapshot_turbostat(node, tag, seconds=3):
        """Best-effort ``turbostat`` capture while the test is running.

        Single 3-sample window (default 1s x 3) — the definitive check
        for actual turbo residency, %c1/%c6, PkgWatt and PkgTmp under
        load. Requires ``turbostat`` (Ubuntu: ``linux-tools-common``)
        and MSR access. Silently no-ops (empty TRACE line) if either
        prerequisite is missing on the CI image.

        :param node: DUT node.
        :param tag: Free-form label included in the log.
        :param seconds: Number of 1-second iterations to capture.
        :type node: dict
        :type tag: str
        :type seconds: int
        """
        cmd = (
            f"sh -c 'if ! command -v turbostat >/dev/null 2>&1; then "
            f"echo turbostat_not_installed; exit 0; fi; "
            f"turbostat --quiet --interval 1 --num_iterations {seconds} "
            f"2>&1'"
        )
        try:
            _, out, _ = exec_cmd(node, cmd, sudo=True)
        except Exception:  # pylint: disable=broad-except
            out = ""
        host = node.get("host", "?")
        logger.trace(
            f"=== turbostat [{tag}] on {host} ({seconds}x1s) ===\n"
            f"{out or '-'}"
        )

    @staticmethod
    def _log_environment_baseline(node, tag):
        """One-shot environment snapshot for cross-testbed comparison.

        Emits kernel cmdline, CPU SKU / microcode / lscpu -e, cpufreq
        governor + turbo + c-state config, CPU vulnerabilities/mitigations,
        RAPL package power limits, NUMA topology, memory / hugepages,
        DMI (BIOS, CPU version, memory speed), PCIe link state + NUMA
        node + driver for every interface listed in the topology, and a
        set of VPP CLI dumps (version / threads / hardware / session /
        tcp / tls / quic).

        Intended to be logged once per DUT per test at TRACE level, so
        two log.html files from different testbeds can be diff'd to spot
        SKU / BIOS / kernel / NIC / VPP-config deltas responsible for
        performance discrepancies.

        :param node: DUT node.
        :param tag: Free-form label included in the log (program name).
        :type node: dict
        :type tag: str
        """
        # (section, shell_cmd, needs_sudo)
        sections = (
            ("kernel", "sh -c 'uname -a; echo ---; cat /proc/cmdline'", False),
            (
                "cpu/model+microcode",
                "sh -c 'grep -m1 -E "
                "\"^(model name|Model|CPU implementer|Hardware|vendor_id)\" "
                "/proc/cpuinfo; grep -m1 microcode /proc/cpuinfo'",
                False,
            ),
            (
                "cpu/lscpu",
                "sh -c 'lscpu 2>/dev/null; echo ---; "
                "lscpu -e 2>/dev/null | head -80'",
                False,
            ),
            (
                "cpu/freq",
                "sh -c '"
                "echo no_turbo=$(cat /sys/devices/system/cpu/intel_pstate/"
                "no_turbo 2>/dev/null); "
                "echo intel_pstate_status=$(cat /sys/devices/system/cpu/"
                "intel_pstate/status 2>/dev/null); "
                "echo intel_idle_max_cstate=$(cat /sys/module/intel_idle/"
                "parameters/max_cstate 2>/dev/null); "
                "for c in /sys/devices/system/cpu/cpu[0-9]*; do "
                "  n=${c##*/cpu}; "
                "  g=$(cat $c/cpufreq/scaling_governor 2>/dev/null); "
                "  mn=$(cat $c/cpufreq/scaling_min_freq 2>/dev/null); "
                "  mx=$(cat $c/cpufreq/scaling_max_freq 2>/dev/null); "
                "  cur=$(cat $c/cpufreq/scaling_cur_freq 2>/dev/null); "
                "  echo cpu$n gov=$g min=$mn max=$mx cur=$cur; "
                "done | head -40'",
                False,
            ),
            (
                "cpu/cstates",
                "sh -c 'for s in /sys/devices/system/cpu/cpu0/cpuidle/state*; "
                "do n=$(cat $s/name 2>/dev/null); "
                "d=$(cat $s/disable 2>/dev/null); "
                "[ -n \"$n\" ] && echo cpu0/${s##*/} $n disable=$d; done'",
                False,
            ),
            (
                "cpu/vulnerabilities",
                "sh -c 'for v in /sys/devices/system/cpu/vulnerabilities/*; "
                "do echo ${v##*/}=$(cat $v 2>/dev/null); done'",
                False,
            ),
            (
                "cpu/rapl_power_limits",
                "sh -c 'for r in /sys/class/powercap/intel-rapl:*/; do "
                "n=$(cat $r/name 2>/dev/null); "
                "for f in $r/constraint_*_power_limit_uw "
                "$r/constraint_*_name $r/constraint_*_time_window_us "
                "$r/enabled; do "
                "[ -r \"$f\" ] && echo $n ${f##*/}=$(cat $f 2>/dev/null); "
                "done; done'",
                False,
            ),
            (
                "numa",
                "sh -c 'numactl --hardware 2>/dev/null; echo ---; "
                "for n in /sys/devices/system/node/node[0-9]*; do "
                "echo $n cpulist=$(cat $n/cpulist 2>/dev/null); "
                "done'",
                False,
            ),
            (
                "memory",
                "sh -c 'free -h; echo ---; grep -i -E "
                "\"^(Huge|MemTotal|MemFree|MemAvailable|DirectMap)\" "
                "/proc/meminfo'",
                False,
            ),
            (
                "dmi/bios+cpu",
                "sh -c 'echo manufacturer=$(dmidecode -s "
                "system-manufacturer 2>/dev/null); "
                "echo product=$(dmidecode -s system-product-name "
                "2>/dev/null); "
                "echo bios_vendor=$(dmidecode -s bios-vendor 2>/dev/null); "
                "echo bios_version=$(dmidecode -s bios-version "
                "2>/dev/null); "
                "echo bios_date=$(dmidecode -s bios-release-date "
                "2>/dev/null); "
                "echo ---; "
                "dmidecode -t processor 2>/dev/null | grep -E "
                "\"(Version|Max Speed|Current Speed|Core Count|"
                "Core Enabled|Thread Count|Signature)\"'",
                True,
            ),
            (
                "dmi/memory",
                "sh -c 'dmidecode -t memory 2>/dev/null | grep -E "
                "\"(Size:|Type:|Speed:|Configured (Memory|Voltage) "
                "Speed:|Locator:|Rank:|Manufacturer:)\" | head -80'",
                True,
            ),
        )

        host = node.get("host", "?")
        lines = [
            f"=== Environment baseline [{tag}] on {host} ===",
        ]
        for section, cmd, sudo in sections:
            try:
                _, out, _ = exec_cmd(node, cmd, sudo=sudo)
            except Exception:  # pylint: disable=broad-except
                out = ""
            lines.append(f"--- {section} ---\n{out or '-'}")

        # Per-interface PCIe + driver + NUMA using topology data
        # (VPP-owned NICs are bound to vfio-pci with no netdev, so we
        # can't rely on ethtool by ifname; look them up by PCI BDF).
        iface_lines = []
        for iface_key, iface in (node.get("interfaces") or {}).items():
            bdf = iface.get("pci_address")
            if not bdf:
                continue
            iface_lines.append(
                f"* interface={iface_key} pci={bdf} "
                f"model={iface.get('model')} "
                f"topo_driver={iface.get('driver')}"
            )
            cmd = (
                f"sh -c 'echo numa_node=$(cat /sys/bus/pci/devices/{bdf}/"
                f"numa_node 2>/dev/null); "
                f"echo current_driver=$(basename $(readlink -f "
                f"/sys/bus/pci/devices/{bdf}/driver 2>/dev/null) "
                f"2>/dev/null); "
                f"lspci -vvv -s {bdf} 2>/dev/null | "
                f"grep -E \"(LnkCap:|LnkSta:|LnkCtl:)\"'"
            )
            try:
                _, out, _ = exec_cmd(node, cmd, sudo=True)
            except Exception:  # pylint: disable=broad-except
                out = ""
            iface_lines.append(out or "-")
        lines.append(
            "--- nic/pcie ---\n"
            + ("\n".join(iface_lines) if iface_lines else "-")
        )

        # VPP CLI dumps confirm the configuration actually landed.
        # Use PapiSocketExecutor.run_cli_cmd defensively; VPP might not
        # yet be responsive on some code paths.
        vpp_cmds = (
            "show version verbose",
            "show threads",
            "show hardware verbose",
            "show session verbose",
            "show tcp",
            "show tls",
            "show quic",
        )
        for vcmd in vpp_cmds:
            try:
                out = PapiSocketExecutor.run_cli_cmd(node, vcmd)
            except Exception:  # pylint: disable=broad-except
                out = ""
            lines.append(f"--- vpp: {vcmd} ---\n{out or '-'}")

        logger.trace("\n".join(lines))

    @staticmethod
    def hoststack_test_program_finished(
        node, program_pid, program, other_node, other_program
    ):
        """Wait for the specified HostStack test program process to complete.

        :param node: DUT node.
        :param program_pid: test program pid.
        :param program: test program
        :param other_node: DUT node of other hoststack program
        :param other_program: other test program
        :type node: dict
        :type program_pid: str
        :type program: dict
        :type other_node: dict
        :type other_program: dict
        :raises RuntimeError: If node subtype is not a DUT.
        """
        if node["type"] != "DUT":
            raise RuntimeError("Node type is not a DUT!")
        if other_node["type"] != "DUT":
            raise RuntimeError("Other node type is not a DUT!")

        if program["name"] in ("vperf_client", "vperf_server", "iperf3"):
            # strace is not applicable for vperf/iperf3; poll until the
            # process exits.  Scale tests (many QUIC sessions, large data
            # volumes) may need significantly more time than base tests;
            # use a generous timeout.
            timeout = 900
            poll_interval = 2
            # Runtime sampler every ~30s -- steady-state signals don't
            # change fast, and denser sampling just spams TRACE.
            metrics_every = 15
            # One-shot per-DUT env dump (BIOS/CPU/kernel/NIC/VPP config)
            # for cross-testbed diffing when CLI access is unavailable.
            HoststackUtil._log_environment_baseline(node, program["name"])
            # turbostat window taken once, right after baseline (program
            # is already running by the time _finished is invoked, so
            # the CPU is under load) -- definitive turbo/c-state check.
            HoststackUtil._snapshot_turbostat(node, program["name"])
            elapsed = 0
            iteration = 0
            while elapsed < timeout:
                ret, _, _ = exec_cmd(
                    node,
                    f"sh -c 'kill -0 {program_pid} 2>/dev/null'",
                    sudo=True,
                )
                if ret != 0:
                    break
                if iteration % metrics_every == 0:
                    HoststackUtil._sample_system_metrics(
                        node, program["name"]
                    )
                sleep(poll_interval)
                elapsed += poll_interval
                iteration += 1
            sleep(1)
            return

        cmd = f"sh -c 'strace -c -fp {program_pid}'"
        try:
            exec_cmd(node, cmd, sudo=True)
        except:
            sleep(180)
            # Use program name (vperf_client …) to
            # determine role rather than args, which vary per program type.
            role = "client" if "client" in program["name"] else "server"
            program_stdout, program_stderr = (
                HoststackUtil.get_hoststack_test_program_logs(node, program)
            )
            if len(program_stdout) > 0:
                logger.debug(
                    f"{program['name']} {role} stdout log:\n"
                    f"{program_stdout}"
                )
            else:
                logger.debug(f"Empty {program['name']} {role} stdout log :(")
            if len(program_stderr) > 0:
                logger.debug(
                    f"{program['name']} stderr log:\n" f"{program_stderr}"
                )
            else:
                logger.debug(f"Empty {program['name']} stderr log :(")
            role = "client" if "client" in other_program["name"] else "server"
            program_stdout, program_stderr = (
                HoststackUtil.get_hoststack_test_program_logs(
                    other_node, other_program
                )
            )
            if len(program_stdout) > 0:
                logger.debug(
                    f"{other_program['name']} {role} stdout log:\n"
                    f"{program_stdout}"
                )
            else:
                logger.debug(
                    f"Empty {other_program['name']} " f"{role} stdout log :("
                )
            if len(program_stderr) > 0:
                logger.debug(
                    f"{other_program['name']} {role} stderr log:\n"
                    f"{program_stderr}"
                )
            else:
                logger.debug(
                    f"Empty {other_program['name']} " f"{role} stderr log :("
                )
            raise
        # Wait a bit for stdout/stderr to be flushed to log files
        sleep(1)

    @staticmethod
    def analyze_hoststack_test_program_output(node, role, nsim_attr, program):
        """Gather HostStack test program output and check for errors.

        The [defer_fail] return bool is used instead of failing immediately
        to allow the analysis of both the client and server instances of
        the test program for debugging a test failure.  When [defer_fail]
        is true, then the string returned is debug output instead of
        JSON formatted test program results.

        :param node: DUT node.
        :param role: Role (client|server) of test program.
        :param nsim_attr: Network Simulation Attributes.
        :param program: Test program.
        :param program_args: List of test program args.
        :type node: dict
        :type role: str
        :type nsim_attr: dict
        :type program: dict
        :returns: tuple of [defer_fail] bool and either JSON formatted hoststack
            test program output or failure debug output.
        :rtype: bool, str
        :raises RuntimeError: If node subtype is not a DUT.
        """
        if node["type"] != "DUT":
            raise RuntimeError("Node type is not a DUT!")

        program_name = program["name"]
        program_stdout, program_stderr = (
            HoststackUtil.get_hoststack_test_program_logs(node, program)
        )

        env_vars = f"{program['env_vars']} " if "env_vars" in program else ""
        program_cmd = f"{env_vars}{program_name} {program['args']}"
        test_results = f"Test Results of '{program_cmd}':\n"

        if nsim_attr["output_nsim_enable"] or nsim_attr["xc_nsim_enable"]:
            if nsim_attr["output_nsim_enable"]:
                feature_name = "output"
            else:
                feature_name = "cross-connect"
            test_results += (
                f"NSIM({feature_name}): delay "
                f"{nsim_attr['delay_in_usec']} usecs, "
                f"avg-pkt-size {nsim_attr['average_packet_size']}, "
                f"bandwidth {nsim_attr['bw_in_bits_per_second']} "
                f"bits/sec, pkt-drop-rate {nsim_attr['packets_per_drop']} "
                f"pkts/drop\n"
            )

        if "error" in program_stderr.lower():
            test_results += f"ERROR DETECTED:\n{program_stderr}"
            return (True, test_results)
        if not program_stdout:
            test_results += f"\nNo {program} test data retrieved!\n"
            ls_stdout, _ = exec_cmd_no_error(
                node, "ls -l /tmp/*.log", sudo=True
            )
            test_results += f"{ls_stdout}\n"
            return (True, test_results)
        if program["name"] == "iperf3":
            test_results += program_stdout
            program_json = json.loads(program_stdout)["intervals"][0]["sum"]
            try:
                retransmits = program_json["retransmits"]
            except KeyError:
                retransmits = None
            export_hoststack_results(
                bandwidth=program_json["bits_per_second"],
                duration=program_json["seconds"],
                retransmits=retransmits,
            )
        elif program["name"] in ("vperf_client", "vperf_server"):
            test_results += program_stdout
            # vperf_test_stats_dump() prints:
            #   CLIENT RESULTS: Streamed <bytes> bytes
            #     in <duration> seconds (<rate> Gbps <duplex>-duplex)!
            # The Gbps line has no colon so key:value splitting misses it.
            # Use a regex to extract both values directly from the raw stdout.
            program_json = {}
            for line in program_stdout.splitlines():
                line = line.strip()
                if ":" not in line:
                    continue
                key, _, value = line.partition(":")
                program_json[key.strip()] = value.strip()
            if program["name"] == "vperf_client":
                m = re.search(
                    r"in\s+([\d.]+)\s+seconds\s+\(([\d.]+)\s+Gbps",
                    program_stdout,
                )
                if m:
                    duration = float(m.group(1))
                    bandwidth = float(m.group(2)) * 1e9
                    export_hoststack_results(
                        bandwidth=bandwidth,
                        duration=duration,
                    )
                else:
                    test_results += "Could not parse vperf_client stats!\n"
                    return (True, test_results)
        else:
            test_results += "Unknown HostStack Test Program!\n" + program_stdout
            return (True, program_stdout)
        return (False, json.dumps(program_json))

    @staticmethod
    def hoststack_test_program_defer_fail(server_defer_fail, client_defer_fail):
        """Return True if either HostStack test program fail was deferred.

        :param server_defer_fail: server no results value.
        :param client_defer_fail: client no results value.
        :type server_defer_fail: bool
        :type client_defer_fail: bool
        :rtype: bool
        """
        return server_defer_fail and client_defer_fail
