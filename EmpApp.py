from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from datetime import datetime

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


#main index
@app.route('/')
def home():
    return render_template('index.html')
    
#Get attendance list
@app.route("/attendanceList", methods=['GET', 'POST'])
def attendance():
    mycursor = db_conn.cursor()
    getempdata = "select * from attendance"
    mycursor.execute(getempdata)
    attendance = mycursor.fetchall()  

    return render_template('AttendanceList.html', attendance=attendance)

#add new employee page
@app.route("/addnewemp", methods=['GET', 'POST'])
def addEmployee():
    return render_template('AddEmp.html')

#get employee page
@app.route("/getempdata", methods=['GET', 'POST'])
def getEmployee():
    return render_template('GetEmp.html')

#benefit page
@app.route("/benefits", methods=['GET', 'POST'])
def benefits():
    return render_template('benefits.html')
    
#payroll page
@app.route("/payroll", methods=['GET', 'POST'])
def payroll():
       #create a cursor
    mycursor = db_conn.cursor()
    getempdata = "select * from employee"
    mycursor.execute(getempdata)
    result = mycursor.fetchall()
    #render template and send the set of tuples to the HTML file for displaying
    return render_template('payroll.html',result=result)

#staff details page
@app.route("/staff", methods=['GET', 'POST'])
def staff_details():
    return render_template('DetailsOutput.html')

#about page
@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

#add employee
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    email = request.form['email']
    position = request.form['position']
    hire_date = request.form['hire_date']
    salary = request.form['salary']
    benefit = request.form['benefit']
    location = request.form['location']
    phone_num = request.form['phone_num']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, email, phone_num, position, hire_date, salary, benefit))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

#edit employee, but currently no edit employee page? also not done
@app.route("/editemp", methods=['GET','POST'])
def EditEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    email = request.form['email']
    position = request.form['position']
    hire_date = request.form['hire_date']
    salary = request.form['salary']
    benefit = request.form['benefit']
    location = request.form['location']
    phone_num = request.form['phone_num']
    emp_image_file = request.files['emp_image_file']

    update_sql = "UPDATE employee SET first_name = %s, last_name = %s, pri_skill = %s, location = %s, email = %s, phone_num = %s, position = %s, hire_date = %s, salary = %s, benefit = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        
        changefield = (first_name, last_name, pri_skill, location, email, phone_num, position, hire_date, salary, benefit, emp_id)
        cursor.execute(update_sql, (changefield))
    
        emp_name = "" + first_name + " " + last_name
        # Upload image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('EditEmpOutput.html', name=emp_name)

#get edit data
@app.route("/geteditemp/<string:id>", methods=['GET','POST'])
def GetEditData(id):
    #emp_id = request.form['emp_id']
    emp_id = id
    mycursor = db_conn.cursor()
    getempdata = "select * from employee WHERE emp_id = %s"
    mycursor.execute(getempdata,(emp_id))
    result = mycursor.fetchall()
    (emp_id, first_name, last_name, pri_skill, location, email, phone_num, position, hire_date, salary, benefit) = result[0]   

    return render_template('EditEmp.html', emp_id=emp_id,first_name=first_name,last_name=last_name,pri_skill=pri_skill,location=location,email=email,phone_num=phone_num,position=position,hire_date=hire_date,salary=salary,benefit=benefit)
    
#delete employee
@app.route("/delemp/<string:id>", methods=['GET','POST'])
def DeleteEmp(id):
    emp_id = id
    mycursor = db_conn.cursor()
    del_emp_sql = "DELETE FROM employee WHERE emp_id = %s"
    mycursor.execute(del_emp_sql, (emp_id))
    db_conn.commit()

    return render_template('DeleteEmpOutput.html', emp_id=emp_id)
    
#get employee
@app.route("/staffDet", methods=['GET','POST'])
def GetEmpData():
    
    mycursor = db_conn.cursor()
    getempdata = "select * from employee"
    mycursor.execute(getempdata)
    employee = mycursor.fetchall()
    #(emp_id, first_name, last_name, pri_skill, location, email, phone_num, position, hire_date, salary, benefit) = result[0]
    
    """try:
        #employee = getempdata.filter_by(first_name).order_by(emp_id).all()
        list = '<ul>'
        for getempdata in result:
            emp_id +='<li>' + first_name + ', ' + last_name + ', ' + pri_skill + ', ' + location + ', ' + email + ', ' + phone_num + ', ' + position + ', ' + hire_date + ', ' + str(salary) + ', ' + benefit + '</li>'
        list  += emp_id + '</ul>'
        #return list
    
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text"""
    

    return render_template('DetailsOutput.html', employee=employee)

#get SINGLE employee
@app.route("/getemp/<string:id>", methods=['GET','POST'])
def GetSingleEmpData(id):
    #emp_id = request.form['emp_id']
    emp_id = id
    mycursor = db_conn.cursor()
    getempdata = "select * from employee WHERE emp_id = %s"
    mycursor.execute(getempdata,(emp_id))
    result = mycursor.fetchall()
    (emp_id, first_name, last_name, pri_skill, location, email, phone_num, position, hire_date, salary, benefit) = result[0]   
    image_url = showimage(bucket, id)
    # commented as not sure S3 image work or not
    #return render_template('GetEmpOutput.html', emp_id=emp_id,first_name=first_name,last_name=last_name,pri_skill=pri_skill,location=location,email=email,phone_num=phone_num,position=position,hire_date=hire_date,salary=salary,benefit=benefit, image_url=image_url)
    return render_template('GetEmpOutput.html', emp_id=emp_id,first_name=first_name,last_name=last_name,pri_skill=pri_skill,location=location,email=email,phone_num=phone_num,position=position,hire_date=hire_date,salary=salary,benefit=benefit,image_url=image_url)

#Get Employee ID
@app.route("/empattid", methods=['GET','POST'])
def GetEmpId(): 
    #create a cursor
    mycursor = db_conn.cursor()
    getempdata = "select * from employee"
    mycursor.execute(getempdata)
    emps = mycursor.fetchall()
    #render template and send the set of tuples to the HTML file for displaying
    return render_template("attendance.html",emps=emps )

#add attendance
@app.route("/empattendance", methods=['POST'])
def EmpAttandance():
    #auto-increment att_id
    emp_id = request.form['emp_id']
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    status = request.form['attstatus']
    
    insert_sql = "INSERT INTO attendance (emp_id, date, time, status) VALUES (%s, %s, %s, %s)"
    cursor = db_conn.cursor()
    
    if emp_id == "" or status == "":
        mycursor = db_conn.cursor()
        getempdata = "select * from employee"
        mycursor.execute(getempdata)
        emps = mycursor.fetchall()
        return render_template("attendance.html", err="Please Fill In All Fields!", emps=emps )
    
    try:
        cursor.execute(insert_sql, (emp_id, date, time, status))
        db_conn.commit()
        empstatus = "Employee " + emp_id + " has updated status at " + date +", " + time 

    except Exception as e:
            return str(e)

    finally:
        cursor.close()

    return render_template('AttOutput.html', status=empstatus) #currently no attendanceOutput.html or any similiar page

#get payroll
@app.route("/getpay", methods=['GET','POST'])
def GetPayroll():
    emp_id = request.form['emp_id']
    if emp_id == "0":
        mycursor = db_conn.cursor()
        getempdata = "select * from employee"
        mycursor.execute(getempdata)
        result = mycursor.fetchall()
        return render_template("payroll.html", err="Please Fill In All Fields!", result=result )

    mycursor = db_conn.cursor()
    getempdata = "select emp_id, first_name, last_name, salary from employee WHERE emp_id = %s"
    mycursor.execute(getempdata,(emp_id))
    result = mycursor.fetchall()
    (emp_id, first_name, last_name, salary) = result[0]
    return render_template('PayrollDetails.html', emp_id=emp_id,first_name=first_name,last_name=last_name,salary=float("%.2f" % salary))

def showimage(bucket, id):
    s3_client = boto3.client('s3')
    public_urls = []
    emp_id = id
    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
    try:
        for item in s3_client.list_objects(Bucket=bucket)['Contents']:
            presigned_url = s3_client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': emp_image_file_name_in_s3}, ExpiresIn = 100)
            public_urls.append(presigned_url)
    except Exception as e:
        pass
    # print("[INFO] : The contents inside show_image = ", public_urls)
    return public_urls

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
