import function_test

def some_func():
    print 'This was printed from the main_test.'

if __name__ == '__main__':
    some_func()
    function_test.some_func()