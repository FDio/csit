
"""Extra Ansible filters"""

def deb_kernel(packages, kernel_version, current_version):
    """
    Return best matching kernel version.
    Args:
        packages (dict): apt-cache showpkg output.
        kernel_version (str): Kernel version to install.
        current_version (str): Current kernel version.
    Returns:
       str: kernel version.
    """
    kernels = set()

    # List all available kernel version and associated repository
    for line in packages['stdout'].splitlines():
        line = line.strip()
        if line.startswith('Package: ') and (
                line.endswith('-common') or  # Debian
                line.endswith('-generic')):  # Ubuntu
            kernel = line.split()[1]

            for string in ('linux-headers-', 'common', 'generic'):
                kernel = kernel.replace(string, '')
            kernel = kernel.strip('-')

            if kernel:
                kernels.add(kernel)

    # Sort Kernel versions
    versions = {}
    for kernel in kernels:
        try:
            version, build = kernel.split('-', 1)
        except ValueError:
            version = kernel
            build = ''
        versions[kernel] = list(
            int(ver) for ver in version.split('.')) + [build]
    kernels = sorted(versions.keys(), key=versions.get, reverse=True)

    # Return more recent kernel package that match version requirement
    for kernel in kernels:
        if kernel.startswith(kernel_version):
            return kernel

    raise RuntimeError(
        'No kernel matching to "%s". Available kernel versions: %s' % (
            kernel_version, ', '.join(reversed(kernels))))


def _deb_kernel_package(kernel, dist, arch, name):
    """
    Return kernel package name.
    Args:
        kernel (str): Kernel version.
        dist (str): Distribution.
        arch (str): Architecture.
        name (str): Package name.
    Returns:
       str: kernel package.
    """
    # Define package suffix
    if dist == 'Ubuntu':
        suffix = 'generic'
    elif name == 'linux-image':
        suffix = arch.replace('x86_64', 'amd64')
    else:
        suffix = 'common'

    return '-'.join((name, kernel, suffix))


def deb_kernel_pkg(packages, kernel_version, current_version, dist, arch, name):
    """
    Return kernel package to install.
    Args:
        packages (dict): apt-cache showpkg output.
        kernel_version (str): Kernel version to install.
        current_version (str): Current kernel version.
        dist (str): Distribution.
        arch (str): Architecture.
        name (str): Package name.
    Returns:
       str: kernel package to install.
    """
    return _deb_kernel_package(
        deb_kernel(packages, kernel_version, current_version), dist, arch, name)


def deb_installed_kernel(installed, packages, kernel_version, current_version):
    """
    Return old kernel packages to remove.
    Args:
        installed (dict): dpkg -l output.
        packages (dict): apt-cache showpkg output.
        kernel_version (str): Kernel version to install.
        current_version (str): Current kernel version.
    Returns:
       list of str: Kernel packages to remove.
    """
    # Filter installed package to keep
    to_keep = deb_kernel(packages, kernel_version, current_version)

    # Return installed package to remove
    to_remove = []
    for line in installed['stdout'].splitlines():
        if ' linux-' not in line:
            continue

        package = line.split()[1]
        if ((package.startswith('linux-image-') or
             package.startswith('linux-headers-')) and not (
             package.startswith('linux-image-' + to_keep) or
             package.startswith('linux-headers-' + to_keep))):
            to_remove.append(package)

    return to_remove


def kernel_match(kernel, kernel_spec):
    """
    Check if kernel version match.
    Args:
        kernel (str): Kernel
        kernel_spec (str): Kernel to match.
    Returns:
        bool: True if Kernel match.
    """
    return kernel.startswith(kernel_spec)


class FilterModule(object):
    """Return filter plugin"""

    @staticmethod
    def filters():
        """Return filter"""
        return {'deb_kernel': deb_kernel,
                'deb_kernel_pkg': deb_kernel_pkg,
                'deb_installed_kernel': deb_installed_kernel,
                'kernel_match': kernel_match}
