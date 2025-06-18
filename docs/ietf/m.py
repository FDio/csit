with open("draft-ietf-bmwg-mlrsearch-10.md", "rt") as fin, open("draft-ietf-bmwg-mlrsearch-10.d.md", "wt") as fout:
    for line in fin:
        if "[MB" in line:
            rest, post = line.split("]", 1)
            pre, snum = rest.split("B", 1)
            dnum = (1 + int(snum)) // 2
            line = f"{pre}B{dnum}]{post}"
        fout.write(line)
