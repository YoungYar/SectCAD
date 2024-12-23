<p>For example, below is a double-I section drawn:</p>

<img src="https://github.com/YoungYar/SectCAD/blob/master/double-I_section.gif?raw=true" alt="Double-I section" width="600"/>

<p>
After adding the I-sections and plates and then pressing the "Merge" button we got this:<br><br>
Final merged polygon(s) vertices:<br>
polygon #1:  [(8.5, 1.5), (2.5, 1.5), (2.5, 2.0), (2.0, 2.0), (2.0, 3.0), (3.0, 3.0), (3.0, 8.0), (2.0, 8.0), (2.0, 9.0), (2.5, 9.0), (2.5, 9.5), (8.5, 9.5), (8.5, 9.0), (9.0, 9.0), (9.0, 8.0), (8.0, 8.0), (8.0, 3.0), (9.0, 3.0), (9.0, 2.0), (8.5, 2.0), (8.5, 1.5)]<br>
  hole:  [(5.0, 8.0), (4.0, 8.0), (4.0, 3.0), (5.0, 3.0), (5.0, 2.0), (6.0, 2.0), (6.0, 3.0), (7.0, 3.0), (7.0, 8.0), (6.0, 8.0), (6.0, 9.0), (5.0, 9.0), (5.0, 8.0)]<br><br>
</p>

<p>
✅ Checked with Python version 3.12.8, matplotlib V.3.10.0, shapely V.2.0.6 and numpy V.2.2.1<br>
🔷 Use Spider IDE for ease of use.
</p>

<p>
Keys and button guidnace:
<ul>
<li>Click on the figure to create a polygon.</li>
<li>Press the "esc" key or "Start (or Clear) Selection" button to clear the current selection and start new selection.</li>
<li>Press the "Add Polygon (+)" button to save current the polygon selection.</li>
<li>Press the "Remove selected Area (-)" button to remove the intersection of the drawn polygon areas and the saved polygons.</li>
<li>Press the "Merge" button to merge overlapping saved (blue) polygons. This command reports the final shape vertices.</li>
<li>Try holding the "shift" key to move all of the vertices.</li>
<li>Try holding the "ctrl" key to move a single vertex.</li>
</ul>
</p>

<p>
Matplotlib control buttons are also available:<br>
<img src="https://github.com/YoungYar/SectCAD/blob/master/Matplotlib-control-buttons.png?raw=true" alt="Matplotlib control buttons"/>
</p>
