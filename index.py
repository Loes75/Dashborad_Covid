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
from plotly.subplots import make_subplots
#from map_graph import results
from sodapy import Socrata



from app import app,server

client = Socrata("www.datos.gov.co", "8ohqgp4u9puH40FbbytMWkjpv")

results = client.get("gt2j-8ykr", where= "fecha_reporte_web > '2020-06-01T00:00:00.000'", limit=100)
#Lectura de los datos
df = pd.DataFrame.from_records(results)

###Cambio de las fechas a tipo datetime
df['fecha_reporte_web']=pd.to_datetime(df['fecha_reporte_web'],errors='coerce')

####Agrupación de casos

Cases=df.groupby('fecha_reporte_web')['id_de_caso'].count().to_frame().reset_index().rename({'id_de_caso':'Casos'},axis='columns')
Cases['Acum']=Cases['Casos'].cumsum()
col_options=[dict(label=x,value=x) for x in Cases.columns[1:3]]

####Agrupación de estado de los contagiados

df['estado']=df['estado'].replace({'leve':'Leve'})
df_estado=df.groupby('estado')['id_de_caso'].count().to_frame().rename({'id_de_caso':'Cant'},axis='columns')
####Agrupacioón de la atención dada a los contagiados
df_atencion=df.groupby(['atenci_n'])['id_de_caso'].count().to_frame().reset_index().rename({'id_de_caso':'Casos'}, axis='columns')

####### TOP 15 Ciudades (casos, recuperados, muertes)

top_15=df.groupby('ciudad_de_ubicaci_n')['id_de_caso'].count().sort_values().tail(15).to_frame().reset_index().rename({'id_de_caso':'Casos'},axis='columns')
figure1=px.bar(top_15,x='Casos',y='ciudad_de_ubicaci_n',orientation='h',color_discrete_sequence =['#f38181'])
top15_m=df.loc[df['fecha_de_muerte'].notnull()].groupby('ciudad_de_ubicaci_n')['id_de_caso'].count().sort_values().tail(15).to_frame().reset_index().rename({'id_de_caso':'Muertes'}, axis='columns')
figure2=px.bar(top15_m,x='Muertes',y='ciudad_de_ubicaci_n',orientation='h')

fig4=make_subplots(rows=1, cols=2, shared_xaxes=False, horizontal_spacing=0.2,
                  subplot_titles=('Infectados','Muertos'))

fig4.add_trace(figure1['data'][0], row=1, col=1)
fig4.add_trace(figure2['data'][0], row=1, col=2)




####Creacion layout
colors = {
    'background': '#FFFFFF',
    'text': '#465442',
    'text2': '#B44646'
}

style1={
            'textAlign': 'center',
            'color': colors['text'],
            'fontWeight':'bold'}
style2={
            'textAlign': 'center',
            'color': colors['text2'],
            'fontWeight':'bold'}


#html.Div(html.H2(id='informacion'),style=style1),

app.layout=html.Div(id='General', style={'backgroundColor': colors['background']},children=[
        html.H1(
        children='Covid-19 en Colombia',
        style=style1
        ),
        html.Div( id='informacion', children= [html.H2("La adquisición de datos toma un poco de tiempo, espera unos segundos")],style=style2),
        html.Div(html.H4("Seleccione Casos si desea ver el número diario de casos y Acum si desea ver el número de casos acumulados "),style=style1),
        dcc.Dropdown(id='y',style={'height': '40px', 'width': '100%', 'fontSize': "25px",'color':'#465442'},options=col_options,multi=False,value='Casos'),
        dcc.Graph(id='graph',figure={'data':[],
            'layout': {
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']}}}),
        html.Div(html.H3("A continuación se muestra el estado de los pacientes "),style=style1),
        html.Div(id='Mayor',children=[
                               
                                html.Div(id='Izq',children=[dcc.Graph(id='graph2',figure=px.pie(df_estado,values='Cant',names=df_estado.index,hole=0.3,title='Estado de los contagiados'),className="six columns")]),
                                html.Div(id='Der',children=[dcc.Graph(id='graph3',figure=px.pie(df_atencion,values='Casos',names='atenci_n',hole=0.3,title='Atencion de los contagiados'),className="six columns")])
                               ],className="row"),
        html.Div(html.H3("A continuación se muetran las ciudades con más infectados y muertes"),style=style1),
        html.Div(id='Top',children=[dcc.Graph(id='top_graph',figure= fig4)]),
        html.Div(html.H3("A continuación se muestra un mapa con información sobre cuantos cuantos casos hay en cada departamento"),style=style1),
        html.Div(id='mapa',children=[html.Iframe(id='map',srcDoc=open('mapa_casos.html').read(),width='70%',height='500px')])
        
        
        
    
        
    
    
    
    
    
    
    ])
    
                     

####Llamada a la función de selección 
@app.callback([Output(component_id='informacion',component_property='children'),
               Output(component_id='graph', component_property='figure'),
               Output(component_id='graph2', component_property='figure'),
               Output(component_id='graph3', component_property='figure'),
               Output(component_id='top_graph', component_property='figure')], 
              [Input(component_id='y', component_property='value')])
def update_graph(option_slctd):
    
    results = client.get("gt2j-8ykr", limit=1000000)  #Limit of 1000000 rows
        
    info = "Datos actualizados"
    df = pd.DataFrame.from_records(results)

    ###Cambio de las fechas a tipo datetime
    df['fecha_reporte_web']=pd.to_datetime(df['fecha_reporte_web'],errors='coerce')
    Cases=df.groupby('fecha_reporte_web')['id_de_caso'].count().to_frame().reset_index().rename({'id_de_caso':'Casos'},axis='columns')
    Cases['Acum']=Cases['Casos'].cumsum()
    ####Agrupacioón del estado de los contagiados
    df_estado=df.groupby('estado')['id_de_caso'].count().to_frame().rename({'id_de_caso':'Cant'},axis='columns')
    ####Agrupacioón de la atención dada a los contagiados
    df_atencion=df.groupby(['atenci_n'])['id_de_caso'].count().to_frame().reset_index().rename({'id_de_caso':'Casos'}, axis='columns')
    
    fig=px.bar(Cases, x='fecha_reporte_web', y=option_slctd)
    fig2=px.pie(df_estado,values='Cant',names=df_estado.index,hole=0.3,title='Estado de los contagiados')
    fig3=px.pie(df_atencion,values='Casos',names='atenci_n',hole=0.3,title='Atencion de los contagiados')
    
    ####### TOP 15 Ciudades (casos, muertes)

    top_15=df.groupby('ciudad_de_ubicaci_n')['id_de_caso'].count().sort_values().tail(15).to_frame().reset_index().rename({'id_de_caso':'Casos'},axis='columns')
    figure1=px.bar(top_15,x='Casos',y='ciudad_de_ubicaci_n',orientation='h',color_discrete_sequence =['#f38181'])
    top15_m=df.loc[df['fecha_de_muerte'].notnull()].groupby('ciudad_de_ubicaci_n')['id_de_caso'].count().sort_values().tail(15).to_frame().reset_index().rename({'id_de_caso':'Muertes'}, axis='columns')
    figure2=px.bar(top15_m,x='Muertes',y='ciudad_de_ubicaci_n',orientation='h')
    fig4=make_subplots(rows=1, cols=2, shared_xaxes=False, horizontal_spacing=0.2,
                  subplot_titles=('Infectados','Muertos'))

    fig4.add_trace(figure1['data'][0], row=1, col=1)
    fig4.add_trace(figure2['data'][0], row=1, col=2)
    
    
    
    return info, fig, fig2 ,fig3, fig4



if __name__== '__main__':
    app.run_server(debug=True)
