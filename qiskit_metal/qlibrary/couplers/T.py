# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
""""""

from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import QComponent
import numpy as np


class T(QComponent):
    """Generate a T shaped coupler with 1 port. The rest of the T is open to ground. All the component has the same gap to the ground plane. Each segment of the T can have different width and length. (0,0) represents the center position of the component.

    Options:
        
    """
    component_metadata = Dict(short_name='cpw', _qgeometry_table_path='True')
    """Component metadata"""

    #Currently setting the primary CPW length based on the coupling_length
    #May want it to be it's own value that the user can control?
    default_options = Dict(prime_width='10um',
                           prime_length='100um',
                           second_width='10um',
                           second_length='50um',
                           gap='6um')
    """Default connector options"""

    TOOLTIP = """This component creates a T shaped coupler with 1 port. The rest of the T is open to ground. All the component has the same gap to the ground plane. Each segment of the T can have different width and length."""

    def make(self):
        """Build the component."""
        p = self.p
        
        #Primary segment
        prime_segment = draw.rectangle(p.prime_width, p.prime_length, 0, p.prime_length/2)
        second_segment = draw.rectangle(p.second_length, p.second_width, 0, 0)
        
        segment = draw.union(prime_segment, second_segment)

        #Secondary segment
        second_segment = draw.LineString([[-p.second_length/2, 0], [p.second_length/2, 0]])
        
        # Background subtraction gap
        background_1 = draw.rectangle(p.prime_width + 2*p.gap, p.prime_length + 2*p.gap, 0, p.prime_length/2)
        background_2 = draw.rectangle(p.second_length + 2*p.gap, p.second_width + 2*p.gap, 0, 0)
        background = draw.union(background_1, background_2)

        # #Rotate and Translate
        # c_items = [prime_cpw, second_cpw]
        # c_items = draw.rotate(c_items, p.orientation, origin=(0, 0))
        # c_items = draw.translate(c_items, p.pos_x, p.pos_y)
        # [prime_cpw, second_cpw] = c_items

        #Add to qgeometry tables
        self.add_qgeometry('poly', {'background': background},
                           subtract=True,
                           layer=p.layer)
        
        self.add_qgeometry('poly', {'segment': segment},
                           layer=p.layer)
        
        
        # self.add_qgeometry('path', {'prime_cpw': prime_cpw},
        #                    width=p.prime_width,
        #                    layer=p.layer)
        # self.add_qgeometry('path', {'prime_cpw_sub': prime_cpw},
        #                    width=p.prime_width + 2 * p.prime_gap,
        #                    subtract=True,
        #                    layer=p.layer)
        # self.add_qgeometry('path', {'second_cpw': second_cpw},
        #                    width=p.second_width,
        #                    layer=p.layer)
        # self.add_qgeometry('path', {'second_cpw_sub': second_cpw},
        #                    width=p.second_width + 2 * p.second_gap,
        #                    subtract=True,
        #                    layer=p.layer)

        # #Add pins
        # prime_pin_list = prime_cpw.coords
        # second_pin_list = second_cpw.coords

        # self.add_pin('prime_start',
        #              points=np.array(prime_pin_list[::-1]),
        #              width=p.prime_width,
        #              input_as_norm=True)
        # self.add_pin('prime_end',
        #              points=np.array(prime_pin_list),
        #              width=p.prime_width,
        #              input_as_norm=True)
        # self.add_pin('second_end',
        #              points=np.array(second_pin_list),
        #              width=p.second_width,
        #              input_as_norm=True)
