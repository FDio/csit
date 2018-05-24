
from collections import deque

from SingleGressionProvider import SingleGressionProvider as provider
from TrivialClassifier import TrivialClassifier as classifier


N = 1000
n = 200
p = provider(1000, 1000, 2.0, 1.0)
undetected = 0
while 1:
    print
    group_list = p.get_runs(N, n)
    groups = deque(group_list)
    runs = []
    for group in groups:
        runs.extend(group.values)
    c = classifier()
    class_list = c.classify(runs)
    classes = deque(class_list)
    stdev = class_list[0].metadata.stdev
    first_avg = group_list[0].metadata.avg
    second_avg = group_list[1].metadata.avg
    jump = abs(first_avg - second_avg) / stdev
    print "Anomaly jumps by {jump} stdevs.".format(jump=jump)

    input_group = None
    output_group = None
    input_bits = 0.0
    output_bits = 0.0
    while 1:
        if input_group is None and groups:
            input_group = groups.popleft()
            print "in", input_group.metadata
            print "bits per sample", input_group.metadata.bits / input_group.metadata.size
            input_bits += input_group.metadata.bits
            input_group.values = deque(input_group.values)
        if output_group is None and classes:
            output_group = classes.popleft()
            print "out", output_group.metadata
            print "bits per sample", output_group.metadata.bits / output_group.metadata.size
            output_bits += output_group.metadata.bits
            output_group.values = deque(output_group.values)
        if input_group is None or output_group is None:
            break
        cont = False
        if not input_group.values:
            input_group = None
            cont = True
        if not output_group.values:
            output_group = None
            cont = True
        if cont:
            continue
    #    print "in pop", 
        input_group.values.popleft()
    ##    print "in remains", repr(input_group.values)
    #    print "out pop", 
        output_group.values.popleft()
    ##    print "out remains", repr(output_group.values)
    if input_group is not None:
        print "input leftovers", repr(input_group), repr(input_group.values)
    if output_group is not None:
        print "output leftovers", repr(output_group), repr(output_group.values)
    if output_bits > input_bits:
        print "input is encoded by {bits} bits less, anomaly is detected.".format(
            bits=(output_bits - input_bits))
        print "detection success is {succ}".format(succ=1.0/(1.0+undetected))
        break
    else:
        print "input is encoded by {bits} bits more, anomaly is undetected.".format(
            bits=(input_bits - output_bits))
        undetected += 1
