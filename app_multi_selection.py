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
import time
from pdfminer.high_level import extract_pages
warnings.filterwarnings("ignore")
## Diskcache
import flask


from waitress import serve


_start_time = time.time()

def tic():
    global _start_time
    _start_time = time.time()
from datetime import datetime
def tac():
    t_sec = round(time.time() - _start_time)
    (t_min, t_sec) = divmod(t_sec,60)
    (t_hour,t_min) = divmod(t_min,60)
    print('{}:{}:{}.'.format(t_hour,t_min,t_sec))
    tim=str(t_hour)+ ":"+ str(t_min) +":"+str(t_sec)
    print(tim)
    dt=datetime.strptime(tim, '%H:%M:%S')

    return  dt
# cache = diskcache.Cache("./cache")
# long_callback_manager =DiskcacheLongCallbackManager(cache)
server = flask.Flask(__name__)
#app = dash.Dash(__name__)
app = dash.Dash(
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    #serve_locally=False,
)

url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

layout_index = html.Div([
    dcc.Link('Navigate to "/page-1"', href='/page-1'),
    html.Br(),
    dcc.Link('Navigate to "/page-2"', href='/page-2'),
])

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


layout_page_1 = html.Div([
dbc.Card(
    [

        dbc.CardBody(

            dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        html.B("Servizio non disponibile"),
                        className="text-center mt-4 mb-5",
                        style={"color": "Purple", "text-decoration": "None",},
                    )
                )
            ]
        ),
        ),
    ],

    style={"height": "100%"},
)
])

    


layout_page_2 = html.Div([
    navbar, uploader, html.Br(), jobs_recommended,



])


# app.layout = html.Div([navbar, uploader, html.Br(), jobs_recommended])
# "complete" layout
app.layout = html.Div([
     dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Index callbacks
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    import json
    with open('json_data_info.json') as json_file:
        data = eval(json.load(json_file))
        stato=data['Stato']
        print(stato)   
        import json
        data['stato_core']='IDLE'

        json_string = json.dumps(data)

        # Directly from dictionary
        with open('json_data_info.json', 'w') as outfile:
            json.dump(json_string, outfile)
            
  
    if stato.strip().lower() == 'run':
        return layout_page_2
    elif stato.strip().lower()=='stop':
        return layout_page_1
    else:
        return layout_index

# Page 1 callbacks
@app.callback(Output('output-state', 'children'),
              Input('submit-button', 'n_clicks'),
              State('input-1-state', 'value'),
              State('input-2-state', 'value'))
def update_output(n_clicks, input1, input2):
    return f'The Button has been pressed {n_clicks} times. \
            Input 1 is {input1} and Input 2 is {input2}'


# Page 2 callbacks
@app.callback(Output('page-2-display-value', 'children'),
              Input('page-2-dropdown', 'value'))
def display_value(value):
    return f'You have selected {value}'

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
        ctrl.folder = None
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
        # import wx
        #
        # app = wx.PySimpleApp()
        # dialog = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        # if dialog.ShowModal() == wx.ID_OK:
        #     print(dialog.GetPath())
        #     directory=dialog.GetPath()
        # dialog.Destroy()
        import tkinter
        from tkinter import filedialog

        root = tkinter.Tk()
        #root.withdraw()

        directory = filedialog.askdirectory()

       # root.mainloop()
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
def get_skilss(n,n2, is_open):
    directory = ctrl.folder
    print(directory)
    if (n or n2) and directory is None:
        return html.Div(),not is_open


    if n and directory is not None:



        global pdfnamepath,name
        import json
        files= list(ctrl.get_contents().keys())
        print('number cv', len(files))
        with open('json_data_info.json') as json_file:
            data = eval(json.load(json_file))


            old=data['number tot cv']
            data['number tot cv'] = int(old)+ len(files)



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
         data["stato_core"] = files
         for   pdfnamepath in  files :
            tic()

            page_num = len(list(extract_pages(pdfnamepath)))
            print('number page',pdfnamepath,page_num)



            page_numold = int(data['number mean pages'])
            print("page_numold", page_numold)
            if page_numold > 0:
                    data['number mean pages'] = (page_numold + page_num) / 2

            else:
                    data['number mean pages'] = page_num

            data['last cv']=pdfnamepath


            oldtime = datetime.strptime(data["time mean cv"], '%H:%M:%S')


            data["time last cv"]='calcolo in corso'
            json_string = json.dumps(data)
             # Directly from dictionary
            with open('json_data_info.json', 'w') as outfile:
                 json.dump(json_string, outfile)
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
            data["time last cv" ] = str(tac().time())


            dt = datetime.strptime('0:0:0', '%H:%M:%S')
            # print('oldtime', oldtime.time(), dt.time(), oldtime.time() != dt.time())
            if oldtime.time()!=dt.time():
             actual=tac()
             delta = actual - oldtime  # delta is a datetime.timedelta object and can be used in the + operation

             avg = oldtime + delta / 2  # average of t1 and t2
             men = [i[0:2] for i in str(avg.time()).split(':')]

             data["time mean cv"]= ":".join(  men)
             print('avg...',":".join(  men))
            else:
                data["time mean cv"] = str(tac().time())
            json_string = json.dumps(data)
            # Directly from dictionary
            with open('json_data_info.json', 'w') as outfile:
                json.dump(json_string, outfile)

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
        with open('json_data_info.json') as json_file:
            data = eval(json.load(json_file))

        data["stato_core"] = "IDLE"




        json_string = json.dumps(data)
        # Directly from dictionary
        with open('json_data_info.json', 'w') as outfile:
            json.dump(json_string, outfile)

       
        return cards, False
    return html.Div(),False





if __name__ == "__main__":
    #app.run_server(debug=True, port=8052)
    #app.run_server(debug=True,host='0.0.0.0',port=8054)
    ctrl.folder=None
    serve(app.server, host="0.0.0.0",port=8080)
    



