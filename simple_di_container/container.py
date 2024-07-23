import inspect

class Container(object):
    """ Simple DI Container. Not thread safe. Singleton only lifetime """
    def __init__(self):
        self.registry = {}
        self.registry[Container] = self

    def register(self, cls, factory=None, instance=None) -> None:
        """
            Register object in container.
            Class Required!
            Registrations: 
                * Only by class  (when resolving class has been created and all dependencies resolved and injected to constructor)
                * By class and factory method or lambda ( resolved by class and execute method for create instance. IF method or lambda has one argument, it will be executed with passing Container instance for resolve another classes)
                * By class and instance. When resolving, return registered object
        """
        if factory is None and instance is None:
            self.registry[cls] = cls
        elif factory is not None and instance is not None:
            raise ValueError("Only one of factory or instance should be provided.")
        else:
            self.registry[cls] = factory or instance

    def resolve(self, cls) -> object:
        """
            Resolve object by class from container and inject dependencies (if exists and registered only by class) into constructor

            If resolving Base or Abstract class, resolved last registered object who implements this base or abstract class
        """
        if cls in self.registry:
            obj = self.registry[cls]
            if callable(obj):
                instance = None
                if inspect.isfunction(obj):
                    instance = obj(self) if len(inspect.signature(obj).parameters) == 1 else obj()
                else:
                    dependencies = self._resolve_dependencies(obj)
                    instance = obj(*dependencies)
                self.registry[cls] = instance
                return instance
            return obj
        for registered_cls in reversed(self.registry):
            if issubclass(registered_cls, cls):
                return self.resolve(registered_cls)
        raise ValueError(f"No registration found for {cls}.")

    def resolve_all_implementations(self, cls) -> list[object]:
        """
            Resolve all implementations of base or abstract classes
        """
        result = []
        for registered_cls in self.registry: 
            if issubclass(registered_cls, cls):
                result.append(self.resolve(registered_cls))
        return result
            
    def _resolve_dependencies(self, func):
        parameters = inspect.signature(func).parameters
        dependencies = []
        for param in parameters.values():
            if param.annotation != inspect.Parameter.empty:
                dependencies.append(self.resolve(param.annotation))
            else:
                raise ValueError(f"Cannot resolve dependency for parameter {param}.")
        return dependencies
