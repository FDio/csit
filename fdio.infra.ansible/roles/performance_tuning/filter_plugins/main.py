"""Extra Ansible filters"""

def irqbalance_banned_cpu_mask(
        processor_cores, processor_count, processor_threads_per_core):
    """
    Return irqbalance CPU mask.
    Args:
        processor_cores (int): Physical processor unit.
        processor_counts (int): Processors per physical unit.
        processor_threads_per_core (int): Threads per physical unit.
    Returns:
       str: irqbalance_banned_cpus.
    """
    mask = int("1" * 128, 2)

    for i in range(processor_count * processor_threads_per_core):
        mask &= ~(1 << i * processor_cores)

    import re
    return ",".join(re.findall('.{1,8}', str(hex(mask))[2:]))


class FilterModule(object):
    """Return filter plugin"""

    @staticmethod
    def filters():
        """Return filter"""
        return {'irqbalance_banned_cpu_mask': irqbalance_banned_cpu_mask}
