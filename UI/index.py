

from robobrowser import RoboBrowser
import os
from flask import Flask,request,render_template

app = Flask(__name__)

folder_for_skill = os.path.join(app.instance_path, "static")

def process_input(text):
    list_of_words = text.split(" ")
    final_string = ""
    for i,j in enumerate(list_of_words):
        if i != len(list_of_words) - 1:
            final_string += j + "+"
        else:
            final_string += j
    return final_string

def get_the_list_of_text(how_many_jobs, job, location):
    multiple_of_fifteen = int(how_many_jobs / 15)
    required_list = []
    
    j = process_input(job)
    l = process_input(location)
    if multiple_of_fifteen != 0:
        for i in range(multiple_of_fifteen):
            if i == 0:
                url = "https://indeed.com/jobs?q={0}&l={1}".format(j,l)
            else:
                url = "https://indeed.com/jobs?q={0}&l={1}".format(j,l) + "&start=" + str(i * 10)
            browser = RoboBrowser()
            browser.open(url)
            listOfJobs = browser.find_all("div", {"class":"jobsearch-SerpJobCard"})
            #print(len(listOfJobs))
            for p in range(len(listOfJobs)):
                browser.follow_link(listOfJobs[p].find("h2").find("a"))
                required_text = browser.find("div", {"class":"jobsearch-JobComponent-description"}).text
                browser.back()
                required_list.append(required_text)
    else:
        url = "https://indeed.com/jobs?q={0}&l={1}".format(j,l)
        browser = RoboBrowser()
        browser.open(url)
        listOfJobs = browser.find_all("div", {"class":"jobsearch-SerpJobCard"})
        #print(len(listOfJobs))
        for i in range(int(how_many_jobs)):
            browser.follow_link(listOfJobs[i].find("h2").find("a"))
            required_text = browser.find("div", {"class":"jobsearch-JobComponent-description"}).text
            browser.back()
            required_list.append(required_text)
    return required_list
def read_skills_file():
    with open(folder_for_skill + "/linkedin skill.txt", "r", encoding="utf-8") as file:
        skills = file.read()
    skills = skills.split("\n")
    skills = [i.lower() for i in skills]
    return skills

stopwords = ['i', 'me', 'my', 'myself', 'we',  'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 
             'your', 'yours', 'yourself', 'yourselves','he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', 
             "it's", 'its', 'itself', 'they', 'them','their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 
             "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',  
             'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 
             'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 
             'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 
             'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 
             'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don',
             "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', 
             "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn',
             "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn',
             "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't",'do', 'does', 'did', 'doing']
def clean_job_desc(list_of_job_desc):
    combined_job_description = " ".join(list_of_job_desc)
    combined_job_description = combined_job_description.replace("\n", " ")
    combined_job_description = combined_job_description.lower()
    combined_job_description = combined_job_description.split(" ")
    combined_job_description = [i for i in combined_job_description if i not in stopwords]
    return combined_job_description

def compute_single_word_skills(req):
    skills = read_skills_file()
    c = clean_job_desc(req)
    single_word_skills = []
    for skill in skills:
        s = skill.split(" ")
        if len(s) == 1:
            single_word_skills.append(skill)
            
    single_word_skills_in_job = {}

    for w in c:
        if w in single_word_skills:
            if w in single_word_skills_in_job:
                single_word_skills_in_job[w] += 1
            else:
                single_word_skills_in_job[w] = 1
    return single_word_skills_in_job
def final_function_to_return_top_skills(req):
    combined_job_description = clean_job_desc(req)
    skills = read_skills_file()
    bigrams = []
    for i in range(0, len(combined_job_description)-1):
            bigrams.append((combined_job_description[i], combined_job_description[i+1]))
    skills_dict2 = {}
    for bi in bigrams:
        w = " ".join(bi)
        if w in skills:
            if w in skills_dict2:
                skills_dict2[w] += 1
            else:
                skills_dict2[w] = 1

    single_word_skills = compute_single_word_skills(req)
    skills_dict2.update(single_word_skills)
    sorted_skills_dict = dict(sorted(skills_dict2.items(), key=lambda item: item[1], reverse = True))
    return sorted_skills_dict

def final_processing(required_dict):
    s = sum(required_dict.values())
    for k in required_dict.keys():
        required_dict[k] = round((required_dict[k] / s)*100,2)
    unigram = {}
    bigram = {}
    for key in required_dict.keys():
        if len(key.split()) == 1:
            unigram[key] = required_dict[key]
        else:
            bigram[key] = required_dict[key]
    unigram_sorted = dict(sorted(unigram.items(), key=lambda item: item[1], reverse = True))
    bigram_sorted = dict(sorted(bigram.items(), key=lambda item: item[1], reverse = True))
    u = {i:unigram_sorted[i] for i in list(unigram_sorted.keys())[:10] if i not in ["", " "]}
    b = {i:bigram_sorted[i] for i in list(bigram_sorted.keys())[:10] if i not in ["", " "]}

    return [u,b]


@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("jobType")
        no_of_jobs = request.form.get("noOfJobs")
        location = request.form.get("location")
        req = get_the_list_of_text(int(no_of_jobs), title, location)
        dict_to_process = final_function_to_return_top_skills(req)
        p1 = final_processing(dict_to_process)[0]
        p2 = final_processing(dict_to_process)[1]
        return render_template("index.html",prediction_dictionary = [p1,p2])
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0")

