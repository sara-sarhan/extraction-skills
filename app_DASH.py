import os
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html
import dash
from dash import dcc
import base64
from controller import Controller
from utils.constants import Constants
import math
import predict
from werkzeug.utils import secure_filename
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
ctrl = Controller()

app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(html.Img(src=Constants.EXPERIS_LOGO, height="60px"), style={"margin-right": "5px"}),
                        dbc.Col(dbc.NavbarBrand("Extracting Skills from resume", className="ms-2",
                                                style={"color": "#4C5154", "font-size": "30px"}),
                                style={"margin-left": "5px"}),
                    ],
                    align="center",
                    className="g-0",
                ),
                style={"textDecoration": "none"},
            ),
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            dbc.Collapse(
                id="navbar-collapse",
                is_open=False,
                navbar=True,
            ),
        ]
    ),
    color="light",
    dark=True,
)

uploader = dbc.Row(

    dbc.Col([dcc.Upload(
        id="upload-resume",
        children=html.Div(
            ["Drag and drop or click to select a resume to upload."]
        ),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px",
        },
        multiple=True,
    ),
html.H4("Seleziona la lingua"),
       
       dbc.RadioItems( id='radio_items',  options = [
                      {"label": "Italian", "value":"Italian"},
                      {"label": "English", "value": 'English'},
                  ]),
        html.Br(),

        dcc.Loading(id="loading-resume", children=[html.Div(id="output-resume")], type="default"),

        html.Div([dbc.Button(id="collapse-button"), dbc.Collapse(
            id="resume-collapse",

        ),
                  dbc.Button("Get job recommendations", style={"text-align": "center"}, id="recommendation-btn",
                             n_clicks=0),







                  ], style={"display": "none"})

    ],
        width={"size": 6, "offset": 3}),

)

jobs_recommended = dcc.Loading(id="loading-recommendations",
                               children=[html.Div(id="recommendations"),html.Div([dbc.Button("Download skills in Excel file", id="btn-download-txt"),dcc.Download(id="download-text")],style={"display":"none"})], type="default")

app.layout = html.Div([navbar, uploader, html.Br(), jobs_recommended])


@app.callback(Output('output-resume', 'children'),
              [Input('upload-resume', 'contents'), State('upload-resume', 'filename'),
               Input('radio_items', 'value'),])
def update_output(contents, filename, value):
    if contents is not None:

        content_type, content_string = contents[0].split(',')

        if 'pdf' in content_type:
            decoded_resume = base64.b64decode(content_string)
            global name
            name=filename[0]
            resume_uploaded = os.path.join(os.getcwd(), filename[0])







            with open(resume_uploaded, "wb") as resume:
                resume.write(decoded_resume)

            ctrl.set_filename (resume_uploaded)
            ctrl.set_language(value)

            resume_card = dbc.Card([
                dbc.CardHeader(
                    html.Div([filename[0], dbc.Button(
                        "Mostra/Nascondi",
                        id="collapse-button",
                        className="mb-3",
                        color="info",
                        n_clicks=0,
                    ), ], className="d-flex w-100 justify-content-between")

                ),

                dbc.Collapse(

                    dbc.CardBody(
                        [

                            html.ObjectEl(data='data:application/pdf;base64,' + content_string,
                                          type='application/pdf',
                                          width="100%", height="1000px"
                                          )
                        ]
                    ),

                    id="resume-collapse",
                    is_open=True,
                )

            ],
                style={"width": "100%", "margin-left": "10px"}, color="light")

            return dbc.Col([resume_card, html.Br(),
                            html.Div(dbc.Button("Get skills"), style={"text-align": "center"},
                                     id="recommendation-btn", n_clicks=0), html.Br()])

    return html.Div()


@app.callback(
    Output("resume-collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("resume-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open




@app.callback(
    Output("recommendations", "children"),
    Input("recommendation-btn", "n_clicks")
)
def get_recommendation(n):
    if n:

        global pdfnamepath
        pdfnamepath= ctrl.get_filenam()




        language =ctrl.get_languag()

        global skillsner,category
        category, skillsner = predict.main(pdfnamepath, language)

        skillsner=[i for i in skillsner if i!='']
        print('skillsner.....', str(skillsner))
        global df
        df = pd.DataFrame({"skills": skillsner}) #, "category": category
        os.remove(pdfnamepath)

        card = dbc.Card([
            dbc.CardHeader(category.capitalize(),
                           style={"background-color": "#5cb85c", "color": "white", "font-weight": "bold"}),

          html.Div([
            dbc.Button("Download skills in Excel file", id="btn-download-txt"),
            dcc.Download(id="download-text")
        ],style={"text-align":"center","margin-top":"2%"}),
            dbc.CardBody([
                html.Ul(id='my-list', children=[html.Li(i) for i in skillsner])

            ]
            )
        ], color="success", outline=True,)
        # btn=html.Div([
        #     html.Button("Download Text", id="btn-download-txt"),
        #     dcc.Download(id="download-text")
        # ])

        return html.Div([card,html.Br()],style={"margin-left":"25%","margin-right":"25%"})
    return html.Div()

@app.callback(
    Output("download-text", "data"),
    Input("btn-download-txt", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
   return  dcc.send_data_frame(df.to_excel, name+"-"+category+".xlsx", sheet_name=category) #dcc.send_data_frame(df.to_csv, name+"-"+category+".csv") # ";".join(skillsner)



if __name__ == "__main__":
    app.run_server(debug=True, port=8052)
    #app.run_server(debug=True,host='0.0.0.0',port=8054)
