# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""
#Librerias usadas


import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd 
import plotly.express as px
from map_graph import results


from app import app


#Lectura de los datos
df = pd.DataFrame.from_records(results)
###Cambio de las fechas a tipo datetime
df['fecha_diagnostico']=pd.to_datetime(df['fecha_diagnostico'],errors='coerce')

####Agrupación de casos

Cases=df.groupby('fecha_diagnostico')['id_de_caso'].count().to_frame().reset_index().rename({'id_de_caso':'Casos'},axis='columns')
Cases['Acum']=Cases['Casos'].cumsum()
col_options=[dict(label=x,value=x) for x in Cases.columns[1:3]]

####Agrupación de estado de los contagiados

df['estado']=df['estado'].replace({'leve':'Leve'})
df_estado=df.groupby('estado')['id_de_caso'].count().to_frame().rename({'id_de_caso':'Cant'},axis='columns')
####Agrupacioón de la atención dada a los contagiados
df_atencion=df.groupby(['atenci_n'])['id_de_caso'].count().to_frame().reset_index().rename({'id_de_caso':'Casos'}, axis='columns')







####Creacion layout


app.layout=html.Div(id='General', children=[
                       
                        
                        html.Div(id='top',children=html.H1('Covid-19 Colombia',style= {'textAlign':'center', 'font-weight': 'bold'})),
                        dcc.Dropdown(id='y',options=col_options,multi=False,value='Casos'),
                        
                        html.Div(id='informacion'),
                        html.Br(),
                        dcc.Graph(id='graph',figure={}),
                        
                        
                        html.Div(id='Mayor',children=[
                               
                                html.Div(id='Izq',children=[dcc.Graph(id='graph2',figure=px.pie(df_estado,values='Cant',names=df_estado.index,width=600,height=500,title='Estado de los contagiados'))]),
                                html.Div(id='Der',children=[dcc.Graph(id='graph3',figure=px.pie(df_atencion,values='Casos',names='atenci_n',hole=0.3,width=600,height=500,title='Atencion de los contagiados'))])
                                ]),
                        html.Iframe(id='map',srcDoc=open('mapa_casos.html','r').read(),width='100%',height='500',)
                        
                        
                            
                           
    ]
   )

                              

####Llamada a la función de selección 
@app.callback([Output(component_id='informacion',component_property='children'),
               Output(component_id='graph', component_property='figure')], 
              [Input(component_id='y', component_property='value')])
def update_graph(option_slctd):
    
    print(option_slctd)

    info = "A continuación se muestran varios gráficos sobre los casos de Covid en Colombia"
    
    fig=px.bar(Cases, x='fecha_diagnostico', y=option_slctd)
    
    
    
    return info, fig



if __name__== '__main__':
    app.run_server(debug=True)
