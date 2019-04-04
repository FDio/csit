
"""Process output.xml, output tag expressions with AND only."""

with open("output.xml", "r") as file_in, open("o.txt", "w") as file_out:
    while 1:
        line = file_in.readline()
        if not line:
            break
        if line != "<tags>\n":
            continue
        out = list()
        while 1:
            line = file_in.readline().lower()
            if not line or not line.startswith("<tag>"):
                break
            line = line[5:-7]
            len_line = len(line)
            if line == "perftest":
                continue
            if len_line == 4 and line[1] == 't' and line[3] == 'c':
                continue
            if line[1:7] == "_node_" and line[-10:] == "_link_topo":
                continue
            if line[1:] == "thread":
                continue
            out.append(line)
        file_out.write("AND".join(out))
        file_out.write("\n")
