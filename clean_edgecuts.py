"""Remove disconnected Edge.Cuts geometry from a KiCad board copy."""

import sys
from collections import defaultdict

import pcbnew


def point_key(point):
    return int(point.x), int(point.y)


def main(source, destination):
    board = pcbnew.LoadBoard(source)
    drawings = [drawing for drawing in board.GetDrawings()
                if drawing.GetLayerName() == "Edge.Cuts"
                and hasattr(drawing, "GetStart")
                and hasattr(drawing, "GetEnd")]

    graph = defaultdict(list)
    for index, drawing in enumerate(drawings):
        graph[point_key(drawing.GetStart())].append(index)
        graph[point_key(drawing.GetEnd())].append(index)

    components = []
    unseen = set(range(len(drawings)))
    while unseen:
        component = set()
        stack = [unseen.pop()]
        while stack:
            index = stack.pop()
            component.add(index)
            ends = (point_key(drawings[index].GetStart()),
                    point_key(drawings[index].GetEnd()))
            for end in ends:
                for neighbor in graph[end]:
                    if neighbor in unseen:
                        unseen.remove(neighbor)
                        stack.append(neighbor)
        components.append(component)

    if not components:
        raise RuntimeError("No connected Edge.Cuts outline found")

    keep = max(components, key=len)
    for index, drawing in enumerate(drawings):
        if index not in keep:
            board.Remove(drawing)

    pcbnew.SaveBoard(destination, board)
    print(f"Kept {len(keep)} Edge.Cuts segments; removed {len(drawings) - len(keep)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(f"usage: {sys.argv[0]} INPUT.kicad_pcb OUTPUT.kicad_pcb")
    main(sys.argv[1], sys.argv[2])
