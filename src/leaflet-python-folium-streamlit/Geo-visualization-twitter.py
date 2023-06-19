import streamlit as st

from streamlit.components.v1 import html

import folium
from streamlit_folium import st_folium

from folium_vectorgrid import VectorGridProtobuf
from branca.element import Element
from folium.plugins import HeatMap

from jinja2 import Template

import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import urllib
import json


st.title("Folium test")

cols = st.columns(3)
with cols[0]:
	show_blue = st.checkbox("Show blue marker", value=True)
with cols[1]:
	show_green = st.checkbox("Show green marker", value=True)
with cols[2]:
	show_red = st.checkbox("Show red marker", value=False)
 
# heatmap load from server
def fill_URL(i):
    return 'http://docker.ilab.sztaki.hu:49158/geoserver/twitter-trekking/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=twitter-trekking%3Aeurope_' + str(i) + '&outputFormat=application%2Fjson'
    # query in EPSG:900913
    # return 'http://docker.ilab.sztaki.hu:49158/geoserver/twitter-trekking/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=twitter-trekking%3Aeurope_' + str(i) + '&srsName=EPSG%3A900913&outputFormat=application%2Fjson'


def load_heatmapData_from_server(url_func = fill_URL):
    # l[::-1] means reversed list like list(reversed(l)) but faster
    europ_collections_dict = {str(i):[feature['geometry']['coordinates'][::-1] for feature in json.loads(urllib.request.urlopen(url_func(i)).read().decode('utf-8'))['features']] for i in range(0, 4)}
    europ_collections_dict["all"] = [feature['geometry']['coordinates'][::-1] for feature in json.loads(urllib.request.urlopen(url_func('all')).read().decode('utf-8'))['features']]

    return europ_collections_dict

# heatmap data from csv
def load_heatmapData_from_csv(csvPath = "../tweets_with_user_info.csv"):
    latlong_df = pd.read_csv(csvPath, usecols = ['lat', 'lng', 'osm_label'])

    europ = Polygon([(-16.1, 32.88), (-16.1, 84.73), (40.18, 84.73), (40.18, 32.88)])

    europ_collection = [x for x in latlong_df.values if europ.contains(Point((x[1], x[0])))]

    europ_collections_dict = {str(i):list(filter(lambda x: x[2] == i, europ_collection)) for i in range(0, 4)}
    europ_collections_dict["all"] = europ_collection

    return europ_collections_dict

loadDataFromServer = True

europ_collections_dict = load_heatmapData_from_server() if loadDataFromServer else load_heatmapData_from_csv()
# check counts
# for key, value in europ_collections_dict.items():
#     print("collection "+ key + "  size " + str(len(value)))

template = Template(
        """
        {% macro header(this, kwargs) %}
            <meta name="viewport" content="width=device-width,
                initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
            <style>
                #{{ this.get_name() }} {
                    position: {{this.position}};
                    width: {{this.width[0]}}{{this.width[1]}};
                    height: {{this.height[0]}}{{this.height[1]}};
                    left: {{this.left[0]}}{{this.left[1]}};
                    top: {{this.top[0]}}{{this.top[1]}};
                }
                .leaflet-container { font-size: 1rem; }
            </style>
        {% endmacro %}

        {% macro html(this, kwargs) %}
            <div class="container-fluid">
              <div class="row footer0" style="height:60px;"></div>
              <div class="row header0">
                  <h1>
                    <!-- <img src="./hikerpicto.svg" class="hikerpicto"> Közösségimédia-alapú látogatómonitoring  -->
                    <img src="https://info.ilab.sztaki.hu/~lukacsg/hikerpicto.svg" class="hikerpicto"> Közösségimédia-alapú látogatómonitoring 
                    <span style="float:right">
                        <img src="https://github.com/lukacsg/openlostcat/blob/master/openlostcat_logo.png?raw=true" height="70"> 
                        <img src="https://poltextlab.com/wp-content/uploads/2021/02/milab_logo_en.png" height="70">
                        <img src="https://www.i40platform.hu/sites/default/files/i40platform/2021-02/sztaki_logo_2019_uj_feher_svg_0.svg" height="70">
                    </span>
                  </h1>
              </div>
              <div class="row footer0" style="height:30px;"></div>
              <div class="row content">
                <div class="col-sm-3 sidenav">
                  <hr>
                  <h4>Helyszín megközelíthetőségi típus rétegek </h4>
                  <ul class="nav nav-pills nav-stacked">
                    <li id="layer-link-all" class="active"><a href="javascript:;">Bármely típusú helyszín</a></li>
                    <li id="layer-link-0"><a href="javascript:;">Turistaúton vagy közlekedéssel megközelíthető helyek</a></li>
                    <li id="layer-link-1"><a href="javascript:;">Közlekedéssel megközelíthető helyek</a></li>
                    <li id="layer-link-2"><a href="javascript:;">Kijelölt turistaúton megközelíthető helyek</a></li>
                    <li id="layer-link-3"><a href="javascript:;">Kijelölt turistaút nélküli terep</a></li>
                  </ul>
                  <hr>
                  <h4>Utazási távolságok (szín és méret)</h4>
                  <ul class="nav nav-pills nav-stacked">
                    <li><a><span class="dot" style="background-color:#00ff00;"></span> 0 - 10 km</a></li>
                    <li><a><span class="dot" style="background-color:#66ff00;"></span> 10 - 60 km</a></li>
                    <li><a><span class="dot" style="background-color:#ccff00;"></span> 60 - 500 km</a></li>
                    <li><a><span class="dot" style="background-color:#ffcc00;"></span> 500 - 4000 km</a></li>
                    <li><a><span class="dot" style="background-color:#ff6600;"></span> 4000 - 20000 km</a></li>
                  </ul>
                  <hr>
                  <h4>Látogatás ideje (átlátszóság)</h4>
                  <ul class="nav nav-pills nav-stacked">
                    <li><a><span class="dot" style="background-color:#b3b3b3;"></span> 2020.aug-nov.</a></li>
                    <li><a><span class="dot" style="background-color:#8d8d8d;"></span> 2020.dec-2021.febr.</a></li>
                    <li><a><span class="dot" style="background-color:#666666;"></span> 2021.márc-máj.</a></li>
                    <li><a><span class="dot" style="background-color:#404040;"></span> 2021.jún-aug.</a></li>
                    <li><a><span class="dot" style="background-color:#1a1a1a;"></span> 2021.szept-nov.</a></li>
                  </ul>
                </div>

                <div class="col-sm-9">
                  <div class="folium-map map" id={{ this.get_name()|tojson }} ></div>
                  <p id="info">Initializing...</p>
                  </div>
                </div>
              </div>
            </div>

            <footer class="container-fluid footer0">
            Hivatkozások:
            <ul>
            <li>
              Cikk: <a href="https://eprints.sztaki.hu/10396/" target="_blank">Béres, Ferenc and Lukács, Gábor and Molnár, András József and Szeiler, P (2022) An Exploratory Survey of Recreational Activities Using Twitter Data with Logic-Based Location Categorization. KIEL COMPUTER SCIENCE SERIES, 2022 (3). pp. 51-71. ISSN 2193-6781 10.21941/kcss/2022/3</a>
            </li>
            <li>
              Helyszínkategorizáló eszköz (saját fejlesztés): <a href="https://github.com/lukacsg/openlostcat" target="_blank">OpenLostCat - A Location Categorizer Based on OpenStreetMap</a>
            <li>Térképi adatok: © <a href="https://www.openstreetmap.org">OpenStreetMap</a> licensz: <a href="https://www.openstreetmap.org/copyright">ODbL</a>. Turistautak réteg: <a href="https://hiking.waymarkedtrails.org">WaymarkedTrails by lonvia</a>. Alaptérkép: <a href="https://opentopomap.org/">OpenTopoMap</a>(<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-by-SA</a>). Domborzat: <a href="help/acknowledgements">SRTM/ASTER</a>.
            </li>
            </ul>
            </footer>
        {% endmacro %}

        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.map(
                {{ this.get_name()|tojson }},
                {
                    center: {{ this.location|tojson }},
                    crs: L.CRS.{{ this.crs }},
                    {%- for key, value in this.options.items() %}
                    {{ key }}: {{ value|tojson }},
                    {%- endfor %}
                }
            );

            {%- if this.control_scale %}
            L.control.scale().addTo({{ this.get_name() }});
            {%- endif %}

            {% if this.objects_to_stay_in_front %}
            function objects_in_front() {
                {%- for obj in this.objects_to_stay_in_front %}
                    {{ obj.get_name() }}.bringToFront();
                {%- endfor %}
            };
            {{ this.get_name() }}.on("overlayadd", objects_in_front);
            $(document).ready(objects_in_front);
            {%- endif %}

        {% endmacro %}
        """
    )

 
# from pyproj import Transformer   
    
geoserver_docker_base_url = 'http://docker.ilab.sztaki.hu:49158/geoserver/gwc/service/tms/1.0.0/';
geoserver_heat_base_url = 'http://docker.ilab.sztaki.hu:49158/geoserver/twitter-trekking/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=';
geoserver_layer_name = 'twitter-trekking:europe_';
geoserver_layer_name_heat = 'twitter-trekking%3Aeurope_';

projection_epsg_no = '900913';

m = folium.Map(# location=list(Transformer.from_crs("EPSG:4326", "EPSG:3857").transform(19.9496, 49.2992)), zoom_start=5)
                crd='EPSG:900913',
               location=(45.9496, 25.2992), zoom_start=5)

# update template
m._template = template

folium.map.CustomPane(name='heatmap', z_index=401, pointer_events=False).add_to(m)

folium.TileLayer(
        tiles='http://tile.waymarkedtrails.org/hiking/{z}/{x}/{y}.png',
        name='waymarkedtrails',
        attr='attribution',
        overlay=True, control=False,
        opacity=.5
    ).add_to(m)

HeatMap.default_js = [
        (
            'leaflet-heat.js',
            'https://info.ilab.sztaki.hu/~lukacsg/leaflet_heat.min.js',
        )
    ]

# hack: fix a bug in the Leaflet.VectorGrid which is used by folium_vectorgrid, upload to info and set the fixed version to use in VectorGridProtobuf.
VectorGridProtobuf.default_js = [
        (
            "vectorGrid",
            "https://info.ilab.sztaki.hu/~lukacsg/Leaflet.VectorGrid.bundled23.js",
        )
    ]

# option for VectorGridProtobuf:
# - interactive option must be true to be able to handle mouse events
# - vectorTileLayerStyles must contain the vectortile layer name that comes from the server. See url.
# - getFeatureId function sholud be implemented if individual style setting is requred with function: setFeatureStyle(id, style), resetFeatureStyle(id)
# - bubblingMouseEvents stop (mouse) event propagationing / it is nor working use this in the event function: L.DomEvent.stopPropagation(event);
options = '''{"interactive": true, 
           "vectorTileLayerStyles": { 
                "geojson": function(properties, zoom) {
                                var distanceCategory = properties.logdistance;
                                var dateCategory = properties.datecategory;
                                return {
                                  "radius": 20 + distanceCategory * 2,                                  
                                  "fillColor": "#000000",
                                  "fillOpacity": .3 + .15*dateCategory,
                                  "color": "#" + (1 << 24 | (Math.min(distanceCategory*102, 255)) << 16 | (Math.min((5 - distanceCategory)*102, 255)) << 8 | 0).toString(16).slice(1),
                                  "opacity": .3 + .15*dateCategory,
                                  "fill": true,
                                  "weight": 1 + distanceCategory * 2,
                                  "stroke": true
                                }
                            }
           },
           "getFeatureId": function(f) {
            return f.properties.id;
           },
           minZoom: 9,
           bubblingMouseEvents: false,
           zIndex: 999
          }'''

featureGroups = []
def createGeoJsonVectorGrid(i, show=False):
    # fg = featureGroups.append(folium.map.FeatureGroup('category-' + str(i), overlay=True, control=True, show=False))
    fg = folium.map.FeatureGroup("<img src='https://info.ilab.sztaki.hu/~lukacsg/hikerpicto.svg' class='hikerpicto' /><strong>category-" + str(i) + "</strong>", overlay=True, control=True, show=show)
    vg = VectorGridProtobuf(geoserver_docker_base_url + geoserver_layer_name + str(i) + '@EPSG%3A' + projection_epsg_no + '@geojson/{z}/{x}/{-y}.geojson', "category-" + str(i), options)
    vg.add_to(fg)
    HeatMap(europ_collections_dict[str(i)], name="heat-" + str(i), min_opacity=0.5, max_zoom=9, max_zoom_v=9, pane='heatmap').add_to(fg)
    featureGroups.append(fg)
    return vg

vgl = list(map(createGeoJsonVectorGrid, range(4)))
vgl.append(createGeoJsonVectorGrid("all", show=True))
for fg in  featureGroups:
    m.add_child(fg)

# must render the map to generate the js scprit and htlm which can be altered than like extend script, add style and htlm elements.
m.render()

# get the map variable name from js to refeer it
mapo = m.get_name()
# get the VectorGridProtobuf variable name from js to refeer it
vglname = [v.get_name() for v in vgl]

# extends js script with:
# - VectorGridProtobuf click event
# - base map click event
# functionility:
# - hightlight point if clicked
# - display poperties of the point in an info panel on the map
def onClickEventStr(vgName):
    return vgName + '''.on('click', function (e) {
            if (id >= 0) {
                actualLayer.resetFeatureStyle(id);
            }
            id = e.layer.properties.id;
            '''+ vgName + '''.setFeatureStyle(id, selectedStyle)
           actualLayer = ''' + vgName + '''
           
           L.DomEvent.stopPropagation(e);
           
            info.style.opacity = 1; 
            info.innerHTML = 
             '<strong>Date:</strong> <span class="datetime">' + e.layer.properties.dt + '</span><br>' +
             '<strong>User name:</strong> ' + e.layer.properties.screen_name+ '<br>' +
             '<strong>User from:</strong> ' + e.layer.user_from + '<br>' +
             //'<strong>User distance:</strong> ' + Math.round(e.layer.properties.distance) + '<br>' +
             '<strong>Text:</strong>' + e.layer.properties.text + '<br>'+
             '<strong>User url:</strong> <a href="' + e.layer.properties.url + '">' + e.layer.properties.url + '</a><br>';
          });
          
          '''

on_click_js = '''var info = document.getElementById('info');
           var id = -1;
           var actualLayer;
           const selectedStyle = {
              radius: 10,
              fillColor: "green",
              fillOpacity: 1,
              color: "yellow",
              fill: true,
              weight: 1.5,
              stroke: false
           }
           
            ''' + ''.join(map(lambda name: onClickEventStr(name), vglname)) + mapo + '''.on('click', function (event) {
             if (id >= 0) {
                actualLayer.resetFeatureStyle(id);
             }
             
             info.innerText = "Choose a point!";
             info.style.opacity = .5;
           });         
'''

fgNames = list(map(lambda fg: fg.get_name(), featureGroups))
buttonToFg = {'b'+str(i):fgNames[i] for i in range(0, 4)}
buttonToFg['ball'] = fgNames[4]

def buttonsClickEventStr(buttonName, featuregroup):
    return buttonName + '.addEventListener("click", function() {onClickButton(' +  buttonName + ', ' + featuregroup + ');});'

button_listeners = '''
        var ball = document.getElementById('layer-link-all');
        var b0 = document.getElementById('layer-link-0');
        var b1 = document.getElementById('layer-link-1');
        var b2 = document.getElementById('layer-link-2');
        var b3 = document.getElementById('layer-link-3');
        
        function buttonSelect(buttonSelected) {
            buttonSelected.classList.add('active');
            for (const b of [ball, b0, b1, b2, b3]) {
                if (b !== buttonSelected) {
                   b.classList.remove('active');
                }
            }         
        }
        
        function layerSelect(fgSelected) {
            ''' + mapo + '''.addLayer(fgSelected);
            for (const fg of [''' + ', '.join(fgNames) + ''']) {
                if (fg !== fgSelected) {
                   ''' + mapo + '''.removeLayer(fg);
                }
            }
        }
        
        function onClickButton(button, feautrGroup) {
            buttonSelect(button);
            layerSelect(feautrGroup);
        }
        
''' + ''.join(map(lambda i: buttonsClickEventStr(i[0], i[1]), buttonToFg.items()))

# extends generated js script 
m.get_root().script.add_child(Element(on_click_js + button_listeners))

# add style element to pregenerated html which can be refereed in the js script
m.get_root().header.add_child(folium.Element(
'''
<style>
    .row.content {height: auto}
    
    .dot {
      height: 25px;
      width: 25px;
      background-color: #bbb;
      border-radius: 50%;
      display: inline-block;
      vertical-align: middle;
    }
    .hikerpicto {
      height: 75px;
      width: 75px;
      display: inline-block;
      vertical-align: middle;
    }

        
    /* Style the header */
    .header0 {
      background-color: #ffffff;
      padding: 15px;
      text-align: left;
      font-size: 50px;
      color: #073c79;
    }
    
    .header0 h1 {
      font-size: 50px;
    }
    
    .header0 .logo {
      float: right;
    }

    /* Set black background color, white text and some padding */
    .footer0 {
      position: relative;
      background-color: #073c79;
      color: white;
      padding: 15px;
    }
    
    footer a {
        color: white;
    }
    
    footer a:hover {
        color: #dddddd;
    }

    /* On small screens, set height to 'auto' for sidenav and grid */
    @media screen and (max-width: 767px) {
      .sidenav {
        height: auto;
        padding: 15px;
      }
      .row.content {height: auto;} 
    }
  
  
    html, body {
      font-family: sans-serif;
    }

    #info {
        z-index: 999;
        opacity: 0.5;
        position: absolute;
        bottom: 0;
        left: 15px;
        margin: 0;
        padding: 15px;
        background: rgba(0,60,136,0.7);
        color: white;
        border: 0;
        transition: opacity 100ms ease-in;
    }
    strong {
        color: LightBlue;
    }
    .datetime {
        font-family: monospace;
    }
    .place-name {
        color: LightGreen;
    }
    ul li {
    width: 100%;
    min-width: 100%;
  }
  </style>
'''
))


# show map
# st_folium(m, width=725)
# use the folium generated html instead of above to keep the script too
html(m.get_root()._repr_html_(), width=2100, height=2200, scrolling=True)
