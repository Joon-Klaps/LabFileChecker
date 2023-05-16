class LintResult:
    """An object to hold the results of a lint test"""

    def __init__(self, row, value, lint_test, message):
        self.row  = row
        self.value = value
        self.lint_test = lint_test
        self.message = message

    def __iter__(self):
        yield 'row', self.row
        yield 'value', self.value
        yield 'lint_test', self.lint_test
        yield 'message', self.message