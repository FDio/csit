
"""Process output.xml, output tag expressions with AND only."""

with open("output.xml", "r") as file_in, open("st.txt", "w") as file_out:
    while 1:
        line = file_in.readline()
        if not line:
            break
        if line[0] != '<':
            continue
        splitted = line[1:].split(" ", 1)
        if len(splitted) < 2:
            continue
        out0, rest = splitted
        if out0 not in ("suite", "test"):
            continue
        sep = 'name="' if out0 != "suite" else 'source="'
        _, rest = rest.split(sep, 1)
        out1, _ = rest.split('"', 1)
        if out0 == "suite":
            _, out1 = out1.split("/tests")
        file_out.write(out0)
        file_out.write(" ")
        file_out.write(out1)
        file_out.write("\n")
