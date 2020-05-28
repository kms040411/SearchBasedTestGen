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

    def __init__(self, K = 1):
        self.config["K"] = K
        return

    def do(self, name):
        self.file_input(name)
        self.init_log_file()
        self.modify_ast()
        self.file_output()
        self.execute_test_suite(0, [1, 2, 3])
        #self.calc_fitness(4, 4, {"x" : 3, "y" : 15, "z" : 17})
        self.gen_test_suite()
        return

    # Print help information
    def help_function(self):
        pass
    
    # Read the file, return ast
    def file_input(self, name):
        self.original_ast = astor.parse_file(name)
        return

    def init_log_file(self):
        f = open(".execution_log", "w")
        f.write("")
        f.close()
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
        node.body.insert(0, ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id=sys.argv[0][:-3]), attr='check_branch'),
                            args=[ast.Constant(value=num, kind=None), ast.Constant(value=1, kind=None)],
                            keywords=[])))
        node.orelse.insert(0, ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id=sys.argv[0][:-3]), attr='check_branch'),
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
        self.original_ast.body.insert(0, ast.Import(names=[ast.alias(name=sys.argv[0][:-3], asname=None)]))
        iter_ast(self.original_ast)
        return

    # Write test code
    def gen_test_suite(self):
        pass

    # Return calculated fitness value
    def calc_fitness(self, predicate_num:int, target_predicate_num:int, args:dict):
        predicate = self.predicates[predicate_num].predicate

        op = predicate.ops[0]
        left = predicate.left
        right = None
        if(hasattr(predicate, "right")):
            right = predicate.right
        elif(hasattr(predicate, "comparators")):
            right = predicate.comparators[0]
        else:
            raise Exception()
        
        left_code = astor.to_source(left).rstrip('\n')
        right_code = astor.to_source(right).rstrip('\n')

        for key in args:
            left_code = left_code.replace(key, str(args[key]))

        left_eval = eval(left_code)
        right_eval = eval(right_code)
        # @TODO : calculate approach_level, it could be wrong when we use elif
        approach_level = len(self.predicates[target_predicate_num].precedent) - len(self.predicates[predicate_num].precedent)
        
        branch_distance = 0
        K = self.config["K"]
        if isinstance(op, ast.Gt):
            branch_distance = right_eval - left_eval + K
        elif isinstance(op, ast.Lt):
            branch_distance = left_eval - right_eval + K
        elif isinstance(op, ast.Eq):
            branch_distance = abs(left_eval - right_eval)
        normalized = 1 - pow(1.001, -1 * branch_distance)
        f = normalized + approach_level

        print(f)
        return f
    
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
        exec(compile(test_code, "test", "exec"))

        # Gather data from the test
        f = open(".execution_log", "r")
        lines = f.readlines()
        for line in lines:
            split_line = line.split(" ")
            predicate_num = int(split_line[0])
            option = int(split_line[1])
        branch_coverage = len(lines) / (len(self.predicates) - 1)
        #print("branch coverage : " + str(branch_coverage))



# This is a helper function added to the original code
# if : 1
# else : 0
# elif : 2 ~
def check_branch(predicate_num, option):
    print("num : " + str(predicate_num) + ", option : " + str(option))
    f = open(".execution_log", "a")
    f.write(str(predicate_num) + " " + str(option) + "\n")
    f.close()
    return

if __name__ == "__main__":
    testgen = TestGen()
    if len(sys.argv) == 1:
        testgen.helper_function()
        exit(0)
    else:
        testgen.do(sys.argv[1])
