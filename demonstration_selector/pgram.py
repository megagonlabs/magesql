
import copy
import functools
import collections
import itertools

from pqnode import Node

class Gram(object):

	def __init__(self, root, p=2, q=3):
        ancestors = collections.deque('*'*p, maxlen=p)
        self.list = list()

        self.profile(root, p, q, ancestors)
        self.sort()

    def gram_list(self, root, p, q, ancestors):
    	ancestors.append(root.label)
        siblings = collections.deque('*'*q, maxlen=q)

        if(len(root.children) == 0):
            self.append(itertools.chain(ancestors, siblings))
        else:
            for child in root.children:
                siblings.append(child.label)
                self.append(itertools.chain(ancestors, siblings))
                self.gram_list(child, p, q, copy.copy(ancestors))
            for i in range(q-1):
                siblings.append("*")
                self.append(itertools.chain(ancestors, siblings))

    def distance(self, other):
    	union = len(self) + len(other)
        return 1.0 - 2.0*(self._intersection(other)/union)

    def _intersection(self, other):
    	intersect = 0.0
        i = j = 0
        maxi = len(self)
        maxj = len(other)
        while i < maxi and j < maxj:
        	if self[i] == other[j]:
        		intersect += 1.0
                i += 1
                j += 1
            elif self[i] < other[j]:
                i += 1
            else:
                j += 1
        return intersect

    def sort(self):
    	self.list.sort(key=lambda x: ''.join(x))

    def append(self, value):
    	 self.list.append(tuple(value))

    def __len__(self):
        return len(self.list)

    def __repr__(self):
        return str(self.list)

    def __str__(self):
        return str(self.list)

    def __getitem__(self, key):
        return self.list[key]

    def __iter__(self):
        return iter(self.list)