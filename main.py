
from flask import Flask, request, jsonify, render_template_string
import mysql.connector
from mysql.connector import errorcode
import json

app = Flask(__name__)
mysql_host = '<db_host>'
mysql_user = '<user>'
mysql_password = '<password>'
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
    connection = mysql.connector.connect(
        host = mysql_host,
        user = mysql_user,
        password = mysql_password,
        database = mysql_database,
        connect_timeout=2
    )
    cursor = connection.cursor()
    sql = "INSERT INTO analyse_records (task_id, analyse_at, revision, project_key, project_name, branch_name, analyse_result, build_url, build_repo_url, build_repo_branch, build_commitid) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (task_id,analyse_at,revision,project_key,project_name,branch_name,analyse_result,build_url,build_repo_url,build_repo_branch,build_commitid)
    try:
        cursor.execute(sql,values)
        connection.commit()
        return "OK",204
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
    app.run(debug=True, host='0.0.0.0', port=8888)
