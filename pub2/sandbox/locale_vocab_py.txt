# Yet another go at the ENGINE CORE locale module (for Spanish)

# SECCION de VOCABULAR
# Aqui, provide definiciones para las palabras que aparecen en el kernal del motor de IF.
#   (IF=ficcion interactivo)

# Map internal verb name (based on English) to localized word (including synonyms).
# The first synonym will be used on output, unless overridden.
# Any synonym will have the same meaning on input.
#
# (The instructions should be translated as much as possible, too, but I'm lazy)
#
verbs = {
        # *go* - the character moves from one place to another
        'go':       (('ir:','ven','va'), ('mover:','mueve','mueve'), 'camin~ar'),

        # *enter* or *get in* - the character becomes contained by the object
        'enter':    ('entr~ar',),

        # *put* - character causes a thing in *inventory* to be moved to a specific place
        'put':      (('poner:','ponga','pone'),),

        # *drop* - character moves thing from *inventory* to current room
        'drop':     (('deber (fall)','debe (fall)', 'debe (fall)'),)

        # *get* - character causes visible thing to move into *inventory*
        'get':      (('obtenir:', 'obtenga', 'obtiene'),),

        
