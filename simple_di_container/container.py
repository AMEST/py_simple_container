import inspect

class Container(object):
    """ Simple DI Container. Supports singleton, transient, and scoped lifetimes. Not thread safe. """
    def __init__(self):
        self.registry = {}
        self.scopes = {}
        self.current_scope = None
        self.registry[Container] = self

    def register(self, cls, factory=None, instance=None, scope="singleton"):
        """
            Register object in container.
            Class Required!
            Registrations: 
                * Only by class  (when resolving class has been created and all dependencies resolved and injected to constructor)
                * By class and factory method or lambda ( resolved by class and execute method for create instance. IF method or lambda has one argument, it will be executed with passing Container instance for resolve another classes)
                * By class and instance. When resolving, return registered object
            
            Scope options:
                - "singleton": One instance per container (current behavior)
                - "transient": New instance on every resolve
                - "scoped": One instance per scope context (requires scope activation)
        """
        if factory is None and instance is None:
            self.registry[cls] = {"type": "class", "value": cls, "scope": scope}
        elif factory is not None and instance is not None:
            raise ValueError("Only one of factory or instance should be provided.")
        else:
            self.registry[cls] = {"type": "factory" if factory is not None else "instance", "value": factory or instance, "scope": scope}

    def resolve(self, cls):
        """
            Resolve object by class from container and inject dependencies (if exists and registered only by class) into constructor

            If resolving Base or Abstract class, resolved last registered object who implements this base or abstract class
        """
        if cls in self.registry:
            registration = self.registry[cls]
            scope = registration["scope"]
            
            # Handle scoped instances
            if scope == "scoped":
                if self.current_scope is None:
                    # If we're trying to resolve a scoped instance outside of any scope, 
                    # we'll create a default scope named "default"
                    self.current_scope = "default"
                
                # Create a scope-specific registry if it doesn't exist
                if self.current_scope not in self.scopes:
                    self.scopes[self.current_scope] = {}
                
                # Return existing instance in this scope or create new one
                if cls in self.scopes[self.current_scope]:
                    return self.scopes[self.current_scope][cls]
                
                # Create new instance for this scope
                instance = self._create_instance(registration)
                self.scopes[self.current_scope][cls] = instance
                return instance
            
            elif scope == "transient":
                # Always create a new instance
                return self._create_instance(registration)
            
            else:  # singleton
                # Check if instance already exists
                if cls in self.registry and isinstance(self.registry[cls], dict) and "instance" in self.registry[cls]:
                    return self.registry[cls]["instance"]
                
                # Create and store singleton instance
                instance = self._create_instance(registration)
                # Store the instance in the registry for singleton
                self.registry[cls] = {"type": registration["type"], "value": registration["value"], "scope": registration["scope"], "instance": instance}
                return instance
                
        # Try to resolve base class implementations
        for registered_cls in reversed(self.registry):
            if issubclass(registered_cls, cls):
                return self.resolve(registered_cls)
        raise ValueError("No registration found for %s." % cls)

    def _create_instance(self, registration):
        """Helper method to create instance based on registration type"""
        obj = registration["value"]
        if registration["type"] == "class":
            dependencies = self._resolve_dependencies(obj)
            return obj(*dependencies)
        elif registration["type"] == "factory":
            if callable(obj):
                try:
                    # Try to call with container if it expects one argument
                    sig = inspect.signature(obj)
                    if len(sig.parameters) == 1:
                        return obj(self)
                    else:
                        return obj()
                except:
                    # Fallback if signature inspection fails
                    return obj()
            else:
                dependencies = self._resolve_dependencies(obj)
                return obj(*dependencies)
        else:  # instance
            return obj

    def create_scope(self, scope_name):
        """Create a new scope context for scoped dependencies"""
        self.current_scope = scope_name
        if scope_name not in self.scopes:
            self.scopes[scope_name] = {}
        return self

    def destroy_scope(self, scope_name):
        """Destroy a scope and its associated instances"""
        if scope_name in self.scopes:
            del self.scopes[scope_name]
        if self.current_scope == scope_name:
            self.current_scope = None

    def _resolve_dependencies(self, func):
        # Just a simplified version that works with Python 3 and 2.7
        # We'll handle parameters by inspection but use a fallback
        try:
            sig = inspect.signature(func)
            dependencies = []
            for param_name, param in sig.parameters.items():
                if param.annotation != inspect.Parameter.empty:
                    dependencies.append(self.resolve(param.annotation))
                else:
                    # Try to resolve based on parameter name as fallback
                    try:
                        dependencies.append(self.resolve(param.annotation))
                    except:
                        raise ValueError("Cannot resolve dependency for parameter %s." % param_name)
            return dependencies
        except:
            # Fallback for when signature cannot be inspected (e.g., built-in functions)
            return []

    def resolve_all_implementations(self, cls) -> list[object]:
        """
            Resolve all implementations of base or abstract classes
        """
        result = []
        for registered_cls in self.registry: 
            if issubclass(registered_cls, cls):
                result.append(self.resolve(registered_cls))
        return result
            
    def _create_instance(self, registration):
        """Helper method to create instance based on registration type"""
        obj = registration["value"]
        if registration["type"] == "class":
            dependencies = self._resolve_dependencies(obj)
            return obj(*dependencies)
        elif registration["type"] == "factory":
            if inspect.isfunction(obj):
                return obj(self) if len(inspect.signature(obj).parameters) == 1 else obj()
            else:
                dependencies = self._resolve_dependencies(obj)
                return obj(*dependencies)
        else:  # instance
            return obj

    def create_scope(self, scope_name):
        """Create a new scope context for scoped dependencies"""
        self.current_scope = scope_name
        if scope_name not in self.scopes:
            self.scopes[scope_name] = {}
        return self

    def destroy_scope(self, scope_name):
        """Destroy a scope and its associated instances"""
        if scope_name in self.scopes:
            del self.scopes[scope_name]
        if self.current_scope == scope_name:
            self.current_scope = None

    def _resolve_dependencies(self, func):
        parameters = inspect.signature(func).parameters
        dependencies = []
        for param in parameters.values():
            if param.annotation != inspect.Parameter.empty:
                dependencies.append(self.resolve(param.annotation))
            else:
                raise ValueError(f"Cannot resolve dependency for parameter {param}.")
        return dependencies
