import unittest
from simple_di_container.container import Container

class ScopeTests(unittest.TestCase):
    
    def test_singleton_scope(self):
        """Test singleton scope behavior"""
        container = Container()
        
        # Register a simple class
        class TestClass:
            def __init__(self):
                self.id = 1
                
        container.register(TestClass)
        
        # Should return the same instance
        instance1 = container.resolve(TestClass)
        instance2 = container.resolve(TestClass)
        self.assertIs(instance1, instance2)
    
    def test_transient_scope(self):
        """Test transient scope behavior"""
        container = Container()
        
        # Register a simple class with transient scope
        class TestClass:
            def __init__(self):
                self.id = 1
                
        container.register(TestClass, scope="transient")
        
        # Should return different instances
        instance1 = container.resolve(TestClass)
        instance2 = container.resolve(TestClass)
        self.assertIsNot(instance1, instance2)
    
    def test_scoped_scope(self):
        """Test scoped scope behavior"""
        container = Container()
        
        # Register a simple class with scoped scope
        class TestClass:
            def __init__(self):
                self.id = 1
                
        container.register(TestClass, scope="scoped")
        
        # Create scope and resolve
        container.create_scope("test")
        instance1 = container.resolve(TestClass)
        instance2 = container.resolve(TestClass)
        
        # Should return same instance within same scope
        self.assertIs(instance1, instance2)
        
        # Create different scope
        container.create_scope("test2")
        instance3 = container.resolve(TestClass)
        
        # Should return different instance in different scope
        self.assertIsNot(instance1, instance3)

if __name__ == '__main__':
    unittest.main()