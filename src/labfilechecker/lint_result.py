class LintResult:
    """An object to hold the results of a lint test"""

    def __init__(self, row,column, value, lint_test, message):
        self.row  = row
        self.column = column
        self.value = value
        self.lint_test = lint_test
        self.message = message

    def __iter__(self):
        yield 'row', self.row
        yield 'column', self.column
        yield 'value', self.value
        yield 'lint_test', self.lint_test
        yield 'message', self.message
    
    def __str__(self):
        return f"LintResult(row :{self.row}, column: {self.column}, value: {self.value}, test: {self.lint_test}, message: {self.message})"