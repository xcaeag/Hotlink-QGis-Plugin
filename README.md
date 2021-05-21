Hotlink-QGis-Plugin 
===================

Triggers [actions](https://docs.qgis.org/3.16/en/docs/training_manual/create_vector_data/actions.html) on single click

Purpose: To facilitate the use of actions attached to vector layers.

Principle: when the plugin is activated (button in the toolbar), the objects "carriers" of actions become "clickable". The associated action is triggered immediately if it is only. A list is available if necessary.
Tips are built from the layer properties (map tip display text option). Layer name + field are concatenated, or HTML version if defined as.

Two variables are available: @click_x and @click_y, last cursor position. These values can thus be passed as a parameter for a URL opening.  
Example of action : `http://my.url?x=[% @click_x %]`

Or a little more complicated, with coordinates transformation : `https://www.openstreetmap.org/#map=14/[% y(transform(make_point(@click_x,@click_y), @map_crs, 'EPSG:4326')) %]/[% x(transform(make_point(@click_x,@click_y), @map_crs, 'EPSG:4326')) %]
`


Attention : Since v0.7.7, Tips are not displayed because of conflict with default qgis map tip. To restore, change 'optionShowTips' variable in qgis.ini.

    [Hotlink]
    optionShowTips=true

Release on QGIS Python Plugins Repository : http://plugins.qgis.org/plugins/Hotlink/

Exemple :

![Exemple](./Hotlink/doc/combo.png)