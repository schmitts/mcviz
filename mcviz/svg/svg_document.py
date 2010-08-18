from .texglyph import TexGlyph

from xml.dom.minidom import getDOMImplementation, Document
dom_impl = getDOMImplementation()

class SVGDocument(object):
    def __init__(self, wx, wy, scale = 1):

        self.doc = dom_impl.createDocument("http://www.w3.org/2000/svg", "svg", None)

        self.svg = self.doc.documentElement
        self.svg.setAttribute("xmlns", "http://www.w3.org/2000/svg")
        self.svg.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink")
        self.svg.setAttribute("viewBox", "0 0 %.1f %.1f" % (wx * scale, 
                                                            wy * scale))
        self.svg.setAttribute("version", "1.1")

        if scale != 1:
            g = self.doc.createElement("g")
            g.setAttribute("transform","scale(%.5f)" % scale)
            self.svg.appendChild(g)
            self.svg = g

        self.defs = self.doc.createElement("defs")
        self.svg.appendChild(self.defs)

    def add_glyph(self, pdgid, x, y, font_size, pid = None):

        if not TexGlyph.exists(pdgid):
            return self.add_text_glyph(pdgid, x, y, font_size, pid)

        glyph = TexGlyph.from_pdgid(pdgid)
        glyph.dom.setAttribute("transform", "scale(%.6f)" % (glyph.default_scale))
        if not glyph.dom in self.defs.childNodes:
            self.defs.appendChild(glyph.dom)

        if False: #options.debug_labels:
            wx, wy = glyph.dimensions
            wx *= font_size * glyph.default_scale
            wy *= font_size * glyph.default_scale

            box = self.doc.createElement("rect")
            box.setAttribute("x", "%.3f" % (x - wx/2))
            box.setAttribute("y", "%.3f" % (y - wy/2))
            box.setAttribute("width", "%.3f" % wx)
            box.setAttribute("height", "%.3f" % wy)
            box.setAttribute("fill", "red")
            self.svg.appendChild(box)

        x -= 0.5 * (glyph.xmin + glyph.xmax) * font_size * glyph.default_scale
        y -= 0.5 * (glyph.ymin + glyph.ymax) * font_size * glyph.default_scale

        use = self.doc.createElement("use")
        use.setAttribute("x", "%.3f" % (x/font_size))
        use.setAttribute("y", "%.3f" % (y/font_size))
        use.setAttribute("transform", "scale(%.3f)" % (font_size))
        use.setAttribute("xlink:href", "#pdg%i"%pdgid)
        self.svg.appendChild(use)

        if pid:
            x_pid = x + glyph.xmax * glyph.default_scale * font_size
            y_pid = y + glyph.ymax * glyph.default_scale * font_size
            self.add_pid(pid, x_pid, y_pid, font_size)

    def add_text_glyph(self, pdgid, x, y, font_size, pid = None):
        label = "%i" % pdgid
        width_est = len(label) * font_size * 0.6
        txt = self.doc.createElement("text")
        txt.setAttribute("x", "%.3f" % (x - width_est / 2))
        txt.setAttribute("y", "%.3f" % (y))
        txt.setAttribute("font-size", "%.2f" % (font_size))
        txt.appendChild(self.doc.createTextNode(label))
        self.svg.appendChild(txt)

        if pid:
            self.add_pid(pid, x + width_est/2, y + font_size/3, font_size)

    def add_pid(self, pid, x, y, font_size):
        txt = self.doc.createElement("text")
        txt.setAttribute("x", "%.3f" % (x))
        txt.setAttribute("y", "%.3f" % (y))
        txt.setAttribute("font-size", "%.2f" % (font_size*0.3))
        txt.appendChild(self.doc.createTextNode("%i" % pid))
        self.svg.appendChild(txt)

    def add_object(self, element):
        self.svg.appendChild(element)

    def toprettyxml(self):
        return self.doc.toprettyxml()

