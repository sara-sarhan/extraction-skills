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

                  html.A("Leggi dettagli", id="a-modal-0", href="#modal-description-0", n_clicks=0),
                  html.A("Leggi dettagli", id="a-modal-1", href="#modal-description-1", n_clicks=0),
                  html.A("Leggi dettagli", id="a-modal-2", href="#modal-description-2", n_clicks=0),
                  html.A("Leggi dettagli", id="a-modal-3", href="#modal-description-3", n_clicks=0),
                  dbc.Modal([
                      dbc.ModalHeader(dbc.ModalTitle("Dettagli")),
                      dbc.ModalBody("aaa")
                  ], size="modal-xl", id="modal-description-0", is_open=False, style={"display": "none"}),

                  dbc.Modal([
                      dbc.ModalHeader(dbc.ModalTitle("Dettagli")),
                      dbc.ModalBody("bbb")
                  ], size="modal-xl", id="modal-description-1", is_open=False, style={"display": "none"}),
                  dbc.Modal([
                      dbc.ModalHeader(dbc.ModalTitle("Dettagli")),
                      dbc.ModalBody("ccc")
                  ], size="modal-xl", id="modal-description-2", is_open=False, style={"display": "none"}),
                  dbc.Modal([
                      dbc.ModalHeader(dbc.ModalTitle("Dettagli")),
                      dbc.ModalBody("ddd")
                  ], size="modal-xl", id="modal-description-3", is_open=False, style={"display": "none"})

                  ], style={"display": "none"})

    ],
        width={"size": 6, "offset": 3}),

)

jobs_recommended = dcc.Loading(id="loading-recommendations", children=[html.Div(id="recommendations")], type="default")

app.layout = html.Div([navbar, uploader, html.Br(), jobs_recommended])


@app.callback(Output('output-resume', 'children'),
              [Input('upload-resume', 'contents'), State('upload-resume', 'filename'),
               Input('radio_items', 'value'),])
def update_output(contents, filename, value):
    if contents is not None:

        content_type, content_string = contents[0].split(',')

        if 'pdf' in content_type:
            decoded_resume = base64.b64decode(content_string)

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



        pdfnamepath= ctrl.get_filenam()




        language =ctrl.get_languag()



        category, skillsner = predict.main(pdfnamepath, language)
        skillsner=[i for i in skillsner if i!='']
        print('skillsner.....', str(skillsner))

        os.remove(pdfnamepath)

        card = dbc.Card([
            dbc.CardHeader(category.capitalize(),
                           style={"background-color": "#5cb85c", "color": "white", "font-weight": "bold"}),
            dbc.CardBody([
                html.Ul(id='my-list', children=[html.Li(i) for i in skillsner])

            ]
            )
        ], color="success", outline=True,)

        return html.Div(card,style={"margin-left":"25%","margin-right":"25%"})
    return html.Div()


@app.callback(
    Output("modal-description-0", "is_open"),
    Input("a-modal-0", "n_clicks"),
    State("modal-description-0", "is_open"),
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal-description-1", "is_open"),
    Input("a-modal-1", "n_clicks"),
    State("modal-description-1", "is_open"),
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal-description-2", "is_open"),
    Input("a-modal-2", "n_clicks"),
    State("modal-description-2", "is_open"),
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("modal-description-3", "is_open"),
    Input("a-modal-3", "n_clicks"),
    State("modal-description-3", "is_open"),
)
def toggle_modal(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == "__main__":
    #app.run_server(debug=True, port=8054)
    app.run_server(host='0.0.0.0',port=8054)
