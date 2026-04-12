# -*- coding: utf-8 -*-
from math import cos, sin, pi
from shapely.geometry import CAP_STYLE
from qiskit_metal import draw
from qiskit_metal.qlibrary.core import QComponent


def _sector_polygon(radius, theta1_deg, theta2_deg, n=96):
    """Sector circular centrado en (0,0) entre ángulos en grados."""
    t1 = pi * theta1_deg / 180.0
    t2 = pi * theta2_deg / 180.0
    if t2 < t1:
        t1, t2 = t2, t1
    ts = [t1 + (t2 - t1) * k / (n - 1) for k in range(n)]
    pts = [(0.0, 0.0)] + [(radius * cos(t), radius * sin(t)) for t in ts]
    return draw.Polygon(pts)


class QuantumCircuitLogo(QComponent):
    """
    Logo tipo 'Quantum Circuit': C exterior con abertura + Q interior,
    sobre un fondo cuadrado.

    Opciones principales:
        * bg_size: '6mm'           (lado del cuadrado de fondo)
        * outer_r: '2.5mm'         (radio exterior de la C)
        * ring_thickness: '0.5mm'  (espesor de la C)
        * opening_deg: '60'        (abertura angular de la C, centrada en +X)
        * q_scale: '0.55'          (RQ = q_scale * outer_r)
        * q_thickness: '0.35mm'    (espesor del anillo de la Q)
        * tail_length: '1.2mm'     (largo de la “cola” de la Q)
        * tail_width: '0.28mm'     (ancho de la cola)
        * tail_angle: '-45'        (ángulo de la cola, -45° ~ abajo-derecha)
        * rotation: '0'            (rotación global del logo, grados)
        * bg_subtract: 'False'     (si True, recorta el sustrato con el fondo)
        * logo_subtract: 'False'   (si True, el logo recorta al fondo)
        * resolution: '64'         (resolución de buffers circulares)
    """

    default_options = dict(
        # posicion
        pos_x='0um', pos_y='0um',
        # fondo y logo
        bg_size='6mm',
        outer_r='2.5mm',
        ring_thickness='0.5mm',
        opening_deg='60',
        resolution='64',
        # Q interna
        q_scale='0.55',
        q_thickness='0.35mm',
        tail_length='1.2mm',
        tail_width='0.28mm',
        tail_angle='-45',
        # transform
        rotation='0',
        # flags
        bg_subtract='False',
        logo_subtract='False',
        helper='False'
    )

    TOOLTIP = "Logo Quantum Circuit (C + Q) con fondo cuadrado"

    def make(self):
        p = self.p  # parámetros parseados

        # --- Fondo cuadrado (centrado) ---
        bg = draw.rectangle(p.bg_size, p.bg_size, 0, 0)

        # --- Anillo exterior (C) ---
        Ro = p.outer_r
        tC = p.ring_thickness
        Ri = max(1e-9, Ro - tC)

        outer_disk = draw.Point(0, 0).buffer(Ro, resolution=int(p.resolution),
                                             cap_style=CAP_STYLE.round)
        inner_disk = draw.Point(0, 0).buffer(Ri, resolution=int(p.resolution),
                                             cap_style=CAP_STYLE.round)
        ring_C = draw.subtract(outer_disk, inner_disk)

        # abrir la C con un sector centrado en +X (0°)
        open_deg = float(p.opening_deg)
        wedge = _sector_polygon(Ro * 1.2, -open_deg/2.0, open_deg/2.0, n=max(32, int(p.resolution)))
        ring_C = draw.subtract(ring_C, wedge)

        # --- Q interna: anillo + cola ---
        Rq = float(p.q_scale) * Ro
        tq = p.q_thickness
        rqi = max(1e-9, Rq - tq)

        q_outer = draw.Point(0, 0).buffer(Rq, resolution=int(p.resolution), cap_style=CAP_STYLE.round)
        q_inner = draw.Point(0, 0).buffer(rqi, resolution=int(p.resolution), cap_style=CAP_STYLE.round)
        ring_Q = draw.subtract(q_outer, q_inner)

        # Cola de la Q como rectángulo centrado, rotado y desplazado radialmente
        tail_len = p.tail_length
        tail_w   = p.tail_width
        tail_ang = float(p.tail_angle)

        tail = draw.rectangle(tail_len, tail_w)  # centrado en (0,0)
        tail = draw.rotate(tail, tail_ang, origin=(0, 0))
        # desplazar para que "salga" desde el borde del anillo interior
        # colocamos el centro de la cola cerca del perímetro interior de la Q
        ang = pi * tail_ang / 180.0
        radial = rqi + 0.5*tail_len*0.6  # pequeño ajuste empírico para que se vea bien
        tail = draw.translate(tail, radial * cos(ang), radial * sin(ang))

        Q_shape = draw.union(ring_Q, tail)

        # --- Logo completo (C + Q) ---
        logo = draw.union(ring_C, Q_shape)

        # aplicar rotación global y traslación
        logo = draw.rotate(logo, float(p.rotation), origin=(0, 0))
        bg   = draw.rotate(bg,   float(p.rotation), origin=(0, 0))

        logo = draw.translate(logo, p.pos_x, p.pos_y)
        bg   = draw.translate(bg,   p.pos_x, p.pos_y)

        # --- Añadir geometrías ---
        # Fondo (podés usar otra 'layer' si querés separar)
        self.add_qgeometry('poly', {'bg': bg},
                           subtract=p.bg_subtract,
                           helper=p.helper)

        # Logo: como metal o como recorte del fondo
        self.add_qgeometry('poly', {'logo': logo},
                           subtract=p.logo_subtract,
                           helper=p.helper)