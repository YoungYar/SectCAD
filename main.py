# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 03:03:23 2024

@author: YoungYar
"""

import matplotlib.pyplot as plt
from matplotlib.widgets import PolygonSelector, Slider, Button
import numpy as np
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.ops import unary_union
from shapely.validation import make_valid
from matplotlib.patches import Polygon
from matplotlib.backend_bases import KeyEvent
import matplotlib.patches as mpatches

class SnappingPolygonSelector(PolygonSelector):
    def __init__(self, ax, grid_spacing_x=1, grid_spacing_y=1, **kwargs):
        self.grid_spacing_x = grid_spacing_x
        self.grid_spacing_y = grid_spacing_y
        self.snapped_verts = []  # List to store snapped vertices
        self.saved_polygons = []  # List to store all saved polygons
        self.current_polygon = []  # List to store vertices of the current polygon
        self.red_polygon = None  # Variable to store the red polygon
        super().__init__(ax, self.onselect, **kwargs)
        self.update_grid_lines()  # Initialize grid lines

    def onmove(self, event):
        """Cursor move event handler and validator with snapping to grid."""
        if not self.ignore(event):
            event = self._clean_event(event)
            if event.xdata is not None and event.ydata is not None:
                # Snap the mouse position to the nearest grid point
                event.xdata, event.ydata = self.snap_to_grid(event.xdata, event.ydata)
            self._onmove(event)
            return True
        return False

    def snap_to_grid(self, x, y):
        """Snap the (x, y) position to the nearest grid point."""
        if np.isfinite(x) and np.isfinite(y):
            snap_x = round(x / self.grid_spacing_x) * self.grid_spacing_x
            snap_y = round(y / self.grid_spacing_y) * self.grid_spacing_y
            return snap_x, snap_y
        return x, y

    def _release(self, event):
        """Override the _release method to save snapped vertices."""
        if event.xdata is not None and event.ydata is not None:
            if np.isfinite(event.xdata) and np.isfinite(event.ydata):
                snapped_vertex = self.snap_to_grid(event.xdata, event.ydata)
                # Ensure the vertex is snapped correctly
                self.current_polygon.append(snapped_vertex)
                # Directly set event.xdata and event.ydata to the snapped coordinates
                event.xdata, event.ydata = snapped_vertex
        super()._release(event)

    def onselect(self, verts):
        """Handle selection of polygon vertices."""
        # Snap vertices to grid
        self.current_polygon = [self.snap_to_grid(x, y) for x, y in verts]
        print("Selected vertices:", self.current_polygon)

    def update_grid_lines(self):
        """Update grid lines based on current view limits and spacing."""
        if self.grid_spacing_x <= 0 or self.grid_spacing_y <= 0:
            return

        # Get current limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        # Generate grid lines
        ticks_x = np.arange(np.floor(xlim[0] / self.grid_spacing_x) * self.grid_spacing_x,
                            np.ceil(xlim[1] / self.grid_spacing_x) * self.grid_spacing_x + self.grid_spacing_x,
                            self.grid_spacing_x)
        ticks_y = np.arange(np.floor(ylim[0] / self.grid_spacing_y) * self.grid_spacing_y,
                            np.ceil(ylim[1] / self.grid_spacing_y) * self.grid_spacing_y + self.grid_spacing_y,
                            self.grid_spacing_y)

        ax.set_xticks(ticks_x)
        ax.set_yticks(ticks_y)
        ax.grid(True)
        fig.canvas.draw_idle()

    def save_polygon(self):
        """Save the current polygon and clear current vertices for new drawing."""
        if self.current_polygon:
            self.saved_polygons.append((self.current_polygon.copy(), []))  # Copy to avoid reference issues
            print("Polygon saved:", self.current_polygon)
            self.current_polygon = []
            self.update_plot()
            self.trigger_escape()  # Simulate pressing the 'esc' key

    def update_plot(self):
        """Update the plot with saved polygons and clear current drawing."""
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()

        ax.clear()

        # Redraw saved polygons
        for exterior, interiors in self.saved_polygons:
            if len(exterior) > 2:  # Ensure there are enough points to form a polygon
                poly = Polygon(exterior, closed=True, edgecolor='blue', facecolor='cyan', alpha=0.3)
                ax.add_patch(poly)
                for interior in interiors:
                    hole = Polygon(interior, closed=True, edgecolor='blue', facecolor='white', alpha=1.0)
                    ax.add_patch(hole)

        # Draw the red polygon if it exists
        if self.red_polygon:
            red_poly = Polygon(self.red_polygon, closed=True, edgecolor='red', facecolor='red', alpha=0.5)
            ax.add_patch(red_poly)

        # Restore axis limits
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        # Redraw grid with updated spacing
        self.update_grid_lines()

        fig.canvas.draw_idle()

    def trigger_escape(self):
        """Trigger the 'escape' key event programmatically."""
        event = KeyEvent(name='key_press_event', canvas=fig.canvas, key='escape')
        fig.canvas.callbacks.process(event.name, event)

    def reset(self):
        """Reset the entire drawing, clearing all saved polygons, current polygon, and red polygon."""
        self.saved_polygons = []
        self.current_polygon = []
        self.red_polygon = None
        self.update_plot()  # Update plot to clear all shapes

    def draw_red_polygon(self):
        """Draw a red polygon and remove intersections with saved polygons."""
        if self.current_polygon:
            self.red_polygon = self.current_polygon.copy()
            self.current_polygon = []
            # Create a shapely Polygon for the red polygon
            red_polygon = ShapelyPolygon(self.red_polygon)

            # Check if the red polygon is valid
            if not red_polygon.is_valid:
                print("Error: The red polygon is not valid!")
                ax.set_title('The selection is not valid! Please adjust the shape.',
                             bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
                             loc='center', pad=15)
                fig.canvas.draw_idle()
                return

            remaining_polygons = []

            for polygon in self.saved_polygons:
                # Create a shapely Polygon for the saved polygon
                saved_polygon = ShapelyPolygon(polygon[0], polygon[1])

                # Check if the saved polygon is valid
                if not saved_polygon.is_valid:
                    print("Error: A saved polygon is not valid!")
                    ax.set_title('A saved polygon is not valid! Please fix it.',
                                 bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
                                 loc='center', pad=15)
                    fig.canvas.draw_idle()
                    return

                try:
                    if saved_polygon.contains(red_polygon) or saved_polygon.intersects(red_polygon):
                        # Compute the difference to remove the intersection area
                        new_polygon = saved_polygon.difference(red_polygon)
                        if not new_polygon.is_empty:
                            if new_polygon.geom_type == 'Polygon':
                                remaining_polygons.append((list(new_polygon.exterior.coords), [list(interior.coords) for interior in new_polygon.interiors]))
                            elif new_polygon.geom_type == 'MultiPolygon':
                                for part in new_polygon.geoms:
                                    remaining_polygons.append((list(part.exterior.coords), [list(interior.coords) for interior in part.interiors]))
                    else:
                        remaining_polygons.append((list(saved_polygon.exterior.coords), [list(interior.coords) for interior in saved_polygon.interiors]))

                except Exception as e:
                    print("Error:", e)
                    ax.set_title('An error occurred while processing the polygons.',
                                 bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
                                 loc='center', pad=15)
                    fig.canvas.draw_idle()
                    return

            # Update saved polygons list
            self.saved_polygons = remaining_polygons

            # Update plot with the modified polygons
            self.update_plot()

    def merge_polygons(self):
        """Merge overlapping blue polygons while retaining holes."""
        if self.saved_polygons:
            # Convert all saved polygons to shapely objects
            shapely_polygons = [ShapelyPolygon(polygon[0], polygon[1]) for polygon in self.saved_polygons]

            # Validate and fix any invalid geometries
            shapely_polygons = [make_valid(polygon) for polygon in shapely_polygons]
            # Use unary_union to merge overlapping polygons
            merged_polygon = unary_union(shapely_polygons)

            # Update saved polygons with the merged result
            self.saved_polygons = []
            if merged_polygon.geom_type == 'Polygon':
                self.saved_polygons.append((list(merged_polygon.exterior.coords), [list(interior.coords) for interior in merged_polygon.interiors]))
            elif merged_polygon.geom_type == 'MultiPolygon':
                for poly in merged_polygon.geoms:
                    self.saved_polygons.append((list(poly.exterior.coords), [list(interior.coords) for interior in poly.interiors]))

            # Print the vertices of the final merged polygon(s)
            print("Final merged polygon(s) vertices:")
            for count, (exterior, interiors) in enumerate(self.saved_polygons):
                print(f'polygon #{count+1}: ', exterior)
                for interior in interiors:
                    print(f'  hole: ', interior)

            self.update_plot()

def update_grid(val):
    """Update the grid spacing based on slider values."""
    grid_spacing_x = round(slider_x.val, 1)
    grid_spacing_y = round(slider_y.val, 1)
    selector.grid_spacing_x = grid_spacing_x
    selector.grid_spacing_y = grid_spacing_y
    selector.update_grid_lines()

def on_save(event):
    """Handle the save button click."""
    selector.red_polygon = None
    selector.save_polygon()

def on_clear(event):
    """Handle the clear button click."""
    selector.current_polygon = []  # Clear the current polygon
    selector.red_polygon = None  # Clear the red polygon
    selector.update_plot()
    selector.trigger_escape()

def on_reset(event):
    """Handle the reset button click."""
    selector.reset()
    selector.trigger_escape()

def on_draw_red_polygon(event):
    """Handle the draw red polygon button click."""
    selector.draw_red_polygon()
    # if direct_remove:
    on_clear(event)

def on_merge(event):
    """Handle the merge polygons button click."""
    selector.merge_polygons()

def on_key(event):
    """Handle key events."""
    if event.key == 'escape':
        selector.current_polygon = []
        selector.update_plot()

# Create figure and axis
fig, ax = plt.subplots(figsize=(7, 7))
plt.subplots_adjust(left=0.2, bottom=0.3)

# Initial grid settings
initial_grid_spacing_x = 1
initial_grid_spacing_y = 1

# Set initial grid with correct spacing
ax.set_xticks(np.arange(0, 10 + initial_grid_spacing_x, initial_grid_spacing_x))
ax.set_yticks(np.arange(0, 10 + initial_grid_spacing_y, initial_grid_spacing_y))
plt.grid(color='grey', linestyle='-', linewidth=0.5, which='both')

# Create the custom SnappingPolygonSelector
selector = SnappingPolygonSelector(ax, grid_spacing_x=initial_grid_spacing_x, grid_spacing_y=initial_grid_spacing_y, useblit=True, grab_range=15, draw_bounding_box=False)

left_padding = 0

# Add sliders for adjusting grid spacing
ax_slider_x = plt.axes([left_padding+0.22, 0.2, 0.65, 0.03], facecolor='lightgoldenrodyellow')
ax_slider_y = plt.axes([left_padding+0.22, 0.15, 0.65, 0.03], facecolor='lightgoldenrodyellow')

slider_x = Slider(ax_slider_x, 'Grid X Spacing', 0.5, 10.0, valinit=initial_grid_spacing_x, valstep=0.5)
slider_y = Slider(ax_slider_y, 'Grid Y Spacing', 0.5, 10.0, valinit=initial_grid_spacing_y, valstep=0.5)

slider_x.on_changed(update_grid)
slider_y.on_changed(update_grid)


# Add a button for clearing the red polygon
ax_clear_button = plt.axes([left_padding+0.01, 0.07, 0.26, 0.04], facecolor='lightgoldenrodyellow')
button_clear = Button(ax_clear_button, 'Start (or Clear) Selection', color='darkslategray', hovercolor='black')
button_clear.label.set_color('white')
button_clear.on_clicked(on_clear)

# Add a button for saving the polygon
ax_save_button = plt.axes([left_padding+0.28, 0.07, 0.2, 0.04], facecolor='lightgoldenrodyellow')
button_save = Button(ax_save_button, 'Add Polygon (+)', color='aqua')
button_save.on_clicked(on_save)

# Add a button for drawing the red polygon
ax_remove_button = plt.axes([left_padding+0.49, 0.07, 0.27, 0.04], facecolor='lightgoldenrodyellow')
button_remove = Button(ax_remove_button, 'Remove selected Area (-)', color='crimson', hovercolor='black')
button_remove.label.set_color('white')
button_remove.on_clicked(on_draw_red_polygon)

# Add a button for clearing all drawings
ax_reset_button = plt.axes([left_padding+0.77, 0.07, 0.1, 0.04], facecolor='lightgoldenrodyellow')
button_reset = Button(ax_reset_button, 'Reset', color='lawngreen', )
button_reset.on_clicked(on_reset)

# Add a button for merging overlapping polygons
ax_merge_button = plt.axes([left_padding+0.88, 0.07, 0.1, 0.04], facecolor='lightgoldenrodyellow')
button_merge = Button(ax_merge_button, 'Merge', color='orange')
button_merge.on_clicked(on_merge)

# Connect the key press event
fig.canvas.mpl_connect('key_press_event', on_key)

print("- Click on the figure to create a polygon.")
print("- Press 'esc' key or 'Start (or Clear) Selection' button to clear the current selection and start new selection.")
print("- Press 'Add Polygon (+)' button to save current the polygon selection.")
print("- Press 'Remove selected Area (-)' button to draw a red polygon and remove intersections with saved polygons.")
print("- Press 'Merge' button to merge overlapping saved (blue) polygons. This command reports the final shape vertices.")
print("- Try holding the 'shift' key to move all of the vertices.")
print("- Try holding the 'ctrl' key to move a single vertex.")
