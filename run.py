from application import app as application

if __name__ == '__main__':
    application.debug = True
    #just for android container
    #default port 5000
    application.run(host='0.0.0.0')