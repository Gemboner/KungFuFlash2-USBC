"""KiKit framing plugin: 5 mm top rail and side rails, no bottom rail."""

from shapely.geometry import box

from kikit.plugin import FramingPlugin
from kikit.substrate import Substrate


def _substrate(geometry):
    result = Substrate([])
    result.union(geometry)
    return result


class TopSides(FramingPlugin):
    """Build a frame on the top, left, and right sides only."""

    def _geometry(self, minx, miny, maxx, maxy):
        framing = self.preset["framing"]
        width = framing["width"]
        hspace = framing.get("hspace", framing.get("space", 0))
        vspace = framing.get("vspace", framing.get("space", 0))

        left = box(minx - hspace - width, miny, minx - hspace, maxy)
        right = box(maxx + hspace, miny, maxx + hspace + width, maxy)
        # KiCad's Y coordinate increases downwards, so miny is the top edge.
        top = box(minx - hspace - width, miny - vspace - width,
                  maxx + hspace + width, miny - vspace)
        return left, right, top

    def buildFraming(self, panel):
        minx, miny, maxx, maxy = panel.boardsBBox()
        for geometry in self._geometry(minx, miny, maxx, maxy):
            panel.appendSubstrate(geometry)
        # The frame has no corner cuts; the panel is separated by tab cuts.
        return []

    def buildDummyFramingSubstrates(self, substrates):
        bounds = [s.bounds() for s in substrates]
        minx = min(item[0] for item in bounds)
        miny = min(item[1] for item in bounds)
        maxx = max(item[2] for item in bounds)
        maxy = max(item[3] for item in bounds)
        return [_substrate(geometry)
                for geometry in self._geometry(minx, miny, maxx, maxy)]
