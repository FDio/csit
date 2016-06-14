



def bla(psid, length, offset=6):
    """

    :param psid: PSID
    :param length: PSID length
    :param offset: PSID offset

                      0                   1
                      0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
                     +-----------+-----------+-------+
       Ports in      |     A     |    PSID   |   j   |
    the CE port set  |    > 0    |           |       |
                     +-----------+-----------+-------+
                     |  a bits   |  k bits   |m bits |


    """
    port_field_len = 16
    port_field_min = int('0x0000', 16)
    port_field_max = int('0xffff', 16)


    a = offset
    k = length
    m = port_field_len - offset - length
    km = k + m
    j_max = port_field_max >> a + k

    r = []
    for A in range(1, (port_field_max >> km) + 1):
        r.append((((A << k) | psid) << m, ((A << k) | psid) << m | j_max))

    return r

# for i in bla(1, 8 ):
#     print '{0:16b}, {1:16b}'.format(*i)

for i in bla(52, 8, 6):
    print '{0}, {1}'.format(*i)





