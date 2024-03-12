import csv
import mysql.connector
import os
import sys

sql_file_path = 'dll.sql'

def set_up_tables(conn):
    #cursor = conn.cursor()
    with open(sql_file_path, 'r') as file:
        sql_script = file.read()

    for statement in sql_script.split(';'):
        # Ignore empty statements (which can occur due to splitting by ';')
        if statement.strip():
            #print("running: ", statement)
            cursor.execute(statement)

    conn.commit()

def import_to_sql(conn, table, cols, folder_name):
    
    col_str = ', '.join(cols)
    csv_file = f'{folder_name}/{table}.csv'

    if table == 'use':
        table = 'used'

    placeholders = ', '.join(['%s'] * len(cols))
    query = f"INSERT IGNORE INTO {table} ({col_str}) VALUES ({placeholders})"
    #print(placeholders)

    #ursor = conn.cursor()
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        #next(csv_reader)
        for row in csv_reader:
            #print(table)
            cursor.execute(query, row)
    conn.commit()
    

def import_data(folder_name):
    set_up_tables(conn)
    table_cols = {
                  'users': ['UCINetID', 'FirstName', 'MiddleName', 'LastName'],
                  'admins': ['admin_id'], 
                  'courses': ['course_id', 'title', 'quarter'],
                  'emails': ['UCINetID', 'email_address'],
                  'machines': ['machine_ID', 'name', 'IP_address', 'operational_status', 'location'],
                  'manage': ['UCINetID', 'machine_ID'],
                  'projects': ['project_id', 'project_name', 'project_description', 'course_id'],
                  'students': ['student_id'],
                  'use' : ['project_id', 'UCINetID', 'machine_id', 'start_date', 'end_date']
                  }


    for k in table_cols.keys():
        import_to_sql(conn, k, table_cols[k], folder_name)
        #print(f'Added {k}')

    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM machines")
    machine_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM courses")
    course_count = cursor.fetchone()[0]
    #cursor.close()
    print(f'{user_count},{machine_count},{course_count}')



def find_popular_course(count):
    dll =  dll = f"select c.course_id, c.title,  count(distinct u.UCINetID) as numStudents from courses as c join projects as p on c.course_id = p.course_id join used as u on p.project_id = u.project_id group by c.course_id, c.title order by numStudents desc limit {count};"
    cursor.execute(dll)
    result = cursor.fetchall()
    for(course_id, title, numStudents) in result:
        print(f'{course_id},{title},{numStudents}')
    cursor.close()

def find_machine_usage(course_id):
    dll =  f'''
    SELECT m.machine_id, m.name, m.IP_address, COALESCE(u.num_uses, 0) AS num_uses
FROM machines m
LEFT JOIN (
    SELECT u.machine_id, COUNT(u.project_id) AS num_uses
    FROM used u
    LEFT JOIN projects p ON u.project_id = p.project_id
    WHERE p.course_id = {course_id}
    GROUP BY u.machine_id
) u ON m.machine_id = u.machine_id 
order by m.machine_id desc;
'''
    cursor.execute(dll)
    result = cursor.fetchall()
    for(machine_id, hostname, ip_address, numUses) in result:
        print(f"{machine_id},{hostname},{ip_address},{numUses}")
    cursor.close()

def find_active_students(machine_id, N, start_date, end_date):

    dll = f'''
        select u.UCINetID, u.FirstName, u.MiddleName, u.LastName
        from users as u
        join students as s on u.UCINetID = s.student_id
        join used as us on s.student_id = us.UCINetID
        where us.machine_id = {machine_id}
        and us.start_date >= date('{start_date}')
        and us.end_date <= date('{end_date}')
        group by s.student_id
        having count(us.machine_id) >= {N}
        order by u.UCINetID;
'''
    cursor.execute(dll)
    result = cursor.fetchall()
    for(UCINetID, FirstName, MiddleName, LastName) in result:
        print(f"{UCINetID},{FirstName},{MiddleName},{LastName}")
    cursor.close()

def find_admin_emails(machine_id):
    dll = f'''
SELECT u.UCINetID, u.FirstName, u.MiddleName, u.LastName, GROUP_CONCAT(e.email_address SEPARATOR ';') AS email_list
FROM users as u
JOIN manage as m ON u.UCINetID = m.UCINetID
JOIN machines mc ON m.machine_id = mc.machine_id
JOIN emails as e ON u.UCINetID = e.UCINetID
WHERE mc.machine_id = {machine_id}
GROUP BY u.UCINetID;
'''
    cursor.execute(dll)
    result = cursor.fetchall()
    for(UCINetID, FirstName, MiddleName, LastName, mailingList) in result:
        print(f"{UCINetID},{FirstName},{MiddleName},{LastName},{mailingList}")


def insertStudent(UCINetID, email, FirstName, MiddleName, LastName):
    try:
        insert_user = f'''
            INSERT INTO users (UCINetID, FirstName, MiddleName, LastName)
            VALUES ('{UCINetID}', '{FirstName}', '{MiddleName}', '{LastName}');
        '''
        insert_email = f'''
            INSERT INTO emails (UCINetID, email_address)
            VALUES ('{UCINetID}', '{email}');
        '''
        insert_student = f'''
            INSERT INTO students (student_id)
            VALUES ('{UCINetID}');
        '''
        with conn.cursor() as cursor:
            cursor.execute(insert_user)
            cursor.execute(insert_email)
            cursor.execute(insert_student)
        conn.commit()
        print("Success")
        return True
    except mysql.connector.errors.IntegrityError as e:
        conn.rollback()
        print("Fail")
        return False

def addEmail(UCINetID, email):
    dll = f'''
        INSERT INTO emails (UCINetID, email_address)
        VALUES ('{UCINetID}', '{email}');
    '''
    with conn.cursor() as cursor:
        cursor.execute(dll)
    conn.commit()
    if cursor.rowcount == 0:
        print("Fail")
    else:
        print("Success")

if __name__ == '__main__':
    #print(sys.argv[1].lower())
    conn = mysql.connector.connect(
        user = 'test',
        # user = 'root',
        password = 'password',
        database = 'cs122a'
    )
    cursor = conn.cursor()

    
    if(sys.argv[1].lower() == 'import'):
        folder_name = sys.argv[2]
        import_data(folder_name)

    if(sys.argv[1].lower() == 'popularcourse'):
        find_popular_course(sys.argv[2])
    
    if(sys.argv[1].lower() == 'machineusage'):
        find_machine_usage(sys.argv[2])

    if(sys.argv[1].lower() == 'activestudent'):
        find_active_students(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    
    if(sys.argv[1].lower() == 'adminemails'):
        find_admin_emails(sys.argv[2])

    if(sys.argv[1].lower() == 'insertstudent'):
        (UCINetID, email, FirstName, MiddleName, LastName) = (sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        insertStudent(UCINetID, email, FirstName, MiddleName, LastName)

    if(sys.argv[1].lower() == 'addemail'):
        (UCINetID, email) = (sys.argv[2], sys.argv[3])
        addEmail(UCINetID, email)