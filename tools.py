# module for all routines not directly connected to any other modules

def hier_sum(current: list):
    """ hierarchic sum/linear combination of elements """
    length = len(current)
    while length > 1:
        next = []
        for i in range(length//2): # floor division
            next.append(current[2*i] + current[2*i+1])
        if length % 2 == 1:
            next[0] += current[-1]
        current = next
        length = len(current)
    return current[0]