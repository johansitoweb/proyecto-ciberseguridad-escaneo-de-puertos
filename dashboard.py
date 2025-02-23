import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Datos de ejemplo
data = {
    'Puertos': ['80', '443', '22', '21', '25'],
    'Estado': [1, 0, 1, 0, 1],
    'Descripción': ['HTTP', 'HTTPS', 'SSH', 'FTP', 'SMTP']
}
df = pd.DataFrame(data)

# Crear un gráfico de barras inicial
fig = px.bar(df, x='Puertos', y='Estado', title='Estado de Puertos',
             labels={'Estado': 'Estado (1=Abierto, 0=Cerrado)'},
             hover_data=['Descripción'],  # Agregar información adicional en el tooltip
             color='Estado', color_continuous_scale=px.colors.sequential.RdBu)

# Definir el diseño de la aplicación
app.layout = html.Div(style={'padding': '20px'}, children=[
    html.H1(children='Visualización Avanzada de Puertos'),

    html.Div(children='''Seleccione un puerto para ver más detalles:'''),

    dcc.Dropdown(
        id='puerto-dropdown',
        options=[{'label': f'Puerto {row["Puertos"]} - {row["Descripción"]}', 'value': row['Puertos']} for index, row in df.iterrows()],
        value='80',  # Valor por defecto
        clearable=False,
        style={'width': '50%'}
    ),

    dcc.Graph(
        id='estado-grafico',
        figure=fig
    ),

    html.Div(id='detalles-puerto', style={'margin-top': '20px'})
])

# Callback para actualizar el gráfico y los detalles del puerto seleccionado
@app.callback(
    Output('estado-grafico', 'figure'),
    Output('detalles-puerto', 'children'),
    Input('puerto-dropdown', 'value')
)
def update_graph(selected_puerto):
    # Filtrar el DataFrame según el puerto seleccionado
    filtered_df = df[df['Puertos'] == selected_puerto]

    if filtered_df.empty:
        return dash.no_update, "No se encontraron detalles para el puerto seleccionado."

    # Crear un nuevo gráfico de barras
    fig = px.bar(filtered_df, x='Puertos', y='Estado', title=f'Estado del Puerto {selected_puerto}',
                  labels={'Estado': 'Estado (1=Abierto, 0=Cerrado)'})

    # Detalles del puerto
    detalles = (f'Puerto: {selected_puerto}, '
                f'Estado: {"Abierto" if filtered_df["Estado"].values[0] == 1 else "Cerrado"}, '
                f'Descripción: {filtered_df["Descripción"].values[0]}')

    return fig, detalles

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)