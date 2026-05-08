class Class1:
 def hello_world(self):
    print("Hello, World!")

class Class2:
    def __init__(self):
        self.class1 = Class1()
    
    def call_hello_world(self):
        self.class1.hello_world()

new_class = Class2()
new_class.call_hello_world()