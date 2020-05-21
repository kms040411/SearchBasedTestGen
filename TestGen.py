import astor
import ast
import sys
import copy

class Func_info():
    def __init__(self, name, args, pointer):
        self.name = name
        self.args = args
        self.pointer = pointer

class Predicate_info():
    def __init__(self, num, predicate, precedent):
        self.num = num
        self.predicate = predicate
        self.precedent = precedent

class TestGen():
    config = dict()
    functions = list() # A list of Func_info
    predicates = [None] # Do not use index 0
    original_ast = None
    precedent_stack = list()

    def __init__(self, depth=10):
        self.config['DEPTH'] = depth

    def do(self, name):
        self.file_input(name)
        self.modify_ast()
        self.file_output()
        self.execute_test_suite(0, [1, 2, 3])
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
        args = list()
        for i in range(arg_num):
            args.append(node.args.args[i].arg)
        self.functions.append(Func_info(name, args, pointer))
        return

    def register_predicate(self, node):
        predicate = node.test
        predicate_num = 0
        precedent = copy.deepcopy(self.precedent_stack)
        #print(precedent)
        if not isinstance(predicate, ast.Compare):
            print("it is not compare")
            raise Exception()
        else:
            predicate_num = len(self.predicates)
            self.predicates.append(Predicate_info(predicate_num, predicate, precedent))
            self.precedent_stack.append(predicate_num)
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
                self.precedent_stack.pop()
            elif isinstance(node, ast.While):
                print("while")
                predicate_num = self.register_predicate(node)
                self.add_helperfunc(predicate_num, node)
                iter_ast(node.body)
                iter_ast(node.orelse)
                self.precedent_stack.pop()
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
    def calc_fitness(self, predicate_num:int, args:list):
        pass
    
    # Generate & Execute test code
    def execute_test_suite(self, func_num:int, args:list):
        # Generate test code
        test_code = ""
        test_code = test_code + "import modified_code\n"
        test_code = test_code + "modified_code." + self.functions[func_num].name + "("
        for arg in args:
            test_code = test_code + str(arg) + ", "
        test_code = test_code + ")\n"

        # Execute test file
        compiled = compile(test_code, "test", "exec")
        exec(compiled)

        # Gather data from the test


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
