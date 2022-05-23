import os
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html
import dash
from dash import dcc
import base64
from controller import Controller
from utils.constants import Constants
from datetime import date
import predict
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
## Diskcache
import flask
import diskcache
import dash_labs
from dash.long_callback import DiskcacheLongCallbackManager
from waitress import serve

# cache = diskcache.Cache("./cache")
# long_callback_manager =DiskcacheLongCallbackManager(cache)
server = flask.Flask(__name__)
#app = dash.Dash(__name__)
app = dash.Dash(
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    #serve_locally=False,
)


ctrl = Controller()
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

    dbc.Col([
        
        
        dcc.Upload(
        id="upload-resume",
        children=html.Div(
            ["Drag and drop or click to select a resumes to upload."]
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
       
     html.Div(id='output-upload'),
        html.Br(),

        dcc.Loading(id="loading-resume", children=[html.Div(id="output-resume")], type="default"),
        dbc.RadioItems( id='radio_items'),
        html.Div([
            
            dbc.Button(id="collapse-button"), 
    
            
            dbc.Collapse(
            id="resume-collapse",

        ),
          
                  dbc.Button("Get skills", style={"text-align": "center"}, id="recommendation-btn",
                             n_clicks=0),

                  dbc.Button("set folder ", style={"text-align": "center"}, id="open_directory",
                             n_clicks=0),
                  html.Div(id='selected_directory'),
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("ATTENTION")),
                    dbc.ModalBody("Select folder!"),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close", id="close1", className="ms-auto", n_clicks=0
                        )
                    ),
                ],
                id="modal",
                is_open=False,
            ),

        ], style={"display": "none"})

    ],
        width={"size": 10, "offset": 1}),

)

jobs_recommended = dcc.Loading(id="loading-recommendations",
                               children=[html.Div(id="recommendations")], type="default")

app.layout = html.Div([navbar, uploader, html.Br(), jobs_recommended])


@app.callback(
    output= Output('output-upload', 'children'),
    inputs=    [Input('upload-resume', 'contents'),
              State('upload-resume', 'filename')]
           )
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        content_type, content_string = list_of_contents[0].split(',')
        # ctrl.set_filename (list_of_names)

        dizlist={}
        for contents,filename in zip(list_of_contents,list_of_names):
            content_type, content_string = contents.split(',')

            dizlist[filename]=contents
    
            if 'pdf' in content_type:
                decoded_resume = base64.b64decode(content_string)
                global name
                
                resume_uploaded = os.path.join(os.getcwd(), filename)







            with open(resume_uploaded, "wb") as resume:
                resume.write(decoded_resume)
        ctrl.set_contents (dizlist)  
        children = dbc.Card([

            # html.Div(dcc.Link('Set folder when saved results', href='/'), style={"text-align": "center"},
            #          id="setfolder-btn", n_clicks=0),
            html.Div([
                dbc.Button('Select the Directory where to save the results', id="open_directory",n_clicks=0,color="link",

                      ),


                html.Div(id='selected_directory', children='No Directory selected!', \
                         ),
            ]),



        html.H3("Resumes",className="me-1"),

                    dbc.RadioItems( id='radio_items',options=[{
                    'label': v,
                    'value': v
                } for v in  list_of_names],value=list_of_names[0],inline=True
                                                              ,style={"margin-right": "20px"}) , #
                    html.Br(),

            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("ATTENTION")),
                    dbc.ModalBody("Select folder!"),
                    dbc.ModalFooter(
                        dbc.Button(
                            "Close", id="close1", className="ms-auto", n_clicks=0
                        )
                    ),
                ],
                id="modal",
                is_open=False,
            ),

                html.Div(dbc.Button("Get skills"), style={"text-align": "center"},
                         id="recommendation-btn", n_clicks=0),



                             html.Br() ],
                                     style={"width": "100%", "margin-left": "10px",'margin-bottom': '10px', "padding": "10px"}, color="light")
  
        return   children


#

@app.callback(output= Output('output-resume', 'children'),
                   inputs= [
               Input('radio_items', 'value'),])
def update_items(value):
    if value is not None:
        diz= ctrl.get_contents()
        content_string=diz[value]
        resume_card = dbc.Card([
            dbc.CardHeader(
                html.Div([value, dbc.Button(
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
                     
    
                       html.ObjectEl(data=content_string,
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
        return resume_card
    else  :  
     return  html.Div()

        
@app.callback(
    output=    Output("resume-collapse", "is_open"),
    inputs=
    [Input("collapse-button", "n_clicks"), State("resume-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open



@app.callback(
    output=
    Output(component_id='selected_directory', component_property='children'),
    inputs=Input(component_id='open_directory', component_property='n_clicks'),
)
def set_folder(n):
    if n:
        import tkinter
        from tkinter import filedialog

        root = tkinter.Tk()
        root.withdraw()
        directory = filedialog.askdirectory()
        root.destroy()
        print(directory)
        ctrl.folder=directory

        return    html.H5("Folder selected: " +directory,
                        style={'width': '50%', 'display': 'inline-block', \
                               'text-align': 'left'}),
    else:
        return html.Div()


@app.callback(

    output=[Output("recommendations", "children"),Output("modal", "is_open")],
    inputs= [Input("recommendation-btn", "n_clicks"),Input("close1", "n_clicks"),State("modal", "is_open")],


)
def get_recommendation(n,n2, is_open):
    directory = ctrl.folder
    print(directory)
    if (n or n2) and directory is None:
        return html.Div(),not is_open


    if n and directory is not None:


        global pdfnamepath,name
        files= list(ctrl.get_contents().keys())




        cards=[]
        language = "Italian"

        global skillsner,category
        list_file_skiss=[]
        today = date.today()

        d1 = today.strftime("%d-%m-%Y")
        folder = directory.split('/')+['skills_'+str(d1)+'.xlsx']
        folder[0]=folder[0]+'/'

        path=os.path.join(*folder)



        with pd.ExcelWriter(path, engine='xlsxwriter') as writer1:

         for   pdfnamepath in  files :
            category, skillsner = predict.main(pdfnamepath, language)


            skillsner=[i for i in skillsner if i!='']
            print('skillsner.....', str(skillsner))
            global df
            df = pd.DataFrame({"skills": skillsner}) #, "category": category
            namesheet=pdfnamepath+' _jobs_'+category
            # n=len(pdfnamepath+' _jobs_'+category)
            # while len(pdfnamepath+' _jobs_'+category)>=31:
            #     namesheet=namesheet[1:n-1]
            df.to_excel(writer1, sheet_name = category, index = False)


            os.remove(pdfnamepath)

            card = dbc.Card(
                [
                dbc.CardHeader(category.capitalize(),
                                style={"background-color": "#5cb85c", "color": "white", "font-weight": "bold"}),
                    dbc.CardBody([
                        html.Ul(id='my-list', children=[html.Li(i) for i in skillsner])

                    ]
                    )


            ], color="success", outline=True,)

            cards.append( html.Div([card, html.Br()], style={"margin-left": "25%", "margin-right": "25%"}))
         df = pd.DataFrame({"name": files}) #, "category": category
         df.to_excel(writer1, sheet_name='name of files curriculum', index=False)

        writer1.save()


       
        return cards, False
    return html.Div(),False





if __name__ == "__main__":
    #app.run_server(debug=True, port=8052)
    #app.run_server(debug=True,host='0.0.0.0',port=8054)
    serve(app.server, host="0.0.0.0", port=8052)