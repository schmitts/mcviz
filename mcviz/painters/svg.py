from ..svg import SVGDocument
from ..svg import identity, photon, final_photon, gluon, multigluon, boson, fermion, hadron, vertex
from ..styles import svg

from painters import GraphvizPainter

from ..utils import get_logger; log = get_logger("svg_painter")

class SVGPainter(GraphvizPainter):

    type_map = {"identity": identity,
                "photon": photon, 
                "final_photon": final_photon,
                "gluon": gluon, 
                "multigluon": multigluon, 
                "boson": boson, 
                "fermion": fermion, 
                "hadron": hadron, 
                "vertex": vertex
                }

    def paint(self):
        self.layout()
        svg(self.layout) # apply svg style
        self.style()
        engine = self.options.layout_engine
        engine = engine if engine else "dot"
        opts = self.options.extra_gv_options
        if not any(opt.startswith("-T") for opt in opts):
            opts.append("-Tplain")
        assert "-Tplain" in opts, "For SVG painting with the internal painter only -Tplain is supported"
        plain = self.graphviz_pass(engine, opts, self.layout.dot)
        self.layout.update_from_plain(plain)
    
        self.doc = SVGDocument(self.layout.width, self.layout.height, self.layout.scale)
        for edge in self.layout.edges:
            if not edge.spline:
                # Nothing to paint!
                continue
            self.paint_edge(edge)
        for node in self.layout.nodes:
            self.paint_vertex(node)

        self.write_data(self.doc.toprettyxml())

    def paint_edge(self, edge):
        """
        In the dual layout, paint a connection between particles
        """

        if edge.show and edge.spline:
            display_func = self.type_map.get(edge.style_line_type, hadron)
            self.doc.add_object(display_func(spline=edge.spline, **edge.style_args))

        if edge.label and edge.label_center:
            if "<" in edge.label:
                self.doc.add_glyph(edge.item.pdgid, edge.label_center,
                               self.options.label_size,
                               ", ".join(map(str, edge.item.subscripts)))
            else:
                self.doc.add_text_glyph(edge.label, edge.label_center,
                               self.options.label_size,
                               ", ".join(map(str, edge.item.subscripts)))


    def paint_vertex(self, node):
        if node.show and node.center:
            vx = vertex(node.center, node.width/2, node.height/2,
                        **node.style_args)
            self.doc.add_object(vx)
           
        if node.label and node.center:
            # This needs fixing for the Feynman layout, if we want node labels.
            self.doc.add_glyph(node.item.pdgid, node.center.tuple(),
                               self.options.label_size,
                               ", ".join(map(str, node.item.subscripts)))

