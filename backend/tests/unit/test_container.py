import pytest
from src.infrastructure.di.container import Container, CircularDependencyError

class IServiceA:
    pass

class ServiceA(IServiceA):
    pass

class IServiceB:
    pass

class ServiceB(IServiceB):
    def __init__(self, a: IServiceA):
        self.a = a

class CircA:
    def __init__(self, b: 'CircB'):
        self.b = b

class CircB:
    def __init__(self, a: CircA):
        self.a = a

def test_container_singleton_registration():
    container = Container()
    container.register_singleton(IServiceA, ServiceA)
    
    instance1 = container.resolve(IServiceA)
    instance2 = container.resolve(IServiceA)
    
    assert isinstance(instance1, ServiceA)
    assert instance1 is instance2

def test_container_transient_registration():
    container = Container()
    container.register_transient(IServiceA, ServiceA)
    
    instance1 = container.resolve(IServiceA)
    instance2 = container.resolve(IServiceA)
    
    assert isinstance(instance1, ServiceA)
    assert instance1 is not instance2

def test_container_dependency_resolution():
    container = Container()
    container.register_singleton(IServiceA, ServiceA)
    container.register_singleton(IServiceB, ServiceB)
    
    b = container.resolve(IServiceB)
    assert isinstance(b, ServiceB)
    assert isinstance(b.a, ServiceA)

def test_container_circular_dependency():
    container = Container()
    container.register_singleton(CircA, CircA)
    container.register_singleton(CircB, CircB)
    
    with pytest.raises(CircularDependencyError):
        container.resolve(CircA)

def test_container_instance_registration():
    container = Container()
    a = ServiceA()
    container.register_singleton(IServiceA, a)
    
    resolved = container.resolve(IServiceA)
    assert resolved is a

def test_container_factory_registration():
    container = Container()
    
    def factory(c: Container) -> ServiceA:
        return ServiceA()
        
    container.register_factory(IServiceA, factory)
    
    a1 = container.resolve(IServiceA)
    a2 = container.resolve(IServiceA)
    
    assert isinstance(a1, ServiceA)
    assert a1 is a2 # singleton by default
