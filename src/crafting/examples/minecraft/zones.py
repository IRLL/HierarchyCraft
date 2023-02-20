""" Minecraft Zones

Abstract zones to simulate simply a Minecraft environment.

"""

from crafting.elements import Zone

#: Zones
FOREST = Zone("forest")  #: FOREST
SWAMP = Zone("swamp")  #: SWAMP
MEADOW = Zone("meadow")  #: MEADOW
UNDERGROUND = Zone("underground")  #: UNDERGROUND
BEDROCK = Zone("bedrock")  #: BEDROCK
NETHER = Zone("nether")  #: NETHER
END = Zone("end")  #: ENDER
STRONGHOLD = Zone("stronghold")  #: STRONGHOLD

OVERWORLD = [FOREST, SWAMP, MEADOW, STRONGHOLD, UNDERGROUND, BEDROCK]
