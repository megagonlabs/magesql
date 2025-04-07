
import random, itertools

from pqnode import Node
from pggram import Gram


def checkGramEquality(pqgram1, pqgram2):
    if len(pqgram1) != len(pqgram2) or len(pqgram1[0]) != len(pqgram2[0]):
    	return False
    for gram1 in pqgram1:
        contains = False
        for gram2 in pqgram2:
            if gram1 == gram2:
                contains = True
                break
        if contains == False:
            return False
    return True

def randtree(depth=2, alpha='abcdefghijklmnopqrstuvwxyz', repeat=2, width=2):
    labels = [''.join(x) for x in itertools.product(alpha, repeat=repeat)]
    random.shuffle(labels)
    labels = (x for x in labels)
    root = Node("root")
    p = [root]
    c = list()
    for x in range(depth-1):
        for y in p:
            for z in range(random.randint(1,1+width)):
                n = tree.Node(next(labels))
                y.addkid(n)
                c.append(n)
        p = c
        c = list()
    return root

def test_init_two_tree():
        p = 2
        q = 3
        num_random = 10
        trees = list()
        pgrams = list()

        small_tree1 = Node("a")
        small_tree2 = Node("b")
        trees.append(small_tree1)
        trees.append(small_tree2)

        small_grams1 = [('*','a','*','*','*')]
        small_grams2 = [('*','b','*','*','*')]
        pgrams.append(small_grams1)
        pgrams.append(small_grams2)

        known_tree1 =  (Node("a").addkid(tree.Node("a")
                                 .addkid(tree.Node("e"))
                                 .addkid(tree.Node("b")))
                                 .addkid(tree.Node("b"))
                                 .addkid(tree.Node("c")))

        known_tree2 =  (Node("a").addkid(tree.Node("a")
                                 .addkid(tree.Node("e"))
                                 .addkid(tree.Node("b")))
                                 .addkid(tree.Node("b"))
                                 .addkid(tree.Node("x")))

        trees.append(known_tree1)
        trees.append(known_tree2)

        known_grams1 = [('*','a','*','*','a'),('a','a','*','*','e'),('a','e','*','*','*'),('a','a','*','e','b'),
                               ('a','b','*','*','*'),('a','a','e','b','*'),('a','a','b','*','*'),('*','a','*','a','b'),
                               ('a','b','*','*','*'),('*','a','a','b','c'),('a','c','*','*','*'),('*','a','b','c','*'),
                               ('*','a','c','*','*')]
        known_grams2 = [('*','a','*','*','a'),('a','a','*','*','e'),('a','e','*','*','*'),('a','a','*','e','b'),
                               ('a','b','*','*','*'),('a','a','e','b','*'),('a','a','b','*','*'),('*','a','*','a','b'),
                               ('a','b','*','*','*'),('*','a','a','b','x'),('a','x','*','*','*'),('*','a','b','x','*'),
                               ('*','a','x','*','*')]


        for i in range(0, num_random):
            depth = random.randint(1, 10)
            width = random.randint(1, 5)
            trees.append(randtree(depth=depth, width=width, repeat=4))

        for tree1 in trees:
            pggrams.append(Gram(tree1, p, q))
    return trees, pggrams
