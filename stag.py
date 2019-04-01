
import os
import sys

search_tags = set(["mrr", "ndrpdr"])
nic_tags = set([
    "nic_cisco-vic-1227",
    "nic_cisco-vic-1385",
    "nic_intel-x520-da2",
    "nic_intel-x553",
    "nic_intel-x710",
    "nic_intel-xl710",
    "nic_intel-xxv710",
])
known_tags = search_tags | nic_tags
pyname = "regenerate_testcases.py"

def sstrip(string):
    return string.strip()

def extend_tags(line, tags):
#    print "extending", line
    cells = map(sstrip, line.split("|"))
    if len(cells) < 3 or cells[1] not in ("force tags", "..."):
        return False
    tags.update(cells[2:])
    return True

tag_lines = list()
for dir_path, subdir_names, file_names in os.walk("tests"):
    if "/perf" not in dir_path:
        continue
#    print "descending to", dir_path
    if pyname not in file_names:
        continue
    if not os.access(os.path.join(dir_path, pyname), os.X_OK):
        continue
    for file_name in file_names:
        if not file_name.endswith(".robot") or "__init__" in file_name:
            continue
        with open(os.path.join(dir_path, file_name), "r") as suite_file:
            force_tags = set()
            while 1:
                line = suite_file.readline().lower()
#                print "suite read line", line
                if not line:
                    print "FAIL"
                    sys.exit(1)
                if line.startswith("| force tags |"):
                    break
            while extend_tags(line, force_tags):
                line = suite_file.readline().lower()
            known_tags.update(force_tags)
            tc_tags = list()
            while 1:
                line = suite_file.readline().lower()
#                print "testcase read line", line
                if not line:
                    break
                if not line.startswith("| | [tags] |"):
                    continue
                tc_tag = map(sstrip, line.split("|")[3:])
                known_tags.update(tc_tag)
                tc_tags.append(tc_tag)
#                print "appended", repr(tc_tag)
            force_tags.remove("ndrpdr")
            force_tags.remove("nic_intel-x710")
            for tc_tag in tc_tags:
                tag_set = force_tags | set(tc_tag)
                for search_tag in search_tags:
                    for nic_tag in nic_tags:
                        tag_list = list(tag_set) + [search_tag] + [nic_tag]
                        tag_lines.append("AND".join(sorted(tag_list)))
with open("tags.log", "w") as tag_file:
    for tag_line in tag_lines:
        tag_file.write(tag_line)
        tag_file.write('\n')
print repr(sorted(known_tags))
