#!/usr/bin/env python
# coding: utf-8

# In[1]:


import google.generativeai as genai
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv('gemini.env')

api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')


api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
else:
    raise ValueError("API key is not set")


# In[2]:


import pandas as pd
import requests
import genai 
answers_path = "Exam1-Answers.xlsx"
questions_path = "Exam1-Q1.xlsx"
output_path = "Processed_Exam_Data.xlsx"


answers_df = pd.read_excel(answers_path, sheet_name='Sheet1')
questions_df = pd.read_excel(questions_path, sheet_name='Question')
queries_df = pd.read_excel(questions_path, sheet_name='Query')

print("Answers DataFrame Columns:", answers_df.columns)
print("Questions DataFrame Columns:", questions_df.columns)
print("Queries DataFrame Columns:", queries_df.columns)


merged_df = pd.merge(questions_df, answers_df, on='QNo', how='inner')


print("Merged DataFrame Columns:", merged_df.columns)


# In[3]:


answers_path = "Exam1-Answers.xlsx"
questions_path = "Exam1-Q1.xlsx"
output_path_method1 = "Processed_Exam_Data_Method1.xlsx"
output_path_method2 = "Processed_Exam_Data_Method2.xlsx"
output_path_method3 = "Processed_Exam_Data_Method3.xlsx"

answers_df = pd.read_excel(answers_path, sheet_name='Sheet1')
questions_df = pd.read_excel(questions_path, sheet_name='Question')
queries_df = pd.read_excel(questions_path, sheet_name='Query')

print("Answers DataFrame Columns:", answers_df.columns)
print("Questions DataFrame Columns:", questions_df.columns)
print("Queries DataFrame Columns:", queries_df.columns)

merged_df = pd.merge(questions_df, answers_df, on='QNo', how='inner')

print("Merged DataFrame Columns:", merged_df.columns)

def assess_answer_method1(question, ref_answer, student_answer):
    prompt = f"Question: {question}\nExpected Answer: {ref_answer}\nStudent Answer: {student_answer}\n\
    Assess how close is the 'Student Answer' to the 'Expected Answer' and\
    assign a 'closeness score' to the student answer on a scale 0 to 1 and then provide your reasoning for the score in not more than 50 words.\
    Output should be as follows: Closeness Score: Score; followed, in the next line, by Reasoning: Reason."

    response = model.generate_content(prompt)
    if response.text:
        response_text = response.text.split('\n')
        if len(response_text) >= 2:
            compliance_score = response_text[0].split(': ')[-1]
            assessment_reason = response_text[1].split(': ')[-1]
        else:
            compliance_score = "NA"
            assessment_reason = "Model generated empty response"
    else:
        compliance_score = "NA"
        assessment_reason = "Model generated no response"
    return compliance_score, assessment_reason

def assess_answer_method2(question, ref_answer, student_answer, queries_df):
    results = {}
    for index, row in queries_df.iterrows():
        if 'Method2' in row['Method-key_Query-key']:
            query_key = row['Method-key_Query-key']
            query_name = row['Value']
            prompt = f"Question: {question}\nReference Answer: {ref_answer}\nStudent Answer: {student_answer}\nQuery: {query_name}\n\
            Give your answer in the following format: Response: yes or no, in the next line Reasoning: Reason in not more than 50 words."

            response_text = model.generate_content(prompt)

            try:
                response_lines = response_text.text.split('\n')
            except AttributeError:
                response_lines = []

            response_line = response_lines[0].split(': ')[-1].strip() if len(response_lines) > 0 else "N/A"
            reason_line = response_lines[1].split(': ')[-1].strip() if len(response_lines) > 1 else "N/A"
            results[query_key] = {
                "Query": query_name,
                "Response": response_line,
                "Reason": reason_line
            }
    return results

def assess_answer_method3(question, student_answer, queries_df):
    results = []
    for index, row in queries_df.iterrows():
        if 'Method3' in row['Method-key_Query-key']:
            query_key = row['Method-key_Query-key']
            query_name = row['Value']
            prompt = f"Question: {question}\nStudent Answer: {student_answer}\nQuery: {query_name}\n\
            Give your answer in the following format: Response: yes or no, in the next line Reasoning: Reason in not more than 50 words."

            response_text = model.generate_content(prompt)

            try:
                response_lines = response_text.text.split('\n')
            except AttributeError:
                response_lines = []

            response_line = response_lines[0].split(': ')[-1].strip() if len(response_lines) > 0 else "N/A"
            reason_line = response_lines[1].split(': ')[-1].strip() if len(response_lines) > 1 else "N/A"
            results.append({
                "Query Key": query_key,
                "Query": query_name,
                "Response": response_line,
                "Reason": reason_line
            })
    return results

method1_data = []
method2_data = []
method3_data = []

for index, row in merged_df.iterrows():
    student_no = row['StudentNo'] 
    question_no = row['QNo']
    question = row['Value']
    ref_answer = row['Ref_Ans']
    student_answer = row['StuAns']
    
    # Method 1
    compliance_score, assessment_reason = assess_answer_method1(question, ref_answer, student_answer)
    method1_data.append({
        "Student No": student_no,
        "Question No": question_no,
        "Question": question,
        "Reference Answer": ref_answer,
        "Student Answer": student_answer,
        "Compliance Score": compliance_score,
        "Assessment Reason": assessment_reason
    })
    
    # Method 2
    method2_assessment = assess_answer_method2(question, ref_answer, student_answer, queries_df)
    for query, result in method2_assessment.items():
        method2_data.append({
            "Student No": student_no,
            "Question No": question_no,
            "Question": question,
            "Reference Answer": ref_answer,
            "Student Answer": student_answer,
            "Query Key": query,
            "Query": result["Query"],
            "Response": result["Response"],
            "Reason": result["Reason"]
        })
    
    # Method 3
    method3_assessment = assess_answer_method3(question, student_answer, queries_df)
    for result in method3_assessment:
        method3_data.append({
            "Student No": student_no,
            "Question No": question_no,
            "Question": question,
            "Student Answer": student_answer,
            "Query Key": result["Query Key"],
            "Query": result["Query"],
            "Response": result["Response"],
            "Reason": result["Reason"]
        })

method1_df = pd.DataFrame(method1_data)
method2_df = pd.DataFrame(method2_data)
method3_df = pd.DataFrame(method3_data)

method1_df.to_excel(output_path_method1, index=False)
method2_df.to_excel(output_path_method2, index=False)
method3_df.to_excel(output_path_method3, index=False)

print("Processed exam data saved to Method 1:", output_path_method1)
print("Processed exam data saved to Method 2:", output_path_method2)
print("Processed exam data saved to Method 3:", output_path_method3)


# In[ ]:


import os
from dotenv import load_dotenv
import pandas as pd
import google.generativeai as genai

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

answers_path = "Exam1-Answers.xlsx"
questions_path = "Exam1-Q1.xlsx"
output_path_method1 = "Processed_Exam_Data_Method1.xlsx"
output_path_method2 = "Processed_Exam_Data_Method2.xlsx"
output_path_method3 = "Processed_Exam_Data_Method3.xlsx"

answers_df = pd.read_excel(answers_path, sheet_name='Sheet1')
questions_df = pd.read_excel(questions_path, sheet_name='Question')
queries_df = pd.read_excel(questions_path, sheet_name='Query')

print("Answers DataFrame Columns:", answers_df.columns)
print("Questions DataFrame Columns:", questions_df.columns)
print("Queries DataFrame Columns:", queries_df.columns)

merged_df = pd.merge(questions_df, answers_df, on='QNo', how='inner')

print("Merged DataFrame Columns:", merged_df.columns)

def assess_answer_method1(question, ref_answer, student_answer, model):
    prompt = f"Question: {question}\nExpected Answer: {ref_answer}\nStudent Answer: {student_answer}\n\
    Assess how close is the 'Student Answer' to the 'Expected Answer' and\
    assign a 'closeness score' to the student answer on a scale 0 to 1 and then provide your reasoning for the score in not more than 50 words.\
    Output should be as follows: Closeness Score: Score; followed, in the next line, by Reasoning: Reason."

    response = model.generate_content(prompt)
    if response.text:
        response_text = response.text.split('\n')
        if len(response_text) >= 2:
            compliance_score = response_text[0].split(': ')[-1]
            assessment_reason = response_text[1].split(': ')[-1]
        else:
            compliance_score = "NA"
            assessment_reason = "Model generated empty response"
    else:
        compliance_score = "NA"
        assessment_reason = "Model generated no response"
    return compliance_score, assessment_reason

def assess_answer_method2(question, ref_answer, student_answer, queries_df, model):
    results = {}
    for index, row in queries_df.iterrows():
        if 'Method2' in row['Method-key_Query-key']:
            query_key = row['Method-key_Query-key']
            query_name = row['Value']
            prompt = f"Question: {question}\nReference Answer: {ref_answer}\nStudent Answer: {student_answer}\nQuery: {query_name}\n\
            Give your answer in the following format: Response: yes or no, in the next line Reasoning: Reason in not more than 50 words."

            response_text = model.generate_content(prompt)

            try:
                response_lines = response_text.text.split('\n')
            except AttributeError:
                response_lines = []

            response_line = response_lines[0].split(': ')[-1].strip() if len(response_lines) > 0 else "N/A"
            reason_line = response_lines[1].split(': ')[-1].strip() if len(response_lines) > 1 else "N/A"
            results[query_key] = {
                "Query": query_name,
                "Response": response_line,
                "Reason": reason_line
            }
    return results

def assess_answer_method3(question, student_answer, queries_df, model):
    results = []
    for index, row in queries_df.iterrows():
        if 'Method3' in row['Method-key_Query-key']:
            query_key = row['Method-key_Query-key']
            query_name = row['Value']
            prompt = f"Question: {question}\nStudent Answer: {student_answer}\nQuery: {query_name}\n\
            Give your answer in the following format: Response: yes or no, in the next line Reasoning: Reason in not more than 50 words."

            response_text = model.generate_content(prompt)

            try:
                response_lines = response_text.text.split('\n')
            except AttributeError:
                response_lines = []

            response_line = response_lines[0].split(': ')[-1].strip() if len(response_lines) > 0 else "N/A"
            reason_line = response_lines[1].split(': ')[-1].strip() if len(response_lines) > 1 else "N/A"
            results.append({
                "Query Key": query_key,
                "Query": query_name,
                "Response": response_line,
                "Reason": reason_line
            })
    return results

method1_data = []
method2_data = []
method3_data = []

for index, row in merged_df.iterrows():
    student_no = row['StudentNo'] 
    question_no = row['QNo']
    question = row['Value']
    ref_answer = row['Ref_Ans']
    student_answer = row['StuAns']
    
    # Method 1
    compliance_score, assessment_reason = assess_answer_method1(question, ref_answer, student_answer, model)
    method1_data.append({
        "Student No": student_no,
        "Question No": question_no,
        "Question": question,
        "Reference Answer": ref_answer,
        "Student Answer": student_answer,
        "Compliance Score": compliance_score,
        "Assessment Reason": assessment_reason
    })
    
    # Method 2
    method2_assessment = assess_answer_method2(question, ref_answer, student_answer, queries_df, model)
    for query, result in method2_assessment.items():
        method2_data.append({
            "Student No": student_no,
            "Question No": question_no,
            "Question": question,
            "Reference Answer": ref_answer,
            "Student Answer": student_answer,
            "Query Key": query,
            "Query": result["Query"],
            "Response": result["Response"],
            "Reason": result["Reason"]
        })
    
    # Method 3
    method3_assessment = assess_answer_method3(question, student_answer, queries_df, model)
    for result in method3_assessment:
        method3_data.append({
            "Student No": student_no,
            "Question No": question_no,
            "Question": question,
            "Student Answer": student_answer,
            "Query Key": result["Query Key"],
            "Query": result["Query"],
            "Response": result["Response"],
            "Reason": result["Reason"]
        })

method1_df = pd.DataFrame(method1_data)
method2_df = pd.DataFrame(method2_data)
method3_df = pd.DataFrame(method3_data)

method1_df.to_excel(output_path_method1, index=False)
method2_df.to_excel(output_path_method2, index=False)
method3_df.to_excel(output_path_method3, index=False)

print("Processed exam data saved to Method 1:", output_path_method1)
print("Processed exam data saved to Method 2:", output_path_method2)
print("Processed exam data saved to Method 3:", output_path_method3)


# In[ ]:




