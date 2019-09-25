
import subprocess


MESSAGE_TEMPLATE = "Command {com} ended with RC {ret} and output:\n{out}"


def run(command, msg="", check=True, log=True, console=True):
    """Wrapper around subprocess.check_output that can tolerates nonzero RCs.

    Stderr is redirected to stdout, so it is part of output
    (but can be mingled as the two streams are buffered independently).
    If check and rc is nonzero, RuntimeError is raised.
    If log (and not checked failure), both rc and output are logged.
    Logging is performed on logging module. By default .debug(),
    optionally print instead.
    The default log message is optionally prepended by user-given string,
    separated by ": ".

    Commands given as single string are not supported, for safety reasons.
    Invoke bash explicitly if you need its glob support for arguments.

    :param command: List of commands and arguments. Split your long string.
    :param msg: Message prefix. Argument name is short just to save space.
    :param check: Whether to raise if return code is nonzero.
    :param log: Whether to log results.
    :param console: Whether use .console() instead of .debug().
        Mainly useful when running from non-main thread.
    :type command: Iterable or OptionString
    :type msg: str
    :type check: bool
    :type log: bool
    :type console: bool
    :returns: rc and output
    :rtype: 2-tuple of int and str
    :raises RuntimeError: If check is true and return code non-zero.
    :raises TypeError: If command is not an iterable.
    """
    if not hasattr(command, "__iter__"):
        # Strings are indexable, but turning into iterator is not supported.
        raise TypeError("Command {cmd!r} is not an iterable.".format(
            cmd=command))
    ret_code = 0
    output = ""
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        output = err.output
        ret_code = err.returncode
        if check:
            raise RuntimeError(MESSAGE_TEMPLATE.format(
                com=err.cmd, ret=ret_code, out=output))
    if log:
        message = MESSAGE_TEMPLATE.format(com=command, ret=ret_code, out=output)
        if msg:
            message = msg + ": " + message
        if console:
            print(message)
        else:
            logging.debug(message)
    return ret_code, output


run(["git", "bisect", "start"])
try:
    run(["git", "bisect", "bad"])
    run(["git", "checkout", "5cbeca02602061d32212e14f289d65cf648920e4"])
    gbcl = ["git", "bisect", "good"]
    run(gbcl)
    while 1:
        rc, output = run(gbcl)
        if not output.startswith("Bisecting"):
            break
#    rc, output, = run(["git", "bisect", "run", "bash", "-c", "if (( $RANDOM % 2 )); then false; fi"])
finally:
    run(["git", "bisect", "reset"])
