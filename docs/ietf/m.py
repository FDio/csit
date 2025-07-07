with open("draft-ietf-bmwg-mlrsearch-11.md", "rt") as fin, open("draft-ietf-bmwg-mlrsearch-11_u.md", "wb") as fout:
    for line in fin.readlines():
        fout.write(line.encode("ascii"))
