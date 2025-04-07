
class Node(object):

	def __init__(self, label):
		self.label = label
        self.children = list()

    def addkid(self, node, before=False):
    	if before:  
    		self.children.insert(0, node)
        else:   
        	self.children.append(node)
        return self

    def split_tree(root, delimiter=""):
    	if(delimiter == ''):
        	sub_labels = [x for x in root.label]
        else:
        	sub_labels = root.label.rsplit(delimiter)
        if len(sub_labels) > 1: 
        	new_root = Node("*")
        	for label in sub_labels:
            	new_root.children.append(Node(label))
        	heir = new_root.children[0]
    	else: 
    		new_root = Node(root.label)
        	heir = new_root
    	for child in root.children:
        	heir.children.extend(split_node(child, delimiter))
    	return new_root

    def split_node(node, delimiter):
    	if(delimiter == ''):
    		sub_labels = [x for x in node.label]
    	else:
    		sub_labels = node.label.rsplit(delimiter)
    	sub_nodes = list()
    	for label in sub_labels:
        	sub_nodes.append(Node(label))
    	if len(sub_nodes) > 0:
        	for child in node.children:
            	sub_nodes[0].children.extend(split_node(child, delimiter))
    	return sub_nodes