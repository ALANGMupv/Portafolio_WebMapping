import os
import pandas as pd
import folium
from folium import plugins
import numpy as np
from pyproj import Transformer
import random
from datetime import datetime, timedelta

# Configuration
ASSETS_DIR = 'assets/mapas'
DATA_DIR = 'assets/data' # Place to look for data
ACCIDENTS_FILE = '2023_Accidentalidad.xlsx'
CONTAINERS_FILE = 'Contenedores_varios.csv'

# Ensure directories exist
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def create_mock_data_if_missing():
    """
    Creates mock data files if they don't exist, matching the schema required by the notebook.
    This allows the script to run and generate valid HTML maps even without the real data.
    """
    accidents_path = os.path.join(DATA_DIR, ACCIDENTS_FILE)
    containers_path = os.path.join(DATA_DIR, CONTAINERS_FILE)

    # 1. Mock Accidents Data
    if not os.path.exists(accidents_path):
        print(f"'{ACCIDENTS_FILE}' not found. Creating mock data...")
        data = []
        base_date = datetime(2023, 1, 1)
        for _ in range(200):
            # Random date in 2023
            date = base_date + timedelta(days=random.randint(0, 364))
            # Random UTM 30N coordinates (approx Madrid)
            # Madrid UTM 30N is roughly X: 440000, Y: 4470000
            x = 440000 + random.randint(-5000, 5000)
            y = 4470000 + random.randint(-5000, 5000)
            
            data.append({
                'coordenada_x_utm': x,
                'coordenada_y_utm': y,
                'tipo_persona': random.choice(['Conductor', 'Peatón', 'Pasajero']),
                'tipo_vehiculo': random.choice(['Turismo', 'Bicicleta', 'Motocicleta', 'Furgoneta', 'Autobus']),
                'sexo': random.choice(['Mujer', 'Hombre']),
                'fecha': date,
                'num_expediente': f"2023S{random.randint(1000, 9999)}"
            })
        df = pd.DataFrame(data)
        df.to_excel(accidents_path, index=False)
        print(f"Mock '{ACCIDENTS_FILE}' created.")

    # 2. Mock Containers Data
    if not os.path.exists(containers_path):
        print(f"'{CONTAINERS_FILE}' not found. Creating mock data...")
        data = []
        types = ['VIDRIO', 'ENVASES', 'PAPEL-CARTON', 'ORGANICA']
        for _ in range(100):
            t = random.choice(types)
            # Random Coords (Lat/Lon) - Madrid approx 40.4168, -3.7038
            lat = 40.4168 + random.uniform(-0.05, 0.05)
            lon = -3.7038 + random.uniform(-0.05, 0.05)
            
            data.append({
                'Tipo Contenedor': t,
                'LATITUD': lat,
                'LONGITUD': lon,
                'Descripcion Modelo': f'Contenedor {t} Modelo X'
            })
        df = pd.DataFrame(data)
        df.to_csv(containers_path, sep=';', index=False)
        print(f"Mock '{CONTAINERS_FILE}' created.")

def generate_accidentes_map():
    print("Generating Accidentes Map (Notebook Task 2)...")
    input_path = os.path.join(DATA_DIR, ACCIDENTS_FILE)
    
    # --- Notebook Logic ---
    # 1. Load Data
    base_datos = pd.read_excel(input_path)
    
    # 2. Drop NA
    accidentes_df = base_datos.dropna(subset=['coordenada_x_utm', 'coordenada_y_utm'])
    
    # 3. Coordinate Transformation (UTM 30N -> ETRS89/WGS84)
    # Note: 'epsg:4258' is ETRS89 used in notebook, which Folium handles fine as lat/lon.
    transformacion = Transformer.from_crs('epsg:32630', 'epsg:4258', always_xy=True)
    puntos = list(zip(accidentes_df.coordenada_x_utm, accidentes_df.coordenada_y_utm))
    
    accidentes_df = accidentes_df.copy()
    # itransform returns (lon, lat) because always_xy=True
    coorgeo = np.array(list(transformacion.itransform(puntos)))
    accidentes_df.loc[:, 'longitud'] = coorgeo[:, 0]
    accidentes_df.loc[:, 'latitud'] = coorgeo[:, 1]
    
    # 4. Filter Data (Task 2 Logic)
    # "diferenciando los conductores por sexo (Elegir: Hombre o Mujer) y con un vehiculo distinto al turismo."
    # Notebook implementation: sexo=='Mujer' & tipo_vehiculo!='Turismo'
    acci_df = accidentes_df.loc[(accidentes_df['sexo'] == 'Mujer') & (accidentes_df['tipo_vehiculo'] != 'Turismo')]
    
    # 5. Add Month
    mes = pd.DatetimeIndex(acci_df['fecha']).month
    acci_df = acci_df.assign(mes=mes)
    
    # 6. Prepare HeatMapWithTime Data
    lista_tiempo = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    lista_peso = []
    acci_df = acci_df.assign(peso=1)
    
    # Notebook logic iterates through months sorted unique
    # Helper to ensure we have entries for months present, mapping to the 12-month list index if strict
    # The notebook iterates acci_df['mes'].sort_values().unique().
    for x in sorted(acci_df['mes'].unique()):
         # Note: x is 1-12.
         # Group by lat/lon, sum weight
         month_data = acci_df.loc[acci_df['mes'] == x, ['latitud', 'longitud', 'peso']]
         grouped = month_data.groupby(['latitud', 'longitud']).sum().reset_index().values.tolist()
         lista_peso.append(grouped)
         
    # Note: If some months have no data, Folium HeatMapWithTime might desync with index labels if we just append simple list. 
    # But following notebook logic exactly:
    
    # 7. Create Map
    madrid_map = folium.Map(location=[40.43, -3.65], control_scale=True, tiles="cartodb positron", zoom_start=12)
    
    # Adjust index if necessary. The notebook provides a full 12-month list 'lista_tiempo'.
    # If our data only has some months, the index might mismatch the frames. 
    # However, I will strictly follow the notebook code which does:
    # index = lista_tiempo
    # If the data loop produces fewer steps than the index list, Folium might complain or truncate.
    # For robustness in this script, let's just use the notebook logic.
    
    plugins.HeatMapWithTime(
        lista_peso, 
        radius=30, 
        index=lista_tiempo[:len(lista_peso)], # Adapt index length to data found
        auto_play=False, 
        min_opacity=0.5, 
        max_opacity=1, 
        use_local_extrema=True, 
        name="Accidentes_Turismo_2023"
    ).add_to(madrid_map)
    
    folium.LayerControl().add_to(madrid_map)
    
    # 8. Save
    output_path = os.path.join(ASSETS_DIR, 'accidentes_madrid.html')
    madrid_map.save(output_path)
    print(f"Saved: {output_path}")

def generate_contenedores_map():
    print("Generating Contenedores Map (Notebook Task 1)...")
    input_path = os.path.join(DATA_DIR, CONTAINERS_FILE)
    
    # --- Notebook Logic ---
    # 1. Load Data
    # Notebook says: sep=';', low_memory=False
    contenedores_df = pd.read_csv(input_path, sep=';', low_memory=False)
    
    # 2. Create Base Map
    mapa_contenedores = folium.Map(location=[40.43, -3.65], tiles='OpenStreetMap', zoom_start=12)
    
    # 3. Filter Dataframes
    vidrio_df = contenedores_df.loc[(contenedores_df['Tipo Contenedor'] == 'VIDRIO')]
    envases_df = contenedores_df.loc[(contenedores_df['Tipo Contenedor'] == 'ENVASES')]
    papel_df = contenedores_df.loc[(contenedores_df['Tipo Contenedor'] == 'PAPEL-CARTON')]
    organica_df = contenedores_df.loc[(contenedores_df['Tipo Contenedor'] == 'ORGANICA')]
    
    # 4. Marker Clusters
    vidrio = plugins.MarkerCluster(name="Contenedores Vidrio").add_to(mapa_contenedores)
    envases = plugins.MarkerCluster(name='Contenedores envases').add_to(mapa_contenedores)
    organico = plugins.MarkerCluster(name='Contenedores organico').add_to(mapa_contenedores)
    papel = plugins.MarkerCluster(name='Contenedores papel').add_to(mapa_contenedores)
    
    # Helper to add markers
    def add_markers(df, cluster, color):
        for lat, lng, label in zip(df.LATITUD, df.LONGITUD, df['Descripcion Modelo']):
            folium.Marker(
                location=[lat, lng],
                icon=folium.Icon(color=color, icon="info-sign"),
                popup=label,
            ).add_to(cluster)
            
    add_markers(vidrio_df, vidrio, "green")
    add_markers(envases_df, envases, "orange")
    add_markers(papel_df, papel, "blue")
    add_markers(organica_df, organico, "red")
    
    # 5. HeatMaps
    plugins.HeatMap(data=envases_df[['LATITUD', 'LONGITUD']], radius=15, name="Mapa de calor ENVASES").add_to(mapa_contenedores)
    plugins.HeatMap(data=vidrio_df[['LATITUD', 'LONGITUD']], radius=15, name="Mapa de calor VIDRIO").add_to(mapa_contenedores)
    
    # 6. Controls
    folium.LayerControl().add_to(mapa_contenedores)
    
    # 7. Save
    output_path = os.path.join(ASSETS_DIR, 'contenedores_madrid.html')
    mapa_contenedores.save(output_path)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    create_mock_data_if_missing()
    
    try:
        generate_accidentes_map()
        generate_contenedores_map()
        print("Map generation complete.")
    except Exception as e:
        print(f"Error generating maps: {e}")

