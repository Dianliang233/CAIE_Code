from .data import *
from ..AST_Base import *
from ..global_var import *
from .array import *

class Statements(AST_Node):
    def __init__(self, *args, **kwargs):
        self.type = 'STATEMENTS'
        self.statements = []
        super().__init__(*args, **kwargs)

    def add_statement(self, statement):
        self.statements.append(statement)

    def get_tree(self, level=0):
        result = []
        for statement in self.statements:
            result.append(str(statement.get_tree(level)))
        return '\n'.join(result)

    def exe(self):
        result = []
        for statement in self.statements:
            # 如果当前请求返回了，那就直接停止运行这个表达式块
            if stack.return_request:
                break
            # 尝试运行，如果失败，直接定制当前表达式块
            try:
                result.append(statement.exe())
            except Exception as e:
                add_error_message(str(e), self)
                break

        return result

class If(AST_Node):
    def __init__(self, condition, true_statement, false_statement=None, *args, **kwargs):
        self.type = 'IF'
        self.condition = condition
        self.true_statement = true_statement
        self.false_statement = false_statement
        super().__init__(*args, **kwargs)

    def get_tree(self, level=0):
        result = LEVEL_STR * level
        result += 'IF\n' + self.condition.get_tree(level+1)
        result += '\n' + self.true_statement.get_tree(level+1)
        result += ( '\n' + LEVEL_STR * level + 'ELSE\n' + self.false_statement.get_tree(level+1) ) if self.false_statement else ''

        return result

    def exe(self):
        if self.condition.exe()[0]:
            self.true_statement.exe()
        else:
            if self.false_statement:
                self.false_statement.exe()

class For(AST_Node):
    def __init__(self, id, left, right, step, body_statement, next_id, *args, **kwargs):
        self.type = 'FOR'
        self.id = id
        self.left = left
        self.right = right
        self.step = step
        self.body_statement = body_statement
        self.next_id = next_id
        super().__init__(*args, **kwargs)

    def get_tree(self, level=0):
        result = LEVEL_STR * level
        result += 'FOR ' + str(self.id)
        result += '\n' + self.left.get_tree(level+1) + '\n' + self.right.get_tree(level+1)
        result += '\n' + self.step.get_tree(level+1)
        result += '\n' + self.body_statement.get_tree(level+1)
        result += '\n' + LEVEL_STR * level + 'NEXT ' + str(self.next_id)

        return result

    def exe(self):
        left = self.left.exe()
        right = self.right.exe()
        step = self.step.exe()
        if left[1] == 'INTEGER' and right[1] == 'INTEGER' and step[1] == 'INTEGER':
            if step[0] < 0:
                diff = -1
            else:
                diff = 1

            # 创建 index 变量
            stack.new_variable(self.id, 'INTEGER')

            # 核对id是否相同
            if self.id != self.next_id:
                print(f'Expect `{self.id}` for next id, but found `{self.next_id}`')
                return

            for i in range(left[0], right[0]+diff, step[0]):
                # 给 index 赋值
                stack.set_variable(self.id, i, 'INTEGER')
                # 执行内部操作
                self.body_statement.exe()
        else:
            print(f'Expect `INTEGER` for index and step, but found `{left[1]}`, `{right[1]}` and `{step[1]}`')

class Case(AST_Node):
    def __init__(self, id, cases, *args, **kwargs):
        self.type = 'CASE'
        self.id = id
        self.cases = cases
        super().__init__(*args, **kwargs)

    def get_tree(self, level=0):
        return LEVEL_STR * level + self.type + ' ' + str(self.id) + '\n' + self.cases.get_tree(level+1)

    def exe(self):
        value = stack.get_variable(self.id)
        self.cases.exe(value)

class Case_array(AST_Node):
    def __init__(self, id, indexes, cases, *args, **kwargs):
        self.type = 'CASE_ARRAY'
        self.id = id
        self.indexes = indexes
        self.cases = cases
        super().__init__(*args, **kwargs)

    def get_tree(self, level=0):
        return LEVEL_STR * level + self.type + ' ' + str(self.id) + '\n' + self.indexes.get_tree(level+1) + '\n' + self.cases.get_tree(level+1)

    def exe(self):
        value = Array_get(self.id, self.indexes, lineno=self.lineno, lexpos=self.lexpos)
        self.cases.exe(value)

class Cases(AST_Node):
    def __init__(self, *args, **kwargs):
        self.type = 'CASES'
        self.cases = []
        self.otherwise = None
        super().__init__(*args, **kwargs)

    def get_tree(self, level=0):
        result = LEVEL_STR * level + self.type
        for i in self.cases:
            result += '\n' + i.get_tree(level+1)
        return result

    def add_case(self, case):
        if case.is_otherwise:
            self.otherwise = case
        else:
            self.cases.append(case)

    def exe(self, value):
        for case in self.cases:
            if case.check(value):
                case.exe()
                break
        else:
            if self.otherwise:
                self.otherwise.exe()

class A_case(AST_Node):
    def __init__(self, condition, true_statement, is_otherwise=False, *args, **kwargs):
        self.type = 'A_CASE'
        self.condition = condition
        self.true_statement = true_statement
        self.is_otherwise = is_otherwise
        super().__init__(*args, **kwargs)

    def get_tree(self, level=0):
        return LEVEL_STR * level + self.type + '\n' + self.condition.get_tree(level+1) + '\n' + self.true_statement.get_tree(level+1)

    def check(self, value):
        if self.condition.type == 'RANGE':
            r = set(self.condition.exe())
        else:
            r = {self.condition.exe()}

        return value in r

    def exe(self):
        self.true_statement.exe()

class Range(AST_Node):
    def __init__(self, start, end, *args, **kwargs):
        self.type = 'RANGE'
        self.start = start
        self.end = end
        super().__init__(*args, **kwargs)

    def get_tree(self, level=0):
        return LEVEL_STR * level + self.type + '\n' + self.start.get_tree(level+1) + '\n' + self.end.get_tree(level+1)

    def exe(self):
        n1 = self.start.exe()
        n2 = self.end.exe()
        if n1[1] == 'INTEGER' and n2[1] == 'INTEGER':
            l = []
            for i in range(n1[0], n2[0]+1):
                l.append((i, 'INTEGER'))
            return l
        else:
            add_error_message(f'Expect `INTEGER` for a range argument, but found `{n1[1]}` and `{n2[1]}`', self)

class Repeat(AST_Node):
    def __init__(self, true_statement, condition, *args, **kwargs):
        self.type = 'REPEAT'
        self.true_statement = true_statement
        self.condition = condition
        super().__init__(*args, **kwargs)

    def get_tree(self, level=0):
        return LEVEL_STR * level + self.type + '\n' + self.true_statement.get_tree(level+1) + '\n' + self.condition.get_tree(level+1)

    def exe(self):
        while 1:
            self.true_statement.exe()
            if self.condition.exe()[0]:
                break

class While(AST_Node):
    def __init__(self, condition, true_statement, *args, **kwargs):
        self.type = 'WHILE'
        self.condition = condition
        self.true_statement = true_statement
        super().__init__(*args, **kwargs)

    def get_tree(self, level=0):
        return LEVEL_STR * level + self.type + '\n' + self.condition.get_tree(level+1) + '\n' + self.true_statement.get_tree(level+1)

    def exe(self):
        while self.condition.exe()[0]:
            self.true_statement.exe()[0]
