# Simple container

## Description 
This simple DI container for Python provides a mechanism for resolving dependencies through a class constructor. It only supports one type of object lifetime - singleton.

Registration is possible in three options:
1) Only by class - then when resolving, all dependencies will be added to the constructor, which will also be resolved
2) By class and factory method/lambda - then during resolution an object will be created using this method. If a factory method or lambda takes 1 argument, it will be passed an instance of the DI container when called
3) By class and instance - then when resolving, the registered object will simply be returned

## Install

Install latest: `pip install https://github.com/AMEST/py_simple_container/archive/refs/heads/master.tar.gz`

## Builder methods

* `register` - Register class (and optional factory or instance) to container
* `resolve` - Get class instance from container and resolve dependencies (only for only class registration)
* `resolve_all_implementations` - Resolve all instances who implement this class or abstract class

## Usage

```python
from simple_di_container import Container

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

obj : MyClass = container.resolve(MyClass) # MyClass has dependency B. Inside Dependency B stored Dependency A
obj2 : DependencyC = container.resolve(DependencyC) # Dependency C has dependency A.
# Dependency A in Dependency B equals Dependency A in Dependency C. Because it's resolved inside container as singleton
```