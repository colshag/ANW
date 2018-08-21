# ---------------------------------------------------------------------------
# Armada Net Wars (ANW)
# sl library
# Written by Sean Riley
# ---------------------------------------------------------------------------
# entityManager.py
# Manages entity objects using weak references
# ---------------------------------------------------------------------------
import weakref

## Entity GID management
gLastId = 1000
gAllEntities = weakref.WeakValueDictionary()    
        
def lookupGID(gid):
    return gAllEntities.get(gid,None)

def nextGID(entity):
    global gLastId, gAllEntities
    gid = gLastId
    gAllEntities[gid] = entity
    gLastId += 1
    return gid

def assignGID(gid, entity, oldGid = None):
    """Associate a paritcular GID with an entity
    """
    global gAllEntities

    if gid == oldGid:
        return
    
    # ensure the new gid is not already in use
    if gAllEntities.has_key(gid):
        raise "Entity ID %s already taken!!" % gid

    # remove the old gid if it exists
    if oldGid:
        if gAllEntities.has_key(oldGid):
            del gAllEntities[oldGid]
            
    gAllEntities[gid] = entity
