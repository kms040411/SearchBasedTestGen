import astor
import ast
import sys

class Func_info():
    def __init__(self, name, arg_num, pointer):
        self.name = name
        self.arg_num = arg_num
        self.pointer = pointer

class TestGen():
    config = dict()
    functions = list() # A list of Func_info
    predicates = list()
    original_ast = None

    def __init__(self, depth=10):
        self.config['DEPTH'] = depth

    def do(self, name):
        self.file_input(name)
        self.modify_ast()
        self.file_output()
        self.gen_test_suite()
        return

    # Print help information
    def help_function(self):
        pass
    
    # Read the file, return ast
    def file_input(self, name):
        self.original_ast = astor.parse_file(name)
        return
    
    def file_output(self):
        f = open("modified_code.py", "w")
        f.write(astor.to_source(self.original_ast))
        f.close()
        return

    def register_function(self, node):
        name = node.name
        pointer = node
        arg_num = len(node.args.args)
        self.functions.append(Func_info(name, arg_num, pointer))
        return

    def register_predicate(self, node):
        predicate = node.test
        predicate_num = 0
        if not isinstance(predicate, ast.Compare):
            print("not compare")
        else:
            predicate_num = len(self.predicates) + 1
            self.predicates.append((predicate_num, predicate))
        return predicate_num

    def add_helperfunc(self, num, node):
        node.body.insert(0, ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id='TestGen'), attr='check_branch'),
                            args=[ast.Constant(value=num, kind=None), ast.Constant(value=1, kind=None)],
                            keywords=[])))
        node.orelse.insert(0, ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id='TestGen'), attr='check_branch'),
                            args=[ast.Constant(value=num, kind=None), ast.Constant(value=0, kind=None)],
                            keywords=[])))
        return

    # Read the ast, analyze predicates, add helper functions to ast
    def modify_ast(self):
        def iter_ast(node):
            if isinstance(node, list):
                print("list")
                for item in node:
                    iter_ast(item)
            elif isinstance(node, ast.FunctionDef):
                print("function_def")
                self.register_function(node)
                iter_ast(node.body)
            elif isinstance(node, ast.If):
                print("if")
                predicate_num = self.register_predicate(node)
                self.add_helperfunc(predicate_num, node)
                iter_ast(node.body)
                iter_ast(node.orelse)
            elif isinstance(node, ast.While):
                print("while")
                predicate_num = self.register_predicate(node)
                self.add_helperfunc(predicate_num, node)
                iter_ast(node.body)
                iter_ast(node.orelse)
            elif isinstance(node, ast.AST):
                print("root or normal node")
                if hasattr(node, "body"):
                    iter_ast(node.body)
                return
            return
        self.original_ast.body.insert(0, ast.Import(names=[ast.alias(name='TestGen', asname=None)]))
        iter_ast(self.original_ast)
        return

    # Write test code
    def gen_test_suite(self):
        pass

    # Return calculated fitness value
    def calc_fitness(self, pnum:int, args:list):
        pass
    
    # Execute test code
    def execute_test_suite(self):
        pass

# This is a helper function added to the original code
# if : 1
# else : 0
# elif : 2 ~
def check_branch(predicate_num, option):
    print("num : " + str(predicate_num) + ", option : " + str(option))
    return

if __name__ == "__main__":
    testgen = TestGen()
    if len(sys.argv) == 1:
        testgen.helper_function()
        exit(0)
    else:
        testgen.do(sys.argv[1])
