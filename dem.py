# los imports

from abc import ABC, abstractmethod, abstractproperty

# el clases

class entidad(ABC):

    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def habla(self, **kwargs):
        pass


class character(entidad):

    def __init__(self, name, faction, vitals, maxs, stats, modifiers, equips, inv, **kwargs):
        self.name = name # chars assigned name, may not be changed
        self.faction = faction # chars assigned faction, may be changed
        self.vitals = vitals # lista con el estado actual
        self.maxs = maxs # lista con la cantidad maxima para vitals
        self.stats = stats # dict con los stats // kwds = {'str', 'dex', 'chr', 'int'}
        self.modifiers = modifiers # dict con los modificadores actuales a los 
        # stats ej: buffs // kwds = {'str', 'dex', 'chr', 'int'}
        self.equips = equips # dict con los objetos que estan equipados, se 
        # guardan temporalmente aqui // kwds = {'head', 'hands', 'torso', 'feet', 
        # 'main-hand', 'off-hand', 'neck', 'ring1', 'ring2', 'earring1', 'earring2'}
        self.inv = inv # lista con el inventario del player, tiene un len max de 20
        # los **kwargs son en caso de que haya herencia

    def __str__(self):
        s = '{0} el {1}'.format(self.name, self.faction) # un string del estilo "nombre el faccion"
        # ej. "Hitler el Nazi"
        return s

    def habla(self, msg, **kwargs):
        raise NotImplementedError

# el main

if __name__ == '__main__':
    pass

