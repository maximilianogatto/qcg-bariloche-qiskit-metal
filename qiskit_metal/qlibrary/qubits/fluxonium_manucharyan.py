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

# This class was created by Maximiliano Gatto (5 Jun. 2025) and is based on the class of Figen YILMAZ, Christian Kraglund Andersen for FloxoniumPocket. This class represent the design that Alex drew.

"""Fluxonium Pocket (Alex)"""

from operator import length_hint
import numpy as np
from qiskit_metal import draw, Dict
from math import *
from qiskit_metal.draw.basic import buffer
from qiskit_metal.qlibrary.core import BaseQubit
import copy
from shapely.geometry import GeometryCollection

class FluxoniumPocket(BaseQubit):
    """The base `AlexFluxonium` class.

    Inherits `BaseQubit` class.

    Description:

    """

    component_metadata = Dict(short_name='FluxoniumPocket',
                              _qgeometry_table_path='True',
                              _qgeometry_table_poly='True',
                              _qgeometry_table_junction='True',
                             )
    """Component metadata"""

    
    default_options = Dict(
            #general
            pos_x='0um',
            pos_y='0um',
            orientation=0,
            chip='main',
            cpw_width='10um',
            cpw_gap='6um',
            
            # Background
            background_width='3mm',
            background_height='3mm',
            
            # pad 
            pad_width_max='80um',
            pad_width_min='4um',
            pad_height='100um',
            pad_gap='45um',
            
            # loop
            loop_position='left',
            loop_height='18um',
            loop_width='70um',
            
            # JJ
            jj_width='5um',
            jj_height='5um',
            L_j = '40.7885nH',
            C_j = '0.72fF',
            
            # JJ array
            jj_array_width = '4um',
            L_jj = '218.823nH',
            gds_cell_jj_array = 'gds_cell_jj_array',
            
            # RESONATOR
            resonator_options=Dict(
                make_resonator=True,
                resonator_length='100um',
                resonator_width='30um',
                resonator_gap='16um',
                qubit_res_gap = '40um',
                jj_dist='35um',
                jj_array_width = '4um',
                L_res = '100nH',    # Inductance of the resonator (JJ array)
            ),
            # FLUX BIAS LINE
            flux_line_options=Dict(
                make_flux_bias_line=True,
                total_length = '1.5mm',
                width = '8um',
                sep_lines='5.2um',
                wait_length='100um',
                adjust_length='50um',
                pad_width='80um',
                pad_height='100um',
                pad_gap='100um',
        )
    )

    # component_metadata = Dict(short_name='component',
    #                          _qgeometry_table_poly='True')
    component_metadata = Dict(short_name='FluxoniumPocket',
                              _qgeometry_table_path='True',
                              _qgeometry_table_poly='True',
                              _qgeometry_table_junction='True',
                             )
    
    TOOLTIP = """The base `FluxoniumPocket` class."""

    def make(self):
        """Define the way the options are turned into QGeometry.

        The make function implements the logic that creates the geometry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed
        information, such as layer, subtract, etc.
        """
        self.make_pocket()
       
        # if self.p.flux_bias_line_options.make_fbl == True:
        #     self.make_flux_bias_line()
        # if self.p.charge_line_options.make_cl == True:
        #     self.make_charge_line()            
        if self.p.resonator_options.make_resonator == True:
            self.make_resonator()
        
        # if self.p.flux_line_options.make_flux_bias_line == True:
        #     self.make_flux_bias_line()
        
    def make_pocket(self):
        ########### SCARAR EL LEFT RIGHT Y HACER UN ESPEJADO ###########
        
        """Makes standard fluxonium in a pocket."""
        # self.p allows us to directly access parsed values (string -> numbers) form the user option
        p = self.parse_options()
        p_res = self.p.resonator_options
        p_flux = self.p.flux_line_options
        
        # Background
        background_width = p.background_width
        background_height = p.background_height
        
        # Pads
        pad_width_max = p.pad_width_max
        pad_width_min = p.pad_width_min
        pad_height = p.pad_height
        pad_gap = p.pad_gap
        
        # Loop
        loop_height = p.loop_height
        loop_width = p.loop_width
        
        # JJ
        jj_width = p.jj_width
        jj_height = p.jj_height
        L_j = p.L_j
        C_j = p.C_j
        
        # JJ array
        jj_array_width = p.jj_array_width

        # Draw the background pocket
        background = draw.rectangle(background_width, background_height, 0, 0)
        
        # Daw the pads
        pa = (-pad_width_max/2, 0)
        pb = (pa[0] + pad_width_max, pa[1])
        pc = (pad_width_min/2, pad_height)
        pd = (pc[0] - pad_width_min, pc[1])
        # Create the pads as polygons
        pad_b = draw.Polygon([pa, pb, pc, pd])  # bottom pad
        
        # Add the loop
        rec_loop = draw.rectangle(pad_width_min, pad_gap/2 - jj_height/2, 0, pad_height + (pad_gap/2 - jj_height/2)/2)  # rectangle for the loop
        pad_b = draw.union([pad_b, rec_loop])  # union the bottom pad with the loop
        
        pad_t = copy.deepcopy(pad_b)  # top pad
        pad_t = draw.rotate(pad_t, 180, (0, pad_height/2))  # rotate the top pad
        pad_t = draw.translate(pad_t, 0, pad_gap + pad_height)  # translate the top pad
        
        pads = draw.union([pad_b, pad_t])  # union the two pads
        
        # Add the Josephson junctions (JJ) to the pads
        jj_object = draw.LineString([(0, pad_height + pad_gap/2 - jj_height/2), (0, pad_height + pad_gap/2 + jj_height/2)])  # JJ line
        
        # Add jj array (the design has 2 jj arrays)
        y_center = pad_height + pad_gap/2  # y center of the JJ array
        jj_array_1 = draw.LineString([(pad_width_min/2, y_center+loop_height/2+jj_array_width/2), (loop_width, y_center+loop_height/2+jj_array_width/2)])   # first JJ array
        jj_array_2 = draw.LineString([(pad_width_min/2, y_center-loop_height/2-jj_array_width/2), (loop_width, y_center-loop_height/2-jj_array_width/2)])   # second JJ array
        
        # Add the rectangle to close te loop
        close_loop = draw.rectangle(pad_width_min, loop_height+2*jj_array_width, loop_width+pad_width_min/2, y_center)
        
        port_lines = None
        
        # Check if have to add the flux bias line
        print("SEP", p_flux.sep_lines)
        if p.flux_line_options.make_flux_bias_line == True:
            # Add thin lines for the flux bias line
            thin_line_1 = draw.rectangle(p_flux.wait_length, jj_array_width, loop_width+pad_width_min/2+p_flux.wait_length/2, y_center + p_flux.sep_lines/2+jj_array_width/2)  # rectangle for the flux bias line

            # Add the adjust line
            pa = (loop_width+pad_width_min/2+p_flux.wait_length, y_center + p_flux.sep_lines/2)
            pb = (pa[0] + p_flux.adjust_length, pa[1])
            pc = (pa[0] + p_flux.adjust_length, pa[1] + p_flux.width)
            pd = (pa[0], pa[1] + jj_array_width)
            
            adjust_pad = draw.Polygon([pa, pb, pc, pd])
            dist_rest = p_flux.total_length - p_flux.wait_length - p_flux.adjust_length
            rest_line = draw.rectangle(dist_rest, p_flux.width, pb[0] + dist_rest/2, pb[1] + p_flux.width/2)  # rectangle for the rest of the flux bias line 
            
            # add the pad for the flux bias line
            flux_pad = draw.rectangle(p_flux.pad_width, p_flux.pad_height, pb[0] + dist_rest + p_flux.pad_width/2, pb[1] + p_flux.pad_height/2 + p_flux.pad_gap/2-p_flux.sep_lines/2)  # rectangle for the flux bias line pad
            
            # connect the pad to the flux bias line
            line_connect = draw.rectangle(p_flux.width, p_flux.pad_gap/2 -p_flux.sep_lines/2,  pb[0] + dist_rest + p_flux.width/2, pb[1] +p_flux.pad_gap/4 - +p_flux.sep_lines/4)
            
            flux_bias_line = draw.union([thin_line_1, adjust_pad, rest_line, line_connect, flux_pad])  # union the thin lines and the adjust line
            
            # Copy, mirror and translate the flux bias line to the left side of the pocket
            flux_bias_line_2 = copy.deepcopy(flux_bias_line)  # copy the flux bias line
            
            # Calculate the center Y of the system to mirror the flux bias line
            y_center = pad_height + pad_gap/2  # Centro Y del sistema

            # mirror the flux bias line to the left side of the pocket
            flux_bias_line_2 = draw.scale(flux_bias_line_2, xfact=1, yfact=-1, origin=(0, y_center))

            flux_bias_line = draw.union([flux_bias_line, flux_bias_line_2])  # union the two flux bias lines
            close_loop = draw.union([close_loop, flux_bias_line])  # union the close loop with the flux bias line
            
            # add ports
            port_flux_in = draw.LineString([(pb[0] + dist_rest + p_flux.pad_width, pb[1] + p_flux.pad_gap/2 -p_flux.sep_lines/2), (pb[0] + dist_rest + p_flux.pad_width, pb[1] + p_flux.pad_gap/2 -p_flux.sep_lines/2 + p_flux.pad_height)])
            
            port_flux_out = draw.LineString([(pb[0] + dist_rest + p_flux.pad_width, pb[1] - p_flux.pad_gap/2 +p_flux.sep_lines/2), (pb[0] + dist_rest + p_flux.pad_width, pb[1] - p_flux.pad_gap/2 +p_flux.sep_lines/2 - p_flux.pad_height)])
            
            # self.add_pin('flix_in', port_flux_in.coords, p.cpw_width)
            
            # port_flux_out = draw.LineString([(pb[0] + dist_rest + p_flux.pad_width/2, pb[1] - p_flux.pad_gap/4 + p_flux.pad_height), (pb[0] + dist_rest + p_flux.pad_width/2, pb[1] + p_flux.pad_gap/4)])  # port for the flux bias line
            
            port_lines = (port_flux_in, port_flux_out)
            
        
        all_objects = [pads, close_loop, jj_object, jj_array_1, jj_array_2, port_lines]
        # translate to the center of the background pocket
        total_y_distances = 2*pad_height + pad_gap + p_res.qubit_res_gap + 2*p_res.resonator_width + p_res.resonator_gap
        all_objects = draw.translate(all_objects, 0, -total_y_distances/2)  # translate the objects to the center of the background pocket
        
        # rotate the loop
        if p.loop_position == 'left':
            all_objects = draw.scale(all_objects, xfact=-1, yfact=1, origin=(0, 0))  # mirror the object to the left side of the pocket
    
        pads, close_loop, jj_object, jj_array_1, jj_array_2, port_lines = all_objects
        
        all_objects = [background, pads, close_loop, jj_object, jj_array_1, jj_array_2, port_lines]
        # rotate the object
        all_objects = draw.rotate(all_objects, p.orientation, origin=(0, 0))
        # translate the object to the position defined by the user
        all_objects = draw.translate(all_objects, p.pos_x, p.pos_y)
        
        background, pads, close_loop, jj_object, jj_array_1, jj_array_2, port_lines = all_objects
        # There are 3 geometries that we can add:
        #   - poly: polygon      # Used for solid shapes like pads or pockets (e.g., rectangles, polygons).
        #   - path:              # Used for thin traces or wires, defined by a path with width (not used in this example).
        #   - junction:          # Used specifically for Josephson junctions, must be a LineString and can have physical properties like width, inductance, and capacitance.
        
        self.add_qgeometry('poly', {'pocket': background}, subtract=True, chip=p.chip)
        self.add_qgeometry('poly', {'pads': pads}, chip=p.chip)
        self.add_qgeometry('poly', {'close_loop': close_loop}, chip=p.chip)
        
        self.add_qgeometry('junction', {'jj_object': jj_object},
                            width=jj_width,
                            hfss_inductance = L_j,
                            hfss_capacitance = C_j,
                            chip=p.chip)
        self.add_qgeometry('junction', {'jj_array_1': jj_array_1},
                            width=p.jj_array_width,
                            hfss_inductance = p.L_jj,
                            # hfss_capacitance = p.C_jj,  # capacitance is not defined for the JJ array
                            chip=p.chip,
                            gds_cell_name=p.gds_cell_jj_array)
        self.add_qgeometry('junction', {'jj_array_2': jj_array_2},
                            width=p.jj_array_width,
                            hfss_inductance = p.L_jj,
                            # hfss_capacitance = p.C_jj,  # capacitance is not defined for the JJ array
                            chip=p.chip,
                            gds_cell_name=p.gds_cell_jj_array)
        
        # Add the port lines if they exist
        if port_lines is not None:
            # If port_lines is a tuple, it means we have two lines for the flux bias line
            if isinstance(port_lines, tuple):
                # Add the port lines to the qgeometry
                self.add_pin('flux_in', port_lines[0].coords, p.cpw_width)  # flux bias line input
                self.add_pin('flux_out', port_lines[1].coords, p.cpw_width)  # flux bias line output
            else:
                # If port_lines is a single line, we add it as a single pin
                self.add_pin('flux_in', port_lines.coords, p.cpw_width)
        
    def make_resonator(self):
        """Creates the resonator for the fluxonium pocket. 
            Also, add the flux bias line for the fluxonium pocket.
        """
        p = self.parse_options()  # parse the options
        pres = self.p.resonator_options  # parser on resonator options
        pflux = self.p.flux_line_options  # parser on flux bias line options
        
        resonator_length = pres.resonator_length
        resonator_width = pres.resonator_width
        resonator_gap = pres.resonator_gap
        qubit_res_gap = pres.qubit_res_gap
        jj_array_width = pres.jj_array_width
        jj_dist = pres.jj_dist
        
        # Create the resonator as a rectangle with rounded corners
        # resonator = draw.rectangle(resonator_length, resonator_width, 2*p.pad_height+p.pad_gap+qubit_res_gap+resonator_length/2, 0, radius=qubit_res_gap)
        dist = resonator_length - resonator_width
        bound_1 = draw.Point((-dist/2, 2*p.pad_height+p.pad_gap+qubit_res_gap+resonator_width/2)).buffer(resonator_width/2, resolution=16)  # Create a rounded rectangle for the resonator
        bound_2 = copy.deepcopy(bound_1)  # Create a second rounded rectangle for the resonator
        bound_2 = draw.translate(bound_2, dist, 0)  # Translate the second rounded rectangle to the right
        
        # add rectangle to close the resonator
        close_resonator = draw.rectangle(dist, resonator_width, 0, 2*p.pad_height+p.pad_gap+qubit_res_gap+resonator_width/2)  # rectangle to close the resonator

        
        pad_1 = draw.union([bound_1, bound_2, close_resonator])  # union the two rounded rectangles and the rectangle to close the resonator bottom pad
        pad_2 = copy.deepcopy(pad_1)  # Create a second pad for the resonator
        pad_2 = draw.translate(pad_2, 0, resonator_gap + resonator_width)  # Translate the second pad to the top
        
        # add the pad for jj_arrays
        jj_pad_bottom = draw.rectangle(jj_dist + resonator_width/2, jj_array_width, resonator_length/2 + jj_dist/2 - resonator_width/4, 2*p.pad_height + p.pad_gap + qubit_res_gap + resonator_width/2)  # bottom pad for the JJ array
        # Add the jj array to make the inductance
        jj_x_point = resonator_length/2 + jj_dist - jj_array_width/2
        jj_y_point = 2*p.pad_height + p.pad_gap + qubit_res_gap + resonator_width/2
        jj_array = draw.LineString([(jj_x_point, jj_y_point + jj_array_width/2), (jj_x_point, jj_y_point + resonator_gap+ resonator_width - jj_array_width/2)])  # JJ array line
        
        jj_pad_top = copy.deepcopy(jj_pad_bottom)  # Create a second pad for the JJ array
        jj_pad_top = draw.translate(jj_pad_top, 0, resonator_gap + resonator_width)  # Translate the second pad to the top
        
        resonator = draw.union([pad_1, pad_2,jj_pad_bottom, jj_pad_top ])  # union the two pads for the resonator
        # translate to the center of the background pocket
        
        
        # Save the JJ point for use in the flux bias line as a tuple
        self.jj_point = (jj_x_point, jj_y_point)  # Save
        
        all_objects = [resonator, jj_array]
        # translate to the center of the background pocket
        total_y_distances = 2*p.pad_height + p.pad_gap + qubit_res_gap + 2*resonator_width + resonator_gap
        all_objects = draw.translate(all_objects, 0, -total_y_distances/2)  # translate the objects to the center of the background pocket
        
        # rotate the loop
        if p.loop_position == 'left':
            all_objects = draw.scale(all_objects, xfact=-1, yfact=1, origin=(0, 0))  # mirror the object to the left side of the pocket
        all_objects = draw.rotate(all_objects, p.orientation, origin=(0, 0))
        all_objects = draw.translate(all_objects, p.pos_x, p.pos_y)  # translate the object to the position defined by the user
        resonator, jj_array = all_objects
        
        # Add the resonator to the qgeometry
        self.add_qgeometry('poly', {'resonator': resonator}, chip=self.p.chip)
        
        # Add the JJ array as a junction geometry
        self.add_qgeometry('junction', {'jj_array': jj_array},
                            width=jj_array_width,
                            hfss_inductance = pres.L_res,
                            # hfss_capacitance = p.C_jj,  # capacitance is not defined for the JJ array
                            chip=p.chip,
                            gds_cell_name=p.gds_cell_jj_array)
    
    # def make_flux_bias_line(self):
    #     """Creates the flux bias line for the fluxonium pocket."""
    #     p = self.parse_options()
    #     pfbl = self.p.flux_line_options  # parser on flux bias line options
    #     pres = self.p.resonator_options
        
    #     # Flux line options
    #     total_length = pfbl.total_length
    #     width = pfbl.width
    #     wait_length = pfbl.wait_length
    #     adjust_length = pfbl.adjust_length
    #     pad_width = pfbl.pad_width
    #     pad_height = pfbl.pad_height
    #     pad_gap = pfbl.pad_gap
        
    #     # Position where strat the flux bias line
    #     x_pos, y_pos = self.jj_point  # Get the position of the JJ array
    #     thin_line = draw.rectangle(wait_length, pres.jj_array_width, x_pos + wait_length/2 + pres.jj_array_width/2, y_pos)
        
        
    #     all_objects = [thin_line]
        
    #     total_y_distances = 2*p.pad_height + p.pad_gap + pres.qubit_res_gap + 2*pres.resonator_width + pres.resonator_gap
    #     all_objects = draw.translate(all_objects, 0, -total_y_distances/2)
        
    #     # rotate the loop
    #     if p.loop_position == 'left':
    #         all_objects = draw.scale(all_objects, xfact=-1, yfact=1, origin=(0, 0))
    #     all_objects = draw.rotate(all_objects, p.orientation, origin=(0, 0))
    #     all_objects = draw.translate(all_objects, p.pos_x, p.pos_y)  # translate the object to the position defined by the user
    #     thin_line = all_objects[0]
        
    #     self.add_qgeometry('poly', {'thin_line': thin_line}, chip=p.chip)
        
        
        
        # Create the first part of the flux bias line
    
