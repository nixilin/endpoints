from flask import Flask, request, jsonify, render_template_string
import mysql.connector
from mysql.connector import errorcode
import json,os,requests,time

app = Flask(__name__)
mysql_host = '<db_host>'
mysql_user = '<db_user>'
mysql_password = '<db_password>'
mysql_database = '<db_name>'

@app.route('/updated/sonar_analyse',methods=['POST'])
def sonar_analyse():
    if not request.is_json:
        return jsonify({'error': 'Request must be in JSON format.'}), 500
    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({'error':'Failed to parse JSON data.','message':str(e)}), 500

    build_url = ''
    build_repo_url = ''
    build_commitid = ''
    build_repo_branch = ''
    task_id = data['taskId']
    analyse_at = data['analysedAt']
    revision = data['revision']
    project_key = data['project']['key']
    project_name = data['project']['name']
    branch_name = data['branch']['name']
    analyse_result = data['qualityGate']['status']
    if 'sonar.analysis.build_url' in data['properties'].keys():
        build_url = data['properties']['sonar.analysis.build_url']

    if 'sonar.analysis.build_repo_branch'    in data['properties'].keys():
        build_repo_branch    =     data['properties']['sonar.analysis.build_repo_branch']

    if 'sonar.analysis.build_commitid'       in data['properties'].keys():
        build_commitid       =     data['properties']['sonar.analysis.build_commitid']

    if 'sonar.analysis.build_repo_url'       in data['properties'].keys():
        build_repo_url       =     data['properties']['sonar.analysis.build_repo_url']

    #################################
    if os.getenv("debug") is not None:
        print("Debug mode.")
        table_name = 'analyse_records_test'
    else:
        table_name = 'analyse_records'
    if os.getenv("SONAR_LOGIN") is not None:
        print("Get metrics from sonar for project key %s branch %s." % (project_key, branch_name))
        sonar_login = os.getenv("SONAR_LOGIN")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        get_measures_params={}
        get_measures_params['branch'] = branch_name
        get_measures_params['component'] = project_key
        get_measures_params['metricKeys'] = 'code_smells,bugs,vulnerabilities,duplicated_blocks,security_hotspots,sqale_index'

        metrics_vulnerabilities = '-'
        metrics_code_smells = '-'
        metrics_sqale_index = '-'
        metrics_duplicated_blocks = '-'
        metrics_bugs = '-'
        metrics_security_hotspots = '-'

        try:
            get_measures_req = requests.get(url="https://sonar.onewo.com/api/measures/component",auth=(sonar_login,''),headers=headers,params=get_measures_params,timeout=3)
            if get_measures_req.status_code == 200:
                measures_json = get_measures_req.json()
                if 'component' in measures_json.keys():
                    for measure in measures_json['component']['measures']:
                        if measure['metric'] == "vulnerabilities": #
                            metrics_vulnerabilities = measure['value']
                        if measure['metric'] == 'code_smells': #
                            metrics_code_smells = measure['value']
                        if measure['metric'] == 'sqale_index': #
                            metrics_sqale_index = measure['value']
                        if measure['metric'] == 'duplicated_blocks': #
                            metrics_duplicated_blocks = measure['value']
                        if measure['metric'] == 'bugs': #
                            metrics_bugs = measure['value']
                        if measure['metric'] == 'security_hotspots': #
                            metrics_security_hotspots = measure['value']
            else:
                print("Http status code ne 200. [%s]\n Headers:\n%s" % (get_measures_req.status_code,get_measures_req.request.headers ))
        except Exception as e:
            print("Error: %s"%e)
            pass
        finally:
            time.sleep(2)

    #################################
    connection = mysql.connector.connect(
        host = mysql_host,
        user = mysql_user,
        password = mysql_password,
        database = mysql_database,
        connect_timeout=2
    )
    cursor = connection.cursor()
    sql = "INSERT INTO `" + table_name
    sql = sql+ "` (task_id, analyse_at, revision, project_key, project_name, branch_name, analyse_result, build_url, build_repo_url, build_repo_branch, build_commitid, metrics_vulnerabilities, metrics_code_smells, metrics_sqale_index, metrics_duplicated_blocks, metrics_bugs, metrics_security_hotspots) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (task_id, analyse_at, revision, project_key, project_name, branch_name, analyse_result, build_url, build_repo_url, build_repo_branch, build_commitid, metrics_vulnerabilities, metrics_code_smells, metrics_sqale_index, metrics_duplicated_blocks, metrics_bugs, metrics_security_hotspots)
    try:
        cursor.execute(sql,values)
        connection.commit()
        return "OK"
    except Exception as e:
        connection.rollback()
        print(f"Error: {str(e)}")
        return f"Error: {str(e)}",500
    finally:
        cursor.close()
        connection.close()
    #################################

@app.errorhandler(404)
def page_not_found(e):
    return render_template_string('four zero four'), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9999)
