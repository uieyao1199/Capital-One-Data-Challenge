###############################################################################
###############################################################################
# Project: CRWD_Survey_Monkey
#Author: Xiaojun Yao (Uie)
# Date: 9 Jun 2019
###############################################################################
###############################################################################

import requests
import json
import random
from itertools import product

import time
import datetime

import pandas as pd
import numpy as np

###############################################################
# Creating Dataframe for Survey Questions
###############################################################
def missing_value_en(df,year,company):

    #Get metric index table
    METRIC_TABLE=df[['METRIC NAME']].drop_duplicates().sort_values(by='METRIC NAME').reset_index(drop=True)
    METRIC_TABLE['METRIC ID']= pd.Categorical(METRIC_TABLE['METRIC NAME'].astype(str)).codes
    #METRIC_TABLE.to_csv('Metric_index_tabel.csv',index=False)

    #Get company index table
    COMPANY_TABLE=df[['COMPANY NAME']].drop_duplicates().sort_values(by='COMPANY NAME').reset_index(drop=True)
    COMPANY_TABLE['COMPANY ID'] = pd.Categorical(COMPANY_TABLE['COMPANY NAME'].astype(str)).codes
    ###------pseudo email address
    COMPANY_TABLE['COMPANY EMAIL']=COMPANY_TABLE['COMPANY NAME'].apply(lambda x:'{}@gmail.com'.format(x.lower().replace(' ','')))
    #COMPANY_TABLE.to_csv('Company_index_tabel.csv',index=False)

    #Get Survey Question Table
    survey=df[['METRIC NAME']].drop_duplicates().reset_index(drop=True)
    ###------pseudo survey questions
    survey['SURVEY QUESTIONS']=survey['METRIC NAME'].apply(lambda x:'Do you have answer to {}? If yes, please specify; if no,please leave the question blank'.format(x))
    #survey.to_csv('Survey_index_table.csv',index=False)

    #Generate new dataframe
    full=pd.DataFrame(list(product([company], METRIC_TABLE['METRIC NAME'].unique(),[year])),
                      columns=['COMPANY NAME','METRIC NAME','YEAR'])

    #merge with df for wanted info
    full=full.merge(df.drop('ANSWER ID',1),on=['COMPANY NAME','METRIC NAME','YEAR'],how='left')

    #return only observations with missing values
    selected=full[ ((full.VALUE.isnull()) | (full.VALUE == 'Unclear') | (full.VALUE == 'Unknown')) & (full.YEAR==year)
                 & (full['COMPANY NAME']==company)]
    selected=selected[['COMPANY NAME', 'YEAR','METRIC NAME']].sort_values(by=['COMPANY NAME', 'YEAR'])

    #Get survey questions for those missing value
    selected=selected.merge(survey,on='METRIC NAME',how='left')

    #def questionid
    def questionid(row):
        company_id=COMPANY_TABLE.loc[COMPANY_TABLE['COMPANY NAME']==row['COMPANY NAME'],'COMPANY ID'].values[0]
        metric_id=METRIC_TABLE.loc[METRIC_TABLE['METRIC NAME']==row['METRIC NAME'],'METRIC ID'].values[0]
        year_id=row.YEAR
        return int(str(year_id)+format(company_id,'04')+format(metric_id,'04'))

    #Generate questionid for each question
    selected['QUESTIONID']=selected.apply(questionid,axis=1)

    return selected

def missing_value_es(df,year,company):

    #Get metric index table
    METRIC_TABLE=df[['METRIC NAME']].drop_duplicates().sort_values(by='METRIC NAME').reset_index(drop=True)
    METRIC_TABLE['METRIC ID']= pd.Categorical(METRIC_TABLE['METRIC NAME'].astype(str)).codes
    #METRIC_TABLE.to_csv('Metric_index_tabel.csv',index=False)

    #Get company index table
    COMPANY_TABLE=df[['COMPANY NAME']].drop_duplicates().sort_values(by='COMPANY NAME').reset_index(drop=True)
    COMPANY_TABLE['COMPANY ID'] = pd.Categorical(COMPANY_TABLE['COMPANY NAME'].astype(str)).codes
    ###------pseudo email address
    COMPANY_TABLE['COMPANY EMAIL']=COMPANY_TABLE['COMPANY NAME'].apply(lambda x:'{}@gmail.com'.format(x.lower().replace(' ','')))
    #COMPANY_TABLE.to_csv('Company_index_tabel.csv',index=False)

    #Get Survey Question Table
    survey=df[['METRIC NAME']].drop_duplicates().reset_index(drop=True)
    ###------pseudo survey questions
    survey['SURVEY QUESTIONS']=survey['METRIC NAME'].apply(lambda x:'¿Tienes respuesta a {}? En caso afirmativo, por favor especifique; Si no, deje la pregunta en blanco.'.format(x))
    #survey.to_csv('Survey_index_table.csv',index=False)

    #Generate new dataframe
    full=pd.DataFrame(list(product([company], METRIC_TABLE['METRIC NAME'].unique(),[year])),
                      columns=['COMPANY NAME','METRIC NAME','YEAR'])

    #merge with df for wanted info
    full=full.merge(df.drop('ANSWER ID',1),on=['COMPANY NAME','METRIC NAME','YEAR'],how='left')

    #return only observations with missing values
    selected=full[ ((full.VALUE.isnull()) | (full.VALUE == 'Unclear') | (full.VALUE == 'Unknown')) & (full.YEAR==year)
                 & (full['COMPANY NAME']==company)]
    selected=selected[['COMPANY NAME', 'YEAR','METRIC NAME']].sort_values(by=['COMPANY NAME', 'YEAR'])

    #Get survey questions for those missing value
    selected=selected.merge(survey,on='METRIC NAME',how='left')

    #def questionid
    def questionid(row):
        company_id=COMPANY_TABLE.loc[COMPANY_TABLE['COMPANY NAME']==row['COMPANY NAME'],'COMPANY ID'].values[0]
        metric_id=METRIC_TABLE.loc[METRIC_TABLE['METRIC NAME']==row['METRIC NAME'],'METRIC ID'].values[0]
        year_id=row.YEAR
        return int(str(year_id)+format(company_id,'04')+format(metric_id,'04'))

    #Generate questionid for each question
    selected['QUESTIONID']=selected.apply(questionid,axis=1)

    return selected

###############################################################
# Access Survey Monkey API
###############################################################

# Create and send survey¶
def process(survey_title, questions_list, recipients_df):
    # 1. Access api
    client = access_api()

    # 2. Create a survey
    survey_id = create_survey(client,survey_title)
    print("survey id: %s" % survey_id)

    # 3. Get a page (first)
    # call create_page to create more pages
    page_id = get_page(client, survey_id)
    print("page id: %s" % page_id)

    # 4. Create questions on a survey page
    for question in questions_list:
        question_id = create_question(client, survey_id, page_id, question)
        print("question id: %s" % question_id)

    # 5. Creates a weblink or email collector for a given survey
    collector_id = create_collector(client, survey_id)
    print("collector id: %s" % collector_id)

    # 6. Create and format an email message
    message_id = create_message(client, collector_id)
    print("message id: %s" % message_id)

    # 7. Upload recipients to receive the message
    upload_recipients(client, collector_id, message_id, recipients_df)

    # 8. Send your message
    send_message(client, collector_id, message_id)

    # keep survey id in record for responses collection
    return survey_id

# Collect results and analysis
def after_survey(survey_id):

    # 1. Access api
    client = access_api()

    # 2. Export the Results of a Survey
    df_results = survey_result(client, survey_id)

    #3. Convert it into a DataFrame
    df_results = pd.DataFrame(df_results)

    #4. Format the column name firt by splitting the df into 2
    split_list = ['collector_id','date_created','date_modified','email_address',
                    'first_name','id','ip_address','last_name','survey_id']
    Len = len(df_results.columns)-len(split_list)
    df_split = np.split(df_results, [Len], axis=1)

    #5. Format the questions' column name
    a = df_split[0].columns
    b = a.str.slice(start=3)
    d = { a[i] : b[i] for i in range(len(a)) }
    df_results.rename(columns=d, inplace=True)

    #6. Format the questions' index name
    x = list(df_results.index)
    y = [df_results.first_name[i]+'_'+df_results.last_name[i]+'_response' for i in df_results.index]
    z = { x[i] : y[i] for i in range(len(x)) }
    df_results.rename(index=z, inplace=True)


    return df_results

# Detail in process()
###################################
# access survey monkey api
def access_api():
    client = requests.Session()
    YOUR_ACCESS_TOKEN = "A3pqR5KzWDoe48H1IbSytyqcXjZfMhrDwgMJ.mpT-RefbwzSg-2Moei9D7GU9GdfJCxfj-skejXXvB79VGASjqJN5xJh-z2qRTh6le9Q1uLtgKo2WeO2rECPkUxilEcA"
    client.headers.update({
        "Authorization": "Bearer %s" % YOUR_ACCESS_TOKEN,
        "Content-Type": "application/json"
    })
    return client

# Create a survey, return survey id
def create_survey(client, survey_title):
    payload = {"title": survey_title}
    url = "https://api.surveymonkey.com/v3/surveys"
    new = client.post(url, json=payload)
    survey_id = new.json()['id']
    return survey_id


###################################
# Get page, return page_id
def get_page(client, survey_id):
    payload = {
      "title": "",
      "description": ""
    }
    url = "https://api.surveymonkey.com/v3/surveys/%s/pages" % (survey_id)
    page = client.get(url, json=payload)
    # first page id
    page_id = page.json()['data'][0]['id']
    return page_id


###################################
# Create a page, return page_id
def create_page(client, survey_id):
    payload = {
      "title": "",
      "description": ""
    }
    url = "https://api.surveymonkey.com/v3/surveys/%s/pages" % (survey_id)
    page = client.post(url, json=payload)
    page_id = page.json()['id']
    return page_id


###################################
# Create a question on a survey page, return question id
# question format: [type, heading, [choices]]
# currently only two types of questions:
# [open_ended (text-based), single_choice]
def create_question(client, survey_id, page_id, question):
    if question[0] == 'open_ended':
        payload = {
          "headings": [
                {
                    "heading": question[1]
                }
            ],
            #"position": 1,
            "family": "open_ended",
            "subtype": "single"

        }
    elif question[0] == 'single_choice':
        choices = [{"text": c} for c in question[2]]
        payload = {
            "headings": [
                {
                    "heading": question[1]
                }
            ],
            #"position": 1,
            "family": "single_choice",
            "subtype": "vertical",
            "answers": {
                "choices": choices,
                "other":[
                        {
                            "text": "Other",
                            "num_chars": 100,
                            "num_lines": 1
                        }
                ]
            }
        }
    else:
        # undefined
        payload = {}

    url = "https://api.surveymonkey.com/v3/surveys/%s/pages/%s/questions" % (survey_id, page_id)
    q = client.post(url, json=payload)
    question_id = q.json()['id']
    return question_id


###################################
# Creates a weblink or email collector
# for a given survey, return collector_id
def create_collector(client, survey_id):
    payload = {
     #"type": "weblink"
      "type": "email"
    }
    url = "https://api.surveymonkey.com/v3/surveys/%s/collectors" % (survey_id)
    collector = client.post(url, json=payload)
    collector_id = collector.json()['id']
    return collector_id


###################################
# Create and format an email message, return message_id
def create_message(client, collector_id):
    payload = {
      "type": "invite"
    }
    url = "https://api.surveymonkey.com/v3/collectors/%s/messages" % (collector_id)
    message = client.post(url, json=payload)
    message_id = message.json()['id']
    return message_id


###################################
# Upload recipients to receive the message
def upload_recipients(client, collector_id, message_id, recipients_df):
    # ex. [{"email":"xxx", "first_name":"xx", "last_name":"xx"}]
    contacts = json.loads(recipients_df.to_json(orient='records'))
    payload = {
      "contacts" : contacts
    }

    url = "https://api.surveymonkey.com/v3/collectors/%s/messages/%s/recipients/bulk" % (collector_id, message_id)
    recipients = client.post(url, json=payload)


###################################
# Send your message (default one minute later)
def send_message(client, collector_id, message_id, lag='00:01'):
    now = datetime.datetime.utcnow()
    sche_time = str(now).replace(' ','T') + '+' + lag
    payload = {
      "scheduled_date": sche_time
    }
    url = "https://api.surveymonkey.com/v3/collectors/%s/messages/%s/send" % (collector_id, message_id)
    r = client.post(url, json=payload)


###################################
# Export the Results of a Survey
def survey_result(client, survey_id):

    # This call returns the survey’s design with all question ids and answer
    # option ids, as well as the values associated with them
    questions = client.get('https://api.surveymonkey.net/v3/surveys/%s/details'%survey_id)

    # map question id to question text (and choices if exist)
    questions_map = {}
    for q in questions.json()['pages'][0]['questions']:
        ques_type = q['family']
        questions_map[q['id']] = [q['headings'][0]['heading'],ques_type]
        if ques_type == 'single_choice':
            questions_map[q['id']].append({x['id']:x['text'] for x in q['answers']['choices']})

    # fetch the first 100 responses to your survey
    responses = client.get('https://api.surveymonkey.net/v3/surveys/%s/responses/bulk?page=1&per_page=100'%survey_id)

    # build a dataframe of responses data
    rows = list()
    # id: respondent ID
    columns = ['survey_id','id','collector_id','date_created','date_modified','ip_address',
               'metadata','pages']
    for r in responses.json()['data']:
        row = {k: r.get(k, None) for k in columns}
        #row=pd.DataFrame(row)
        #print(type(row))
        contact_info = row.pop('metadata')
        if contact_info:
            row['email_address'] = contact_info['contact']['email']['value']
            row['first_name'] = contact_info['contact']['first_name']['value']
            row['last_name'] = contact_info['contact']['last_name']['value']

        answers_info = row.pop('pages')
        if answers_info:
            i = 0
            for a in answers_info[0]['questions']:
                question = questions_map[a['id']]
                if question[1] == 'open_ended':
                    row['Q'+str(i)+'_'+question[0]] = a['answers'][0]['text']
                elif question[1] == 'single_choice':
                    choice_id = a['answers'][0]['choice_id']
                    row['Q'+str(i)+'_'+question[0]] = question[2][choice_id]
                else:
                    pass   # undifined
                i += 1

        rows.append(row)
    df = rows
    return df

###############################################################
# Generate Result Table
###############################################################

def result_table(selected_df,df_result_answer, question_list):

    drop_list_1 = ['collector_id','date_created','date_modified','email_address',
                    'first_name','id','ip_address','last_name','survey_id']
    df_result_answer = df_result_answer.drop(drop_list_1, axis =1)
    df_result_answer = df_result_answer.transpose()
    df_result_answer = df_result_answer.reset_index(inplace=False)
    df_result_answer.rename(columns={'index':'SURVEY QUESTIONS'}, inplace=True)

    question_list = pd.DataFrame(question_list)[1]
    result_table = selected_df.merge(question_list,left_on=['SURVEY QUESTIONS'],right_on=[1],how='inner')
    drop_list_2 = ['METRIC NAME',1,'QUESTIONID']
    result_table = result_table.drop(drop_list_2, axis =1)

    result_table = result_table.merge(df_result_answer,on=['SURVEY QUESTIONS'], how='inner')
    result_table = result_table.groupby('SURVEY QUESTIONS').first().reset_index()

    return result_table
