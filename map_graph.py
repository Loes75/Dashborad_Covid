# -*- coding: utf-8 -*-

import folium
import pandas as pd 
from sodapy import Socrata


url="https://raw.githubusercontent.com/Loes75/Covid19_Col_Web/master/coordenadas_col.csv"
#client = Socrata("www.datos.gov.co", None)  
client = Socrata("www.datos.gov.co", "8ohqgp4u9puH40FbbytMWkjpv")
results = client.get("gt2j-8ykr", limit=2000000)  #Limit of 1000000 rows



df = pd.DataFrame.from_records(results)
###Cambio de las fechas a tipo datetime
df['fecha_diagnostico']=pd.to_datetime(df['fecha_diagnostico'],errors='coerce')

##Lectura coordenadas capitales departamentos
Col_coordinates=pd.read_csv(url,header=None,names=['departamento','Latitud','Longitud']) 


########Renombrar departamentos igual a como estan en coordenadas
df['departamento']=df['departamento'].replace({'Bogotá D.C.':'Bogota','Valle del Cauca':'Valle_del_Cauca','Cartagena D.T. y C.':'Cartagena',
                                    'Barranquilla D.E.':'Barranquilla','Santa Marta D.T. y C.':'Santa_Marta','Archipiélago de San Andrés Providencia y Santa Catalina':'San_Andres',
                                    'Atlántico':'Atlantico','Boyacá':'Boyaca', 'Córdoba':'Cordoba', 'Bolívar':'Bolivar','Buenaventura D.E.':'Buenaventura', 'Chocó':'Choco',
                                                               'Caquetá':'Caqueta','Vaupés':'Vaupes','Norte de Santander':'Norte_de_Santander','Quindío':'Quindio'
                                                              })
Col_coordinates['departamento']=Col_coordinates['departamento'].replace({'Chocó':'Choco'})
#######Merge df con col_cordinates

mapa_info=df.groupby('departamento')['id_de_caso'].count().to_frame().reset_index().rename({'id_de_caso':'Casos'}, axis='columns')
df_merge=pd.merge(Col_coordinates,df,on='departamento',how='right')
mapa_info=pd.merge(Col_coordinates,mapa_info,on='departamento')
mapa_info.drop_duplicates();


map=folium.Map(location=[4.5709,-74.2973],zoom_start=5,tiles='Stamenterrain')

for lat,long,value, name in zip(mapa_info['Latitud'],mapa_info['Longitud'],mapa_info['Casos'],mapa_info['departamento']):
    folium.CircleMarker([lat,long],radius=value*0.003,popup=('<strong>State</strong>: '+str(name).capitalize()+'<br>''<strong>Total_Cases</strong>: ' + str(value)+ '<br>'),color='red',fill_color='red',fill_opacity=0.3).add_to(map)
    


map.save('mapa_casos.html')
    
