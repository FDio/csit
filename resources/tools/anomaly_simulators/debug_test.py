
from collections import deque

from SingleGressionProvider import SingleGressionProvider as provider
from TrivialClassifier import TrivialClassifier as classifier


N = 10
p = provider(1.0, 1.0, 0.1)
groups = deque(p.get_runs(N))
runs = []
for group in groups:
    runs.extend(group.values)
c = classifier()
classes = deque(c.classify(runs))
input_group = None
output_group = None
while 1:
    if input_group is None and groups:
        input_group = groups.popleft()
        print "in", input_group.metadata
        input_group.values = deque(input_group.values)
    if output_group is None and classes:
        output_group = classes.popleft()
        print "out", output_group.metadata
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
