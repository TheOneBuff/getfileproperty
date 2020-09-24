#!coding:utf-8
import db_utils
import address
import pymysql
import sys
import paramiko


port = 22

service_user_datas = []
server_datas = []


# 查询服务的属性
def select_service_user():
    try:
        oss_service_user_db = db_utils.mysql_connect(address.oss_mysql_config)
        cursor_oss_service_user_db = oss_service_user_db.cursor(pymysql.cursors.DictCursor)
        cursor_oss_service_user_db.execute("select * from service_user")
        return cursor_oss_service_user_db.fetchall()
    except Exception as ex:
        db_utils.rollback_quietly(cursor_oss_service_user_db)
        raise ex
    finally:
        db_utils.close_quietly(cursor_oss_service_user_db)


# 查询服务器属性
def select_server():
    try:
        oss_server_db = db_utils.mysql_connect(address.oss_mysql_config)
        cursor_oss_server_db = oss_server_db.cursor(pymysql.cursors.DictCursor)
        cursor_oss_server_db.execute("select * from server")
        return cursor_oss_server_db.fetchall()
    except Exception as ex:
        db_utils.rollback_quietly(cursor_oss_server_db)
        raise ex
    finally:
        db_utils.close_quietly(cursor_oss_server_db)


def uploadfile(update_server_data, local_server_data, service_user_data):
    try:
        # 连接更新的文件所在机器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(local_server_data["ip"], port, local_server_data["user"], password=local_server_data["password"])
        update_command = "scp " + service_user_data["service_jar_path"] + "/" + service_user_data["service_jar_name"] + "*.jar " + \
                         update_server_data["user"] + "@" + service_user_data["updatetoserver"] + ":" + service_user_data["service_jar_path"]
        stdin, stdout, stderr = ssh.exec_command(update_command)
        print(service_user_data["service_jar_name"] + "更新成功")
        ssh.close()
        # 连接更新后的机器
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 建立连接
        ssh.connect(update_server_data["ip"], port, update_server_data["user"], password=update_server_data["password"])
        start_command = "cd /root && python3 publish.py -s " + service_user_data["script_name"] + " --remove --install"
        jar_version_command = "curl -X POST http://"+ update_server_data["ip"] +":1010/serverversion/insertServerversion?jarpath=" + service_user_data["service_jar_path"].replace("/", "%2F") + "%2F"
        stdin, stdout, stderr = ssh.exec_command(start_command)
        print(service_user_data["script_name"] + "重启成功")
        stdin, stdout, stderr = ssh.exec_command(jar_version_command)
        print("版本号已经写入数据库")
        ssh.close()
    except Exception as e:
        print(88, e)


if __name__ == '__main__':
    service_user_datas = select_service_user()
    server_datas = select_server()
    service_jar_name = []
    for server in service_user_datas:
        service_jar_name.append(server["service_jar_name"])
    # 获取输入参数，可以是多个。如果是多个用,分开
    sysdata = sys.argv[1]
    input_jar_name = []
    if sysdata.find(",") != -1:
        input_jar_name = sysdata.split(",")
    else:
        input_jar_name.append(sysdata)
    for jar_name in input_jar_name:
        for service_user_data in service_user_datas:
            if jar_name == service_user_data["service_jar_name"]:
                for server_data in server_datas:
                    if service_user_data["updatetoserver"] == server_data["ip"]:
                        update_server_data = server_data
                    if service_user_data["localserver"] == server_data["ip"]:
                        local_server_data = server_data
                        uploadfile(update_server_data, local_server_data, service_user_data)





