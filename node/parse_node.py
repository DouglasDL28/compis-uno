

class ParseNode():
    productions: dict[str, "ParseNode"] = {}
    parser_file = None

    def __init__(self, value=None, left=None, right=None) -> None:
        self.value = value
        self.left: ParseNode = left
        self.right: ParseNode = right

    def print_tree(self, node, level=0):
        if node != None:
            self.print_tree(node.left, level + 1)
            print(' ' * 4 * level + '-> ' + str(node))
            self.print_tree(node.right, level + 1)

    def nullable(self) -> bool:
        pass

    def firstpos(self) -> set:
        pass

    def indentation(self, lvl):
        self.parser_file.write(" "*4*lvl)

    def gen_code(self, root: "ParseNode", lvl=0):
        """ Generate node code """
        if root:
            if isinstance(root, ParseSymbolNode):
                if root.value in self.productions:
                    has_attr = True if root.left and isinstance(root.left, ParseAttributesNode) else False
                    if has_attr:
                        attr = root.left.value
                        val = f'{attr} = self.{root.value}({attr})'
                    else:
                        val = f"self.{root.value}()"
                        
                    self.indentation(lvl)
                    self.parser_file.write(val + '\n')
                else:
                    self.indentation(lvl)
                    self.parser_file.write(f'self.expect("{root.value}")\n')
                self.gen_code(root.left, lvl=lvl+1) # recur left child
                self.gen_code(root.right, lvl=lvl+1) # recur right child
            elif isinstance(root, ParseKleeneNode):
                self.indentation(lvl)
                first = ",".join(f'"{i}"' for i in root.firstpos())
                self.parser_file.write(f"while self.la.name in {{{first}}}:\n")
                self.gen_code(root.left, lvl=lvl+1) # recur left child
                self.gen_code(root.right, lvl=lvl+1) # recur right child
            elif isinstance(root, ParseOrNode):
                self.indentation(lvl)
                first = ",".join(f'"{i}"' for i in root.left.firstpos())
                self.parser_file.write(f"if self.la.name in {{{first}}}:\n")
                self.gen_code(root.left, lvl=lvl+1) # recur left child
                self.indentation(lvl)
                first = ",".join(f'"{i}"' for i in root.right.firstpos())
                self.parser_file.write(f"elif self.la.name in {{{first}}}:\n")
                self.gen_code(root.right, lvl=lvl+1) # recur right child
                self.indentation(lvl)
                self.parser_file.write(f"else: self.syn_error({root.left.firstpos().union(root.right.firstpos())})\n")
            elif isinstance(root, ParseSemActionNode):
                self.indentation(lvl)
                self.parser_file.write(root.value + "\n")
                self.gen_code(root.left, lvl=lvl+1) # recur left child
                self.gen_code(root.right, lvl=lvl+1) # recur right child
            elif isinstance(root, ParseOptionalNode):
                self.indentation(lvl)
                first = ",".join(f'"{i}"' for i in root.firstpos())
                self.parser_file.write(f"if self.la.name in {{{first}}}:\n")
                self.gen_code(root.left, lvl=lvl+1) # recur left child
                self.gen_code(root.right, lvl=lvl+1) # recur right child
            else:
                lvl = lvl-1
                self.gen_code(root.left, lvl=lvl+1) # recur left child
                self.gen_code(root.right, lvl=lvl+1) # recur right child

    def __str__(self) -> str:
        return f"{self.value}"

class ParseKleeneNode(ParseNode):
    """ {Expression} """
    def __init__(self, value=None, left=None, right=None) -> None:
        super().__init__(value, left, right)

    def nullable(self) -> bool:
        return True

    def firstpos(self) -> set:
        return self.left.firstpos()

class ParseConcatNode(ParseNode):
    """ (Expression) """
    def __init__(self, value=None, left=None, right=None) -> None:
        super().__init__(value, left, right)

    def nullable(self) -> bool:
        return self.left.nullable() and self.right.nullable()

    def firstpos(self) -> set:
        if self.left.nullable():
            return self.left.firstpos().union(self.right.firstpos())
        else:
            return self.left.firstpos()

class ParseOrNode(ParseNode):
    """ Term | Term """
    def __init__(self, value=None, left=None, right=None) -> None:
        super().__init__(value, left, right)

    def nullable(self) -> bool:
        return self.left.nullable() or self.right.nullable()

    def firstpos(self) -> set:
        return self.left.firstpos().union(self.right.firstpos())

class ParseOptionalNode(ParseNode):
    """ [Expression] """
    def __init__(self, value=None, left=None, right=None) -> None:
        super().__init__(value, left, right)

    def nullable(self):
        return True

    def firstpos(self):
        return self.left.firstpos()

class ParseSymbolNode(ParseNode):
    """ Symbol """
    def __init__(self, value=None, left=None, right=None) -> None:
        super().__init__(value, left, right)

    def nullable(self) -> bool:
        return False

    def firstpos(self) -> set:
        if self.value in self.productions:
            return self.productions[self.value].firstpos()
        else:
            return {str(self.value)}

class ParseSemActionNode(ParseNode):
    """ SemAction. """
    def __init__(self, value=None, left=None, right=None) -> None:
        super().__init__(value, left, right)

    def nullable(self) -> bool:
        return True

    def firstpos(self) -> set:
        return set()

    def __str__(self) -> str:
        return f"({self.value})"

class ParseAttributesNode(ParseNode):
    """ Attributes. """
    def __init__(self, value=None, rv=None, left=None, right=None) -> None:
        super().__init__(value, left, right)
        self.rv = rv

    def nullable(self) -> bool:
        return True

    def firstpos(self) -> set:
        return set()

    def __str__(self) -> str:
        return f"<{self.value}>"
