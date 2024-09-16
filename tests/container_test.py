import unittest
from abc import ABC
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from simple_di_container.container import Container, CyclicDependencyError

class ContainerTest(unittest.TestCase):

    def test_class_registration(self):
        class AbstractClass:
            pass

        class ConcreteClass(AbstractClass):
            pass

        container = Container()
        container.register(ConcreteClass)

        actual : AbstractClass = container.resolve(AbstractClass)

        self.assertEqual(type(actual), ConcreteClass)

    def test_factory_registration(self):
        class AnotherClass():
            pass

        class MyClass:
            def __init__(self, dependency : AnotherClass):
                self.dependency = dependency

        def my_factory(container : Container):
            dependency = container.resolve(AnotherClass)
            return MyClass(dependency)

        container = Container()
        container.register(AnotherClass)
        container.register(MyClass, factory=my_factory)

        actual : MyClass = container.resolve(MyClass)

        self.assertTrue(isinstance(actual, MyClass))

    def test_instance_registration(self):
        class SomeClass:
            pass

        instance = SomeClass()
        container = Container()
        container.register(SomeClass, instance=instance)

        actual : SomeClass = container.resolve(SomeClass)

        self.assertEqual(actual, instance)

    def test_resolve_nested_dependencies(self):
        class DependencyA:
            pass

        class DependencyB:
            def __init__(self, dependency_a : DependencyA):
                self.dependency_a = dependency_a
        
        class DependencyC:
            def __init__(self, dependency_a : DependencyA) -> None:
                self.dependency_a = dependency_a

        class MyClass:
            def __init__(self, dependency_b : DependencyB):
                self.dependency_b = dependency_b

        def factory_c(container : Container):
            dependency_a = container.resolve(DependencyA)
            return DependencyC(dependency_a)

        container = Container()
        container.register(DependencyA)
        container.register(DependencyB)
        container.register(MyClass)
        container.register(DependencyC, factory=factory_c)

        obj : MyClass = container.resolve(MyClass)
        obj2 : DependencyC = container.resolve(DependencyC)

        self.assertTrue(isinstance(obj, MyClass))
        self.assertTrue(isinstance(obj.dependency_b, DependencyB))
        self.assertTrue(isinstance(obj.dependency_b.dependency_a, DependencyA))
        self.assertTrue(isinstance(obj2, DependencyC))
        self.assertTrue(isinstance(obj2.dependency_a, DependencyA))
        self.assertEqual(obj2.dependency_a, obj.dependency_b.dependency_a)

    def test_resolve_all_implementations(self):
        class MyInterface(ABC):
            pass

        class ImplementationOne(MyInterface):
            pass

        class ImplementationTwo(MyInterface):
            pass

        class ImplementationThree(MyInterface):
            pass

        class MyClass():
            pass

        container = Container()
        container.register(ImplementationOne)
        container.register(ImplementationTwo)
        container.register(MyClass)
        container.register(ImplementationThree)

        actual = container.resolve_all_implementations(MyInterface)
        
        self.assertTrue(len(actual), 3)

    def test_resolve_container(self):
        container = Container()

        actual = container.resolve(Container)

        self.assertEqual(actual, container)

    def test_validate_container(self):
        class DependencyA:
            pass

        class DependencyB:
            def __init__(self, dependency_a : DependencyA):
                pass
        
        class DependencyC:
            def __init__(self, dependency_a : DependencyA, dependency_b: DependencyB) -> None:
                pass

        class MyClass:
            def __init__(self, dependency_b : DependencyB, dependency_a: DependencyA, dependency_c: DependencyC):
                pass
        
        def factory_c(container : Container):
            dependency_a = container.resolve(DependencyA)
            dependency_b = container.resolve(DependencyB)
            return DependencyC(dependency_a, dependency_b)

        container = Container()
        container.register(DependencyA)
        container.register(DependencyB)
        container.register(MyClass)
        container.register(DependencyC, factory=factory_c)

        container.validate()
        self.assertTrue(True)

    def test_validate_container_when_cycle(self):
        from cycled_dependency.dependency_a import DependencyA
        from cycled_dependency.dependency_b import DependencyB
        from cycled_dependency.dependency_c import DependencyC

        class MyClass:
            def __init__(self, dependency_b : DependencyB, dependency_a: DependencyA, dependency_c: DependencyC):
                pass
        
        def factory_c(container : Container):
            dependency_a = container.resolve(DependencyA)
            dependency_b = container.resolve(DependencyB)
            return DependencyC(dependency_a, dependency_b)

        container = Container()
        container.register(DependencyA)
        container.register(DependencyB)
        container.register(MyClass)
        container.register(DependencyC, factory=factory_c)

        with self.assertRaises(CyclicDependencyError):
            container.validate()

if __name__ == '__main__':
    unittest.main()