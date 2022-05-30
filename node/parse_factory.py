from node.parse_node import *

class ParseNodeFactory():

    def get_parse_node(self, type:str):
        if type == "kleene":
            return ParseKleeneNode()
        elif type == "concat":
            return ParseConcatNode()
        elif type == "or":
            return ParseOrNode()
        elif type == "optional":
            return ParseOptionalNode()
        elif type == "symbol":
            return ParseSymbolNode()
        elif type == "sem_action":
            return ParseSemActionNode()
        elif type == "Attribute":
            return ParseAttributesNode()
        else:
            print(f"No {type} parse node.")