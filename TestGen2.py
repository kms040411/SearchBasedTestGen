import astor
import ast
import sys
import copy

class Func_info():
    def __init__(self, name, args):
        self.name = name
        self.args = args
        self.predicates = [None] # Do not use index 0

class Predicate_info():
    def __init__(self, num, predicate, precedent, op):
        self.num = num
        self.predicate = predicate
        self.op = op
        self.precedent = precedent

class Answer_info():
    def __init__(self, func_num, arg, target_predicate, predicate_option):
        self.func_num = func_num
        self.arg = arg
        self.target_predicate = target_predicate
        self.predicate_option = predicate_option

class TestGen():
    config = dict()
    functions = list() # A list of Func_info
    file_ast = None
    precedent_stack = list()
    constant_stack = list()
    constant_num_stack = list()
    answers = list()

    def __init__(self, K = 1, DEPTH = 100):
        self.config["K"] = K
        self.config["DEPTH"] = DEPTH
        return
    
    def do(self, name):
        self.file_input(name)
        self.init_log_file()
        self.modify_ast()
        self.file_output()
        self.gen_test_suite_()
        print("end of the program")
        return
    
    def gen_test_suite_(self):
        f = open("search_result.txt", "w")
        for i in range(self.current_func + 1):
            f.write("Test cases for function (" + str(i) + ")\n")
            print("Test cases for function (" + str(i) + ")")
            self.gen_test_suite(i, f)
            f.write("\n")
            print("")
        f.close()
        return

    # Read the file
    def file_input(self, name):
        self.file_ast = astor.parse_file(name)
        return

    def file_output(self):
        f = open("modified_code.py", "w")
        f.write(astor.to_source(self.file_ast))
        f.close()
        return

    def init_log_file(self):
        f = open(".execution_log", "w")
        f.write("")
        f.close()
        return

    def register_function(self, node):
        name = node.name
        arg_num = len(node.args.args)
        args = list()
        for i in range(arg_num):
            args.append(node.args.args[i].arg)
        self.functions.append(Func_info(name, args))
        return

    def register_predicate(self, node):
        predicate = None
        if not isinstance(node, ast.For):
            predicate = node.test
        else:
            predicate = ast.Compare(left=node.target, ops=[ast.LtE], right=node.iter)
        predicate_num = len(self.functions[self.current_func].predicates)
        precedent = copy.deepcopy(self.precedent_stack)
        op = predicate.ops[0]
        self.functions[self.current_func].predicates.append(Predicate_info(predicate_num, predicate, precedent, op))
        self.precedent_stack.append(predicate_num)
        return predicate_num
        

    def add_helperfunc(self, num, node):
        args_char = list()
        args_char = args_char + self.functions[self.current_func].args
        args_char = args_char + self.constant_stack

        args0 = [ast.Constant(value=num, kind=None), ast.Constant(value=0, kind=None)]
        args1 = [ast.Constant(value=num, kind=None), ast.Constant(value=1, kind=None)]
        char_list = list()
        for item in args_char:
            char_list.append(item)
        args0.append(ast.parse(str(char_list), mode='eval'))
        args1.append(ast.parse(str(char_list), mode='eval'))
        for item in args_char:
            args0.append(ast.Name(id = item))
            args1.append(ast.Name(id = item))
            
        node.body.insert(0, ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id=sys.argv[0][:-3]), attr='check_branch'),
                            args=args0,
                            keywords=[])))
        node.orelse.insert(0, ast.Expr(value=ast.Call(func=ast.Attribute(value=ast.Name(id=sys.argv[0][:-3]), attr='check_branch'),
                            args=args1,
                            keywords=[])))
        return

    # Read the ast, analyze predicates, add helper functions to ast
    def modify_ast(self):
        self.current_func = -1
        def iter_ast(node):
            if isinstance(node, list):
                self.constant_num_stack.append(0)
                for item in node:
                    iter_ast(item)
                num = self.constant_num_stack.pop()
                for i in range(num):
                    self.constant_stack.pop()
            elif isinstance(node, ast.FunctionDef):
                self.current_func = self.current_func + 1
                self.register_function(node)
                iter_ast(node.body)
            elif isinstance(node, ast.If):
                predicate_num = self.register_predicate(node)
                self.add_helperfunc(predicate_num, node)
                iter_ast(node.body)
                iter_ast(node.orelse)
                self.precedent_stack.pop()
            elif isinstance(node, ast.While):
                predicate_num = self.register_predicate(node)
                self.add_helperfunc(predicate_num, node)
                iter_ast(node.body)
                iter_ast(node.orelse)
                self.precedent_stack.pop()
            elif isinstance(node, ast.For):
                #predicate_num = self.register_predicate(node)
                #self.add_helperfunc(predicate_num, node)
                iter_ast(node.body)
                iter_ast(node.orelse)
                #self.precedent_stack.pop()
            elif isinstance(node, ast.Assign):
                target = node.targets[0].id
                self.constant_stack.append(target)
                self.constant_num_stack.append(self.constant_num_stack.pop() + 1)
            elif isinstance(node, ast.AST):
                if hasattr(node, "body"):
                    iter_ast(node.body)
                return
            return
        self.file_ast.body.insert(0, ast.Import(names=[ast.alias(name=sys.argv[0][:-3], asname=None)]))
        iter_ast(self.file_ast)
        return

    def register_answer(self, func_num:int, target_predicate:int, predicate_option:int, arg:dict):
        ans = Answer_info(func_num, arg, target_predicate, predicate_option)
        self.answers.append(ans)

    def get_answer(self, func_num:int, target_predicate:int):
        precedent = self.functions[func_num].predicates[target_predicate].precedent
        if len(precedent) == 0:
            return self.init_generate(func_num)
        else:
            answer = self.answers[(precedent[-1] - 1) * 2]
            if answer.arg is None:
                return None
            return answer.arg

    # Write test code
    def gen_test_suite(self, func_num:int, f):
        function = self.functions[func_num]
        predicate = function.predicates
        for i in range(1, len(function.predicates)):
            target_predicate = i
            init_arg = self.get_answer(func_num, target_predicate)
            arg = init_arg
            if arg is not None:
                arg = self.avm_generate(func_num, target_predicate, 1, arg)
            if arg is None:
                f.write(str(i) + "T : -\n")
                print(str(i) + "T : -")
            else:
                f.write(str(i) + "T : " + str(arg) + "\n")
                print(str(i) + "T : " + str(arg))
            self.register_answer(func_num, target_predicate, 1, arg)

            arg = init_arg
            if arg is not None:
                arg = self.avm_generate(func_num, target_predicate, 0, arg)
            if arg is None:
                f.write(str(i) + "F : -\n")
                print(str(i) + "F : -")
            else:
                f.write(str(i) + "F : " + str(arg) + "\n")
                print(str(i) + "F : " + str(arg))
            self.register_answer(func_num, target_predicate, 0, arg)

    def get_current_predicate(self, func_num:int, args:dict, target_predicate:int):
        predicates = self.execute_test_suite(func_num, args)
        target_precedent = self.functions[func_num].predicates[target_predicate].precedent
        target_precedent.append(target_predicate)
        current_predicate = 1
        for precedent in target_precedent:
            if precedent in predicates:
                current_predicate = precedent
        target_precedent.pop()
        return current_predicate

    # Generate 0 args
    def init_generate(self, func_num:int):
        arg_number = len(self.functions[func_num].args)
        arg_list = dict()
        for i in range(arg_number):
            arg_list[self.functions[func_num].args[i]] = 0
        return arg_list

    def check_fitness(self, op, fitness, target_predicate_num, target_predicate_option, current_predicate_num):
        if target_predicate_option != 0:
            if isinstance(op, ast.Gt) or isinstance(op, ast.Lt):
                if fitness < 0 and current_predicate_num == target_predicate_num:
                    return True
            elif isinstance(op, ast.GtE) or isinstance(op, ast.LtE):
                if fitness <= 0 and current_predicate_num == target_predicate_num:
                    return True
            elif isinstance(op, ast.Eq):
                if fitness == 0 and current_predicate_num == target_predicate_num:
                    return True
            else:
                raise Exception()
        else:
            if isinstance(op, ast.Gt) or isinstance(op, ast.Lt):
                if fitness > 0 and current_predicate_num == target_predicate_num:
                    return True
            elif isinstance(op, ast.GtE) or isinstance(op, ast.LtE):
                if fitness >= 0 and current_predicate_num == target_predicate_num:
                    return True
            elif isinstance(op, ast.Eq):
                if fitness != 0 and current_predicate_num == target_predicate_num:
                    return True
            else:
                raise Exception()
        return False

    # Run AVM to find args
    def avm_generate(self, func_num:int, target_predicate_num:int, target_predicate_option:int, init_arg:dict):
        arg_number = len(self.functions[func_num].args)
        arg_flag = 0 # 0 ~ (arg_number - 1)
        arg = copy.deepcopy(init_arg)

        fitness, current_predicate_num = self.calc_fitness(func_num, target_predicate_num, arg)
        op = self.functions[func_num].predicates[current_predicate_num].op
        if isinstance(op, ast.NotEq):
            op = ast.Eq()
            target_predicate_option = not target_predicate_option
        if self.check_fitness(op, fitness, target_predicate_num, target_predicate_option, current_predicate_num):
            return arg
        
        probe = 1
        for i in range(self.config["DEPTH"] * arg_number):
            # exploratory move
            arg_letter = self.functions[func_num].args[arg_flag]
            target_arg = arg[arg_letter]
            # case 1 : +
            if i > 10 * arg_number:
                probe = (probe + int(probe / 10) + 1)
            arg[arg_letter] = target_arg + probe
            fitness_1, temp = self.calc_fitness(func_num, target_predicate_num, arg)
            # case 2 : -
            arg[arg_letter] = target_arg - probe
            fitness_2, temp = self.calc_fitness(func_num, target_predicate_num, arg)

            # pattern move
            arg[arg_letter] = target_arg
            delta = 1
            fitness = 0
            old_fitness = 0
            current_predicate_num = 1
            if target_predicate_option != 0:
                if fitness_1 < fitness_2 :
                    # +, use fitness_1
                    fitness = fitness_1
                    old_fitness = fitness_1
                    for i in range(self.config["DEPTH"]):
                        arg[arg_letter] = arg[arg_letter] + delta
                        old_fitness = fitness
                        fitness, current_predicate_num = self.calc_fitness(func_num, target_predicate_num, arg)
                        if fitness > old_fitness:
                            arg[arg_letter] = arg[arg_letter] - delta
                            break
                        if self.check_fitness(op, old_fitness, target_predicate_num, target_predicate_option, current_predicate_num) \
                            and self.check_fitness(op, fitness, target_predicate_num, target_predicate_option, current_predicate_num):
                            break
                        delta = delta * 2
                elif fitness_1 > fitness_2:
                    # -, use fitness_2
                    fitness = fitness_2
                    old_fitness = fitness_2
                    for i in range(self.config["DEPTH"]):
                        arg[arg_letter] = arg[arg_letter] - delta
                        old_fitness = fitness
                        fitness, current_predicate_num = self.calc_fitness(func_num, target_predicate_num, arg)
                        if fitness > old_fitness:
                            arg[arg_letter] = arg[arg_letter] + delta
                            break
                        if self.check_fitness(op, old_fitness, target_predicate_num, target_predicate_option, current_predicate_num) \
                            and self.check_fitness(op, fitness, target_predicate_num, target_predicate_option, current_predicate_num):
                            break
                        delta = delta * 2
                else:
                    old_fitness = fitness_1
                op = self.functions[func_num].predicates[current_predicate_num].op
                if isinstance(op, ast.NotEq):
                    op = ast.Eq()
                if self.check_fitness(op, old_fitness, target_predicate_num, target_predicate_option, current_predicate_num):
                    return arg
            else:
                if fitness_1 < fitness_2:
                    fitness = fitness_2
                    old_fitness = fitness_2
                    for i in range(self.config["DEPTH"]):
                        arg[arg_letter] = arg[arg_letter] - delta
                        old_fitness = fitness
                        fitness, current_predicate_num = self.calc_fitness(func_num, target_predicate_num, arg)
                        if fitness < old_fitness:
                            arg[arg_letter] = arg[arg_letter] + delta
                            break
                        if self.check_fitness(op, old_fitness, target_predicate_num, target_predicate_option, current_predicate_num) \
                            and self.check_fitness(op, fitness, target_predicate_num, target_predicate_option, current_predicate_num):
                            break
                        delta = delta * 2
                elif fitness_1 > fitness_2:
                    fitness = fitness_1
                    old_fitness = fitness_1
                    for i in range(self.config["DEPTH"]):
                        arg[arg_letter] = arg[arg_letter] + delta
                        old_fitness = fitness
                        fitness, current_predicate_num = self.calc_fitness(func_num, target_predicate_num, arg)
                        if fitness < old_fitness:
                            arg[arg_letter] = arg[arg_letter] - delta
                            break
                        if self.check_fitness(op, old_fitness, target_predicate_num, target_predicate_option, current_predicate_num) \
                            and self.check_fitness(op, fitness, target_predicate_num, target_predicate_option, current_predicate_num):
                            break
                        delta = delta * 2
                else:
                    old_fitness = fitness_1
                    if target_arg == 0:
                        arg[arg_letter] = arg[arg_letter] + 1
                        old_fitness, current_predicate_num = self.calc_fitness(func_num, target_predicate_num, arg)
                op = self.functions[func_num].predicates[current_predicate_num].op
                if isinstance(op, ast.NotEq):
                    op = ast.Eq()
                if self.check_fitness(op, old_fitness, target_predicate_num, target_predicate_option, current_predicate_num):
                    return arg
            arg_flag = (arg_flag + 1) % arg_number
        # Cannot find answer
        return None

    # Return calculated fitness value
    def calc_fitness(self, func_num:int, target_predicate_num:int, args:dict):
        def get_args_from_file(current_predicate_num:int):
            f = open(".execution_log", "r")
            lines = f.readlines()
            predicates = list()
            for line in lines:
                split_line = line.split('/')
                predicate_num = int(split_line[0])
                if predicate_num == current_predicate_num:
                    f.close()
                    return ast.literal_eval(split_line[2].strip())
            f.close()
            return dict()

        predicate_num = self.get_current_predicate(func_num, args, target_predicate_num)
        predicate = self.functions[func_num].predicates[predicate_num].predicate
        args = get_args_from_file(predicate_num)

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
            right_code = right_code.replace(key, str(args[key]))

        left_eval = int(eval(left_code))
        right_eval = int(eval(right_code))
        approach_level = len(self.functions[func_num].predicates[target_predicate_num].precedent) - len(self.functions[func_num].predicates[predicate_num].precedent)

        branch_distance = 0
        K = self.config["K"]
        if isinstance(op, ast.Gt):
            branch_distance = right_eval - left_eval + K
        elif isinstance(op, ast.Lt):
            branch_distance = left_eval - right_eval + K
        elif isinstance(op, ast.Eq):
            branch_distance = abs(left_eval - right_eval)
        elif isinstance(op, ast.GtE):
            branch_distance = right_eval - left_eval + K
        elif isinstance(op, ast.LtE):
            branch_distance = left_eval - right_eval + K
        elif isinstance(op, ast.NotEq):
            branch_distance = abs(left_eval - right_eval)
        normalized = 0
        if branch_distance + 1 != 0:
            normalized = branch_distance / abs(branch_distance + 1)
        f = normalized + approach_level
        return f, predicate_num

    # Generate & Execute test code
    def execute_test_suite(self, func_num:int, args:dict):
        # Generate test code
        test_code = ""
        test_code = test_code + "import modified_code\n"
        test_code = test_code + "modified_code." + self.functions[func_num].name + "("
        for arg in self.functions[func_num].args:
            test_code = test_code + str(int(args[arg])) + ", "
        test_code = test_code + ")\n"

        self.init_log_file()

        # Execute test file
        exec(compile(test_code, "test", "exec"))

        # Gather data from the test
        f = open(".execution_log", "r")
        lines = f.readlines()
        predicates = list()
        for line in lines:
            split_line = line.split("/")
            predicate_num = int(split_line[0])
            predicates.append(predicate_num)
            option = int(split_line[1])
        return predicates

    # Print help information
    def help_function(self, program_name):
        print(str(program_name) + ": Search Based Test Data Generation")
        print("Usage: " + str(program_name) + " [Target program] [Depth=100]")
        pass

# This is a helper function added to the original code
# if : 1
# else : 0
# elif : 2 ~
def check_branch(predicate_num, option, char_list, *args):
    arg_dict = dict()
    for i in range(len(char_list)):
        arg_dict[char_list[i]] = args[i]

    f = open(".execution_log", "a")
    f.write(str(predicate_num) + "/" + str(option) + "/" + str(arg_dict))
    f.write("\n")
    f.close()
    return

if __name__ == "__main__":
    if len(sys.argv) == 1:
        testgen = TestGen()
        testgen.help_function(sys.argv[0])
        exit(0)
    else:
        depth = 100
        if len(sys.argv) == 3:
            depth = int(sys.argv[2])
        testgen = TestGen(DEPTH = depth)
        testgen.do(sys.argv[1])