from __future__ import division

from math import log10
from layouts import BaseLayout, LayoutEdge, LayoutNode

class FeynmanLayout(BaseLayout):

    def get_subgraph(self, vertex):
        if vertex.initial:
            return "initial"
        elif vertex.connecting:
            return "connecting"

    def process(self):

        if self.options.fix_initial:
            initial = self.subgraphs["initial"]
            initial_pairs = len(initial) // 2
            for i, p in enumerate(initial):
                sg_options = self.subgraph_options.setdefault("initial", [])
                sg_options.append('rank="source"')
                pair = i // 2
                if self.width and self.height:
                    stretch = self.options.stretch * self.width / 2.0
                    xposition = stretch + (i % 2) * (self.width - 2 * stretch)
                    yposition = (1 + pair) * self.height / (initial_pairs + 1)
                    p.dot_args["pos"] = "%s,%s!" % (xposition, yposition)
        
        # sort the edges
        def ordering(edge): 
            order = (1 if edge.item.gluon else 
                     0 if edge.item.color else 
                     2 if edge.item.anticolor else None)
            return edge.going.reference, order, edge.item.reference

        self.edges.sort(key=ordering)

    def get_vertex(self, vertex, node_style=None):

        lo = LayoutNode(vertex, width = 0.1, height = 0.1)
        lo.label = False
        lo.subgraph = self.get_subgraph(vertex)

        if node_style:
            lo.dot_args.update(node_style)
       
        if "summary" in vertex.tags:
            lo.width = 1.0
            lo.height = 1.0
        elif vertex.hadronization:
            # Big white hardronization vertices
            if self.options.layout_engine == "dot":
                n_gluons_in = sum(1 for p in vertex.incoming if p.gluon)
                lo.width = 2 + n_gluons_in*0.5
                lo.height = 1
                lo.dot_args["shape"] = "record"
                lo.dot_label = " <leftedge>|<left>|<middle>|<right>|<rightedge>"
            else:
                lo.width = lo.height = 1.0
            
        elif vertex.initial:
            # Big red initial vertices
            lo.width = lo.height = 1.0

        elif vertex.final:
            # Don't show final particle vertices
            lo.show = False
        
        else:
            nr_particles = len(vertex.incoming) + len(vertex.outgoing)
            lo.width = lo.height = nr_particles * 0.04

        return lo
   
    def get_particle(self, particle):

        lo = LayoutEdge(particle, particle.start_vertex, particle.end_vertex)

        lo.label = self.get_label_string(particle.pdgid)
        if particle.gluon or particle.photon:
            lo.label = ""

        lo.dot_args["weight"] = log10(particle.e+1)*0.1 + 1

        if self.options.layout_engine == "dot":
            if particle.end_vertex.hadronization:
                if particle.gluon:
                    lo.port_going = "middle"
                elif particle.color:
                    lo.port_going = "left"
                elif particle.anticolor:
                    lo.port_going = "right"
       
        return lo

class FixedHadronsLayout(FeynmanLayout):
    """
    Place all of the hadronization vertices on the same rank.
    """
    def process(self):

        sg_options = self.subgraph_options.setdefault("hadronization", [])
        sg_options.append('rank="same"')
        
        return super(FixedHadronsLayout, self).process()
        
    @property
    def subgraph_names(self):
        return ["hadronization"] + super(FixedHadronsLayout, self).subgraph_names
        
    def get_subgraph(self, vertex):
        if vertex.hadronization:
            return "hadronization"
        return super(FixedHadronsLayout, self).get_subgraph(vertex)

class InlineLabelsLayout(FeynmanLayout):
    
    def get_particle(self, particle):
            
        down = super(InlineLabelsLayout, self).get_particle(particle)
        if down.item.gluon or down.item.photon:
            return down
        
        middle = LayoutNode(down.item, label=self.get_label_string(down.item.pdgid))
        middle.show = False
        middle.dot_args["margin"] = "0,0"
        #middle.dot_args["shape"] = "square"
        #middle.dot_args["group"] = "plabels"
        
        up = LayoutEdge(down.item, down.coming, middle.item, **down.args)
        down.coming = middle.item
        up.label = down.label = ""
        up.port_going = None
        
        return [up, middle, down] 