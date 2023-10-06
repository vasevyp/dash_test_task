from dash import html, Output, Input, State, dcc, dash_table
from dash_extensions.enrich import (DashProxy,
                                    ServersideOutputTransform,
                                    MultiplexerTransform)
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate
import sqlite3 as sl
import pandas as pd
import plotly.express as px

con = sl.connect('../testDB.db')
df = pd.read_sql_query("SELECT * FROM sources", con)

fig = px.pie(df, values=df.duration_hour+df.duration_min /
             60, names=df.state)
fig_line = px.timeline(df, x_start='state_begin',
                       x_end='state_end', y='endpoint_name', color="state",  hover_data=['reason', 'status'])


CARD_STYLE = dict(withBorder=True,
                  shadow="sm",
                  radius="md",
                  style={'height': '550px'})


class EncostDash(DashProxy):
    def __init__(self, **kwargs):
        self.app_container = None
        super().__init__(transforms=[ServersideOutputTransform(),
                                     MultiplexerTransform()], **kwargs)


app = EncostDash(name=__name__)


def get_layout():

    return html.Div([
        dmc.Paper([
            dmc.Grid([
                dmc.Col([

                    dmc.Card([
                        html.H2('Клиент: ' + df.client_name[0]),
                        html.H4('Сменный день: ' + df.calendar_day[0]),
                        html.H4('Точка учета: ' + df.endpoint_name[0]),
                        html.H4('Начало периода: ' + min(df.state_begin)),
                        html.H4('Конец периода: ' + max(df.state_end)),
                        html.Br(),

                    ],
                        **CARD_STYLE)
                ], span=6),
                dmc.Col([

                    dmc.Card([
                        html.H2('Диаграмма состояний агрегата '),
                        dcc.Graph(figure=fig),
                    ],
                        **CARD_STYLE)
                ], span=6),

                dmc.Col([

                    dmc.Card([
                        html.H2(
                            'Диаграмма длительности состояний агрегата'),
                        html.H5(
                            f'Фильтрация по состоянию:'),

                        dmc.Select(
                            id='input',
                            data=["Работа", "Простой", "Наладка", "См. задание выполнено",
                                  "Обед 60мин", "Перерыв 5мин", "Обед 30мин", "Вычисление"],
                            searchable=True,
                            nothingFound="No options found",
                            style={"width": 300},
                            placeholder='выберете состояние'
                        ),
                        html.Br(),
                        dmc.Button(
                            'Фильтровать',
                            id='button1'),
                        dmc.Button(html.A(('Перезагрузить'), href='/'),
                                   style={"margin-left": "15px"}),

                        html.Div(
                            id='output'),
                        dcc.Graph(figure=fig_line)
                    ],
                        **CARD_STYLE)
                ], span=12),
            ], gutter="xl",)
        ]),

    ])


app.layout = get_layout()

print("Start - OK!")


@app.callback(
    Output('output', 'children'),
    State('input', 'value'),
    Input('button1', 'n_clicks'),
    prevent_initial_call=True,
)
def update_div1(
    value,
    click
):
    df1 = df[df['state'] == value]
    print(f'Кнопка нажата, данные: {value}')
    fig_line = px.timeline(df1, y='endpoint_name', hover_data=['reason', 'status'], x_start='state_begin',
                           x_end='state_end',  color="state")

    if click is None:
        raise PreventUpdate

    return html.Div([
        dmc.Paper([
            dmc.Grid([
                dmc.Col([
                    dmc.Card([
                        dcc.Graph(figure=fig_line)
                    ],
                        **CARD_STYLE)
                ], span=12),
            ], gutter="xl",)
        ])
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
