from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

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
    
#attendance page
@app.route("/attendance", methods=['GET', 'POST'])
def attendance():
    return render_template('attendance.html')

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
    return render_template('payroll.html')

#staff details page
@app.route("/staffDet", methods=['GET', 'POST'])
def staff_details():
    return render_template('staff_details.html')

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
    
#delete employee
@app.route("/delemp", methods=['GET','POST'])
def DeleteEmp():
    emp_id = request.form['emp_id']
    mycursor = db_conn.cursor()
    del_emp_sql = "DELETE FROM employee WHERE emp_id = %s"
    mycursor.execute(del_emp_sql, (emp_id))
    db_conn.commit()

    return render_template('DelEmpOut.html', emp_id=emp_id)
    
#get employee
@app.route("/getemp", methods=['GET','POST'])
def GetEmpData():
    emp_id = request.form['emp_id']
    mycursor = db_conn.cursor()
    getempdata = "select * from employee WHERE emp_id = %s"
    mycursor.execute(getempdata,(emp_id))
    result = mycursor.fetchall()
    (emp_id, first_name, last_name, pri_skill, location, email, phone_num, position, hire_date, salary, benefit) = result[0]   
    image_url = showimage(bucket)
    
    try:
        employee = getempdata.query.filter_by(pri_skill).order_by(emp_id).all()
        first_name = '<ul>'
        for getempdata in employee:
            emp_id +='<li>' + first_name + ', ' last_name', '+ pri_skill +', '+ location +', '+ email + ', ' + phone_num + ', ' + position + ', ' + hire_date + ', ' + salary + ', ' + benefit + '</li>
         first_name += '<ul>'
    
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text
    

    return render_template('GetEmpDataOut.html', emp_id=emp_id,first_name=first_name,last_name=last_name,pri_skill=pri_skill,location=location,email=email,phone_num=phone_num,position=position,hire_date=hire_date,salary=salary,benefit=benefit,image_url=image_url)

#add attendance
@app.route("/empattendance", methods=['POST'])
def EmpAttandance():
   
    emp_id = request.form['emp_id']
    date = request.form['date']
    time = request.form['time']

    insert_sql = "INSERT INTO attendance VALUES (%s, %s, %s)"
    cursor = db_conn.cursor()
    
    try:
        cursor.execute(insert_sql, (emp_id, date, time))
        db_conn.commit()
        status = "Employee " + emp_id + " has checked in at " + date +", " + time 

    except Exception as e:
            return str(e)

    finally:
        cursor.close()

    return render_template('Index.html', status=status) #currently no attendanceOutput.html or any similiar page

#get payroll
@app.route("/getpay", methods=['GET','POST'])
def GetPayroll():
    emp_id = request.form['emp_id']
    mycursor = db_conn.cursor()
    getempdata = "select first_name, last_name, salary from employee WHERE emp_id = %s"
    mycursor.execute(getempdata,(emp_id))
    result = mycursor.fetchall()
    (emp_id, first_name, last_name, salary) = result[0]
    return render_template('payroll.html', emp_id=emp_id,first_name=first_name,last_name=last_name,salary=salary)   #not sure send to where


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)