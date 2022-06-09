
from flask import Flask, request, redirect, jsonify,json


app = Flask(__name__)




@app.route('/services/start', methods=['POST'])
def start():
   import json
   import json
   with open('json_data_info.json') as json_file:
      data = eval(json.load(json_file))
   json_string = json.dumps(data)
    # Directly from dictionary
   data['Stato']='run'
   json_string = json.dumps(data)
   with open('json_data_info.json', 'w') as outfile:
        json.dump(json_string, outfile)
   return json_string


@app.route('/services/stop', methods=['POST'])
def stop():
    import json
    import json
    with open('json_data_info.json') as json_file:
       data = eval(json.load(json_file))
    json_string = json.dumps(data)
     # Directly from dictionary
    data['Stato']='stop'
    json_string = json.dumps(data)
    with open('json_data_info.json', 'w') as outfile:
         json.dump(json_string, outfile)
    return json_string


@app.route('/services/restart', methods=['POST'])
def restart():
   


    # with open('json_data_info.json') as json_file:
    #     data = eval(json.load(json_file))
    #     data['Stato']='run'
    #     data['stato_core']='IDLE'
    #     data['number tot cv']=0
    #     data['number mean pages']=0
    #     data['last cv']=''
    #     data['time last cv']='00:00:00'
    #     data['time mean cv']='00:00:00'
        import json
        data = {'Stato':'run','stato_core':'IDLE', \
                'number tot cv':0,'number mean pages':0,'last cv':'',\
                   'time last cv' :'00:00:00', 'time mean cv':'00:00:00'}
        json_string = json.dumps(data)
         # Directly from dictionary
        with open('json_data_info.json', 'w') as outfile:
             json.dump(json_string, outfile)
   

        return json_string


@app.route('/services/get_results', methods=['GET'])
def get_results():
     import json
     with open('json_data_info.json') as json_file:
        data = eval(json.load(json_file))
     return  json.dumps(data)

@app.route('/monitoring/getMetricsDefinitions', methods=['GET'])
def getMetricsDefinitions():
     import json
     with open('json_data_info.json') as json_file:
        data = eval(json.load(json_file))
     return  json.dumps({' nomi di parametri ':list(data.keys())})
 
    
@app.route('/monitoring/getMetricsData', methods=['POST'])
def getMetricsData():
       json_dict = request.get_json()
       name = str(json_dict["name"])
  
       import json
       with open('json_data_info.json') as json_file:
          data = eval(json.load(json_file))
       return  json.dumps({ name :data[name] })

if __name__ == "__main__":
    app.run(port=8070)
