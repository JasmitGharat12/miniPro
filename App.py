

from multiprocessing import Value
import streamlit as st
import pandas as pd
import base64,random
import time,datetime
import numpy as np
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams,LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
from streamlit_tags import st_tags
from PIL import Image
import pickle
import pymysql
from Courses import ds_course,web_course,android_course,ios_course,uiux_course
import plotly.express as px
import http.client
import json

def get_table_download_link(df,filename,text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# def course_recommender(course_list):
#     st.subheader("**Courses Recommendations🌟**")
#     c = 0
#     rec_course = []
#     no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
#     random.shuffle(course_list)
#     for c_name, c_link in course_list:
#         c += 1
#         st.markdown(f"({c}) [{c_name}]({c_link})")
#         rec_course.append(c_name)
#         if c == no_of_reco:
#             break
#     return rec_course


connection = pymysql.connect(host='localhost',user='root',password='root',db='sys')
cursor = connection.cursor()

conn = http.client.HTTPSConnection("job-salary-data.p.rapidapi.com")
headers = {
    'X-RapidAPI-Key': "143f035457msh481dd753ce3a758p1144adjsnd4c4a5e41024",
    'X-RapidAPI-Host': "job-salary-data.p.rapidapi.com"
}

def job():
    st.title("Apply For Jobs")
    
    # Get user input for job title, location, and radius
    job_title = st.text_input("Enter job title")
    location = st.text_input("Enter location")
    
    # Make API call and display the result as a DataFrame
    if st.button("Get Jobs"):
        conn.request("GET", f"/job-salary?job_title={job_title}&location={location}&radius=200", headers=headers)
        res = conn.getresponse()
        data = res.read()
        json_data = json.loads(data.decode("utf-8"))
        x=np.matrix(json_data['data'])
        st.dataframe(data=json_data['data'])

def insert_data(name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (name, email, str(res_score), timestamp,str(no_of_pages), reco_field, cand_level, skills,recommended_skills,courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


st.set_page_config(
   page_title="Automatic Resume Analyzer",
   page_icon='./Logo/1.png',
)
def run():
    st.title("Automatic Resume Analyser")
    st.sidebar.markdown("# Dashboard")
    activities = ["Home", "Admin"]
    choice = st.sidebar.selectbox("", activities)
    link = '[©Developed by JasmitNOOB](https://github.com/JasmitGharat12)'
    st.sidebar.markdown(link, unsafe_allow_html=True)
    img = Image.open('./Logo/3.png')
    img = img.resize((340,220))
    st.image(img)
    
    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS SRA;"""
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(100) NOT NULL,
                     Email_ID VARCHAR(50) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field VARCHAR(25) NOT NULL,
                     User_level VARCHAR(30) NOT NULL,
                     Actual_skills VARCHAR(300) NOT NULL,
                     Recommended_skills VARCHAR(300) NOT NULL,
                     Recommended_courses VARCHAR(600) NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    if choice == 'Home':

        pdf_file = st.file_uploader("A Machine Learning Model", type=["pdf"])
        if pdf_file is not None:
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Basic Information**")
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                if resume_data['total_experience'] <= 1:
                    cand_level = "Fresher"
                    st.markdown( '''<h4 style='text-align: left; color: #FFC710;'>Looks like Your a Fresher!!!</h4>''',unsafe_allow_html=True)
                elif resume_data['total_experience'] <= 3:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #0D65E7;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif resume_data['total_experience'] >3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #00D612;'>You are at experience level!</h4>''',unsafe_allow_html=True)

                
                ## Skill shows              
                keywords = st_tags(label='### Your Skills',text='',value=resume_data['skills'],key = '1')
                exp = resume_data['total_experience']

   
                ##  recommendation
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes',
                                'adobe illustrator','illustrator','adobe after effects','after effects',
                                'adobe premier pro','premier pro','adobe indesign']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                

                     
                # Inclined recommendation
                   
                for i in resume_data['skills']:
                    ## Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.markdown( '''<h4 style='text-align: left; color: #FF5900;'>#You may be looking for Data Science Jobs.</h4>''',unsafe_allow_html=True)
                        break

                    ## Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.markdown( '''<h4 style='text-align: left; color: #FF5900;'>#You may be looking for Web Development Jobs.</h4>''',unsafe_allow_html=True)
                        break

                    ## Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.markdown( '''<h4 style='text-align: left; color: #FF5900;'>#You may be looking for Android Development Jobs.</h4>''',unsafe_allow_html=True)
                        break

                    ## IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.markdown( '''<h4 style='text-align: left; color: #FF5900;'>#You may be looking for IOS Development Jobs.</h4>''',unsafe_allow_html=True)
                        break

                    ## UI-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.markdown( '''<h4 style='text-align: left; color: #FF5900;'>#You may be looking for UI-UX Development Jobs.</h4>''',unsafe_allow_html=True)             
                        break             
                
                courses_list = pickle.load(open('courses.pkl', 'rb'))
                similarity = pickle.load(open('similarity.pkl', 'rb'))

                def recommend(course):
                    index = courses_list[courses_list['course_name'] == course].index[0]
                    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
                    recommended_course_names = []
                    for i in distances[1:7]:
                        course_name = courses_list.iloc[i[0]].course_name
                        recommended_course_names.append(course_name)
                    return recommended_course_names
                ## Courses recommender
                                
                st.markdown("<h2 style='text-align: center; color: grey;'>Course Recommendation</h2>",unsafe_allow_html=True)
                course_list = courses_list['course_name'].values
                selected_course = st.selectbox("Select a course you like :",courses_list)
                if st.button('Recommend Courses'):
                    recommended_course_names = recommend(selected_course)
                    st.text(recommended_course_names[0])
                    st.text(recommended_course_names[1])
                    st.text(recommended_course_names[2])
                    st.text(recommended_course_names[3])
                    st.text(recommended_course_names[4])
                    st.text(recommended_course_names[5])
                    st.text(" ")

                job()
                    
                
                
                ## Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)

                ### Resume writing recommendation
                st.subheader("**Resume Quality⏳**")
                resume_score = 0
                if 'Objective' in resume_text:
                    resume_score = resume_score+20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #ff2b2b;'>[-] ERROR!!! Add your career objective.</h4>''',unsafe_allow_html=True)

                if 'Declaration'  in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Delcaration✍/h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #ff2b2b;'>[-] ERROR!!! Add your Delcaration.</h4>''',unsafe_allow_html=True)

                if 'Hobbies' or 'Interests'in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies⚽</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #ff2b2b;'>[-] ERROR!!! Add your Hobbies.</h4></h4>''',unsafe_allow_html=True)

                if 'Achievements' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements🏅 </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #ff2b2b;'>[-] ERROR!!! Add your Achievements.</h4>''',unsafe_allow_html=True)

                if 'Projects' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects👨‍💻 </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #ff2b2b;'>[-] ERROR!!! Add your Personal Projects. </h4>''',unsafe_allow_html=True)

                st.subheader("**Resume Score📊**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('** Your Resume Score is: ' + str(score)+'**')
                
                

                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                              str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                              str(recommended_skills), str(rec_course))


                connection.commit()
            else:
                st.error('Something went wrong..')
    
   
    
    
    
    
    
    
    else:
        ## Admin Side
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'SPIT' and ad_password == '12345678':
                st.success("Welcome Jasmit")
                #Display Data
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("**User's🧛 Data**")
                df = pd.DataFrame(data, columns=['ID','Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection)

                ## Pie chart for predicted field recommendations
                labels = plot_data.Predicted_Field.unique()
                print(labels)
                values = plot_data.Predicted_Field.value_counts()
                print(values)
                st.subheader("📈 **Pie-Chart for Predicted Field Recommendations**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

                ### Pie chart for User's👨‍💻 Experienced Level
                labels = plot_data.User_level.unique()
                values = plot_data.User_level.value_counts()
                st.subheader("📈 ** Pie-Chart for User's👨🧛 Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart📈 for User's👨 Experienced Level")
                st.plotly_chart(fig)
            else:
                st.error("ERROR!!! Wrong ID Or Password")
run()