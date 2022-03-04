import math


class SkeletonTree:
    def __init__(self, is_leaf, left_cap=None, parent=None):
        """For internal use only.  Use from_sorted_list to create a new SkeletonTree."""

        self.left_cap = left_cap
        self.is_leaf = is_leaf
        self.parent = parent
        self.left = self.right = None
        self.is_empty = True

    @classmethod
    def from_sorted_list(cls, values, parent=None):
        """Creates a SkeletonTree to accept values in the provided list."""

        if len(values) <= 2:
            leaf = SkeletonTree(is_leaf=True, left_cap=values[0], parent=parent)
            leaf.left = leaf.right = None
            return leaf

        midpoint = math.floor((len(values) - 1) / 2)
        root = cls(is_leaf=False, left_cap=values[midpoint], parent=parent)
        root.left = cls.from_sorted_list(values[:midpoint + 1], parent=root)
        root.right = cls.from_sorted_list(values[midpoint + 1:], parent=root)
        return root

    @property
    def is_left_child(self):
        return self.parent is not None and self.parent.left is self

    @property
    def is_right_child(self):
        return self.parent is not None and self.parent.right is self

    def insert(self, v):
        self.is_empty = False
        if v <= self.left_cap:
            if self.is_leaf:
                self.left = v
            else:
                self.left.insert(v)
        else:
            if self.is_leaf:
                self.right = v
            else:
                self.right.insert(v)

    def find_predecessor(self):
        current = self
        while current.is_left_child:
            current = current.parent
        if current.is_right_child:
            left_max = current.parent.left.find_max()
            # left_max is None if the right subtree is currently empty
            return left_max if left_max is not None else current.parent.find_predecessor()
        else:  # current is the root
            return None

    def find_max(self):
        if self.is_empty:
            return None
        current = self
        while not current.is_leaf:
            current = current.right if not current.right.is_empty else current.left
        return current.right if current.right is not None else current.left

    def find_value_or_predecessor(self, v):
        current = self
        while not current.is_empty and not current.is_leaf:
            current = current.left if v <= current.left_cap else current.right
        if current.left == v or current.right == v:
            return v
        elif current.is_leaf and current.left is not None and current.left < v:
            return current.left
        else:
            return current.find_predecessor()


def test_skeleton_tree():
    numbers = sorted([1, 2, -1, 0, 100, 45, -20])
    tree = SkeletonTree.from_sorted_list(numbers)
    for i in range(-100, 101):
        assert tree.find_value_or_predecessor(i) is None
    tree.insert(1)
    assert tree.find_value_or_predecessor(1) == 1
    assert tree.find_value_or_predecessor(2) == 1
    assert tree.find_value_or_predecessor(0) is None
    tree.insert(-20)
    tree.insert(45)
    assert tree.find_value_or_predecessor(1) == 1
    assert tree.find_value_or_predecessor(2) == 1
    assert tree.find_value_or_predecessor(0) == -20
    assert tree.find_value_or_predecessor(-20) == -20
    assert tree.find_value_or_predecessor(-21) is None
    assert tree.find_value_or_predecessor(45) == 45
    assert tree.find_value_or_predecessor(46) == 45



if __name__ == '__main__':
    test_nums()

