from copy import deepcopy
from collections import defaultdict

from csbgnpy.pd.lo import *
from csbgnpy.pd.entity import *
from csbgnpy.pd.modulation import *
from csbgnpy.pd.ui import *
from csbgnpy.utils import get_object
from csbgnpy.pd.io.sbgntxt import *

class Network(object):
    def __init__(self, entities = None, processes = None, modulations = None, compartments = None, los = None):
        self.entities = entities if entities is not None else []
        self.processes = processes if processes is not None else []
        self.modulations = modulations if modulations is not None else []
        self.compartments = compartments if compartments is not None else []
        self.los = los if los is not None else []

    @property
    def macromolecules(self):
        return [e for e in self.entities if isinstance(e, Macromolecule)]

    @property
    def associations(self):
        return [p for p in self.processes if insinstance(p, Association)]

    @property
    def transcriptions(self):
        transcriptions = []
        for p in self.processes:
            if isinstance(p.reactants[0], EmptySet) and isinstance(p.products[0], NucleicAcidFeature) and UnitOfInformation("ct", "mRNA") in p.products[0].uis:
                for m in self.modulations:
                    if m.target == p and isinstance(m, NecessaryStimulation) and isinstance(m.source, NucleicAcidFeature) and UnitOfInformation("ct", "gene") in m.source.uis:
                        transcriptions.append(p)
        return transcriptions

    @property
    def translations(self):
        translations = []
        for p in self.processes:
            if isinstance(p.reactants[0], EmptySet) and isinstance(p.products[0], Macromolecule):
                for m in self.modulations:
                    if m.target == p and isinstance(m, NecessaryStimulation) and isinstance(m.source, NucleicAcidFeature) and UnitOfInformation("ct", "mRNA") in m.source.uis:
                        translations.append(p)
        return translations

    def add_process(self, proc):
        if isinstance(proc, str):
            parser = Parser()
            proc =  parser.process.parseString(proc)
        if proc not in self.processes:
            if hasattr(proc, "reactants"):
                reactants = []
                for reactant in proc.reactants:
                    existent_reactant = self.get_entity(reactant, by_entity = True)
                    if existent_reactant:
                        reactants.append(existent_reactant)
                    else:
                        self.add_entity(reactant)
                        reactants.append(reactant)
                proc.reactants = reactants

            if hasattr(proc, "products"):
                products = []
                for product in proc.products:
                    existent_product = self.get_entity(product, by_entity = True)
                    if existent_product:
                        products.append(existent_product)
                    else:
                        products.append(product)
                        self.add_entity(product)
                proc.products = products
            self.processes.append(proc)

    def add_entity(self, entity):
        if isinstance(entity, str):
            parser = Parser()
            entity =  parser.entity.parseString(entity)
        if entity not in self.entities:
            self.entities.append(entity)
            if hasattr(entity, "compartment") and entity.compartment:
                existent_compartment = self.get_compartment(entity.compartment, by_compartment  = True)
                if existent_compartment:
                    entity.compartment = existent_compartment
                else:
                    self.add_compartment(entity.compartment)

    def add_modulation(self, mod):
        if isinstance(mod, str):
            parser = Parser()
            mod =  parser.modulation.parseString(mod)
        if mod not in self.modulations:
            source = mod.source
            target = mod.target
            if isinstance(source, Entity):
                existent_source = self.get_entity(source, by_entity = True)
                if existent_source:
                    mod.source = existent_source
                else:
                    self.add_entity(source)
            elif  isinstance(source, LogicalOperator):
                existent_source = self.get_lo(source, by_lo = True)
                if existent_source:
                    mod.source = existent_source
                else:
                    self.add_lo(source)
            existent_target = self.get_process(target, by_process = True)
            if existent_target:
                mod.target = existent_target
            else:
                self.add_process(target)
            self.modulations.append(mod)

    def add_compartment(self, comp):
        if isinstance(comp, str):
            parser = Parser()
            comp =  parser.compartment.parseString(comp)
        if comp not in self.compartments:
            self.compartments.append(comp)

    def add_lo(self, op):
        if isinstance(op, str):
            parser = Parser()
            op =  parser.lo.parseString(op)
        if op not in self.los:
            for child in op.children:
                if isinstance(child, Entity):
                    existent_child = self.get_entity(child, by_entity = True)
                    if existent_child:
                        op.children.remove(child)
                        op.children.append(child)
                    else:
                        self.add_entity(child)
                elif isinstance(child, LogicalOperator):
                    existent_child = get_lo(child, by_lo = True)
                    if existent_child:
                        op.children.remove(child)
                        op.children.append(child)
                    else:
                        self.add_lo(child)
            self.los.append(op)

    def remove_process(self, process):
        if isinstance(process, str):
            parser = Parser()
            process =  parser.process.parseString(process)
        for modulation in self.modulations:
            if modulation.target == process:
                self.remove_modulation(modulation)
        self.processes.remove(process)

    def remove_entity(self, entity):
        if isinstance(entity, str):
            parser = Parser()
            entity =  parser.entity.parseString(entity)
        toremove = set()
        for process in self.processes:
            if entity in process.reactants or entity in process.products:
                toremove.add(process)
        for process in toremove:
            self.remove_process(process)
        toremove = set()
        for modulation in self.modulations:
            if modulation.source == entity:
                toremove.add(modulation)
        for modulation in toremove:
            self.remove_modulation(modulation)
        self.entities.remove(entity)

    def remove_compartment(self, compartment):
        if isinstance(compartment, str):
            parser = Parser()
            compartment =  parser.compartment.parseString(compartment)
        self.compartments.remove(compartment)
        for entity in self.entities:
            if hasattr(entity, "compartment") and entity.compartment == compartment:
                entity.compartment = None

    def remove_lo(self, op):
        if isinstance(op, str):
            parser = Parser()
            op =  parser.lo.parseString(op)
        remove_op = True
        toremove = set()
        for child in op.children:
            if isinstance(child, LogicalOperator):
                toremove.add(child)
        for child in toremove:
            self.remove_lo(child)
        toremove = set()
        for modulation in self.modulations:
            if modulation.source == op:
                toremove.add(modulation)
                remove_op = False
        for modulation in toremove:
            self.remove_modulation(modulation)
        if remove_op:
            self.los.remove(op)

    def remove_modulation(self, modulation):
        if isinstance(modulation, str):
            parser = Parser()
            modulation =  parser.modulation.parseString(modulation)
        self.modulations.remove(modulation)
        if isinstance(modulation.source, LogicalOperator):
            self.remove_lo(modulation.source)

    def get_compartment(self, val, by_compartment = False, by_id = False, by_label = False, by_hash = False, by_string = False):
        for c in self.compartments:
            if by_compartment:
                if c == val:
                    return c
            if by_id:
                if c.id == val:
                    return c
            if by_label:
                if hasattr(c, "label"):
                    if c.label == val:
                        return c
            if by_hash:
                if hash(c) == val:
                    return c
            if by_string:
                if str(c) == val:
                    return c
        return None

    def get_lo(self, val, by_lo = False, by_id = False, by_hash = False, by_string = False):
        for o in self.los:
            if by_lo:
                if o == val:
                    return o
            if by_id:
                if o.id == val:
                    return o
            if by_hash:
                if hash(o) == val:
                    return o
            if by_string:
                if str(o) == val:
                    return o
        return None

    def get_modulation(self, val, by_modulation = False, by_id = False, by_hash = False, by_string = False):
        for m in self.modulations:
            if by_modulation:
                if m == val:
                    return m
            if by_id:
                if m.id == val:
                    return m
            if by_hash:
                if hash(m) == val:
                    return m
            if by_string:
                if str(m) == val:
                    return m
        return None

    def get_process(self, val, by_process = False, by_id = False, by_label = False, by_hash = False, by_string = False):
        for p in self.processes:
            if by_process:
                if p == val:
                    return p
            if by_id:
                if p.id == val:
                    return p
            if by_label:
                if hasattr(p, "label"):
                    if p.label == val:
                        return p
            if by_hash:
                if hash(p) == val:
                    return p
            if by_string:
                if str(p) == val:
                    return p
        return None

    def get_entity(self, val, by_entity = False, by_id = False, by_label = False, by_hash = False, by_string = False):
        for e in self.entities:
            if by_entity:
                if e == val:
                    return e
            if by_id:
                if e.id == val:
                    return e
            if by_label:
                if hasattr(e, "label"):
                    if e.label == val:
                        return e
            if by_hash:
                if hash(e) == val:
                    return e
            if by_string:
                if str(e) == val:
                    return e
        return None

    def union(self, other):
        new = Network()
        for e in self.entities:
            new.add_entity(deepcopy(e))
        for p in self.processes:
            new.add_process(deepcopy(p))
        for m in self.modulations:
            new.add_modulation(deepcopy(m))
        for c in self.compartments:
            new.add_compartment(deepcopy(c))
        for o in self.los:
            new.add_lo(deepcopy(o))
        for e in other.entities:
            new.add_entity(deepcopy(e))
        for p in other.processes:
            new.add_process(deepcopy(p))
        for m in other.modulations:
            new.add_modulation(deepcopy(m))
        for c in other.compartments:
            new.add_compartment(deepcopy(c))
        for o in other.los:
            new.add_lo(deepcopy(o))
        # new.entities = list(set(self.entities).union(set(other.entities)))
        # new.processes = list(set(self.processes).union(set(other.processes)))
        # new.modulations = list(set(self.modulations).union(set(other.modulations)))
        # new.los = list(set(self.los).union(set(other.los)))
        # new.compartments = list(set(self.compartments).union(set(other.compartments)))
        return new

    def intersection(self, other):
        new = Network()
        for e in self.entities:
            if e in other.entities:
                new.add_entity(deepcopy(e))
        for p in self.processes:
            if p in other.processes:
                new.add_process(deepcopy(p))
        for m in self.modulations:
            if m in other.modulations:
                new.add_modulation(deepcopy(m))
        for c in self.compartments:
            if c in other.compartments:
                new.add_compartment(deepcopy(c))
        for o in self.los:
            if o in other.los:
                new.add_compartment(deepcopy(c))
        return new
        # new.entities = list(set(self.entities).intersection(set(other.entities)))
        # new.processes = list(set(self.processes).intersection(set(other.processes)))
        # new.modulations = list(set(self.modulations).intersection(set(other.modulations)))
        # new.los = list(set(self.los).intersection(set(other.los)))
        # new.compartments = list(set(self.compartments).intersection(set(other.compartments)))

    def difference(self, other):
        new = Network()
        for m in self.modulations:
            if m not in other.modulations:
                new.add_modulation(deepcopy(m))
        for p in self.processes:
            if p not in other.processes:
                # for e in p.reactants:
                    # if hasattr(e, "label") and e.label == "p16INK4a":
                        # print("aaa")
                newp = deepcopy(p)
                new.add_process(deepcopy(p))
        for e in self.entities:
            if e not in other.entities:
                new.add_entity(deepcopy(e))
        for c in self.compartments:
            if c not in other.compartments:
                new.add_compartment(deepcopy(c))
        # new.entities = list(set(self.entities).difference(set(other.entities)))
        # new.processes = list(set(self.processes).difference(set(other.processes)))
        # new.modulations = list(set(self.modulations).difference(set(other.modulations)))
        # new.los = list(set(self.los).difference(set(other.los)))
        # new.compartments = list(set(self.compartments).difference(set(other.compartments)))
        return new

    def simplify_gene_expressions(self):
        mods = defaultdict(list)
        for t in self.transcriptions:
            for m in self.modulations:
                if m.target == t:
                    if isinstance(m.source, NucleicAcidFeature) and UnitOfInformation("ct", "gene") in m.source.uis:
                        self.remove_entity(m.source)
                    else:
                        mods[t].append(m)
            self.remove_process(t)
        for tt in self.translations:
            for m in self.modulations:
                if isinstance(m.source, NucleicAcidFeature) and UnitOfInformation("ct", "mRNA") in m.source.uis and m.target == tt:
                    for t in mods:
                        if t.products[0] == m.source:
                            for mod in mods[t]:
                                mod.target = tt
                                self.add_modulation(mod)
                    self.remove_entity(m.source)

    def __eq__(self, other):
        return isinstance(other, Network) and \
                set(self.entities) == set(other.entities) and \
                set(self.processes) == set(other.processes) and \
                set(self.compartments) == set(other.compartments) and \
                set(self.los) == set(other.los) and \
                set(self.modulations) == set(other.modulations)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result
