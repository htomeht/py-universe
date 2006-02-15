class Drink(Verb):
    dobj_iface = IDrink
    iobj_ifaces = { "from": (IContainer, ILiqContainer),
                    "in": (IContainer, ILiqContainer),
                    "using": IStraw,
                    "through": IStraw,
                    }

    prepositions = property(get_prepositions, ...)
    
    def get_prepositions(self):
        return [Preposition(self, k) for k in self.iobj_ifaces.keys()]


