# makeHexagon.py
# Eric Pavey - 2014-11-22
# www.akeric.com

import pymel.core as pm

def main(hexOnly=True, doHollow=True):
    """
    Based on the selected poly objects, convert their faces to hexagonal shapes.
    It expects all faces to be quads, but no check is made for this.

    Parameters:
    hexOnly : bool : Default True.  If True, delete all faces that aren't hexagons.
    doHollow : bool : Default True.  If True, create hollow hexagons by extruding
        them in, and deleting the resultant faces.  The history is left, so the
        user can adjust later.
    """
    sel = pm.ls(selection=True)
    if not sel:
        pm.displayError("Please select at least one poly object")
        return

    mesh = pm.listRelatives(sel, type='mesh')

    # Convert from quads to tris
    pm.polyTriangulate(sel)
    # Apply the smooth, which will create the hexagonal pattern:
    pm.polySmooth(mth=0, divisions=1, bnr=1, continuity=1, keepBorder=1,
                  keepSelectionBorder=1, keepTessellation=1, kmb=1, suv=1,
                  propagateEdgeHardness=1, sl=1, dpe=1, ps=0.1, ro=1,
                  constructionHistory=1)
    # Pick only verts that have six connecting edges:  This is the vert in the
    # middle of each hexagon:
    pm.select(pm.polyListComponentConversion(toVertex=True))
    pm.mel.eval("changeSelectMode -component")
    pm.polySelectConstraint(type=0x0001, mode=2, order=True, orderbound=[6,6])
    midVerts = pm.ls(selection=True)
    pm.polySelectConstraint(mode=0, disable=True, where=False)
    # Convert those to their edges, and delete:
    edges = pm.ls(pm.polyListComponentConversion(midVerts, toEdge=True))
    pm.delete(edges)
    # Select all verts, and delete:  This will clean up any verts with only two
    # edges:
    pm.mel.eval("changeSelectMode -object")
    pm.select(sel)
    newVerts = pm.ls(pm.polyListComponentConversion(toVertex=True))
    pm.delete(newVerts)
    # This will remove all faces that aren't hexagons, if wanted:
    if hexOnly:
        notSix = []
        for s in mesh:
            for face in s.f:
                if len(face.getEdges()) < 6:
                    notSix.append(face)
        if notSix:
            pm.delete(notSix)
    # Create the extrude & delete that will hollow out the hexagons.
    if doHollow:
        pm.select(pm.polyListComponentConversion(toFace=True))
        pm.polyExtrudeFacet(constructionHistory=True, keepFacesTogether=0, pvx=0,
                            pvy=0, pvz=0, divisions=1, twist=0, taper=1, offset=0.2,
                            thickness=0, smoothingAngle=30)
        pm.delete()
    else:
        six = []
        for s in mesh:
            for face in s.f:
                if len(face.getEdges()) >= 6:
                    six.append(face)
        if six:
            pm.mel.eval("changeSelectMode -component")
            pm.select(six)


    if doHollow:
        pm.select(sel)
        pm.displayInfo("Convert to hexagon complete!  Select 'polyExtrudeFace' in the Channel Box & hit 't' to change settings.")
    else:
        pm.displayInfo("Convert to hexagon complete!")