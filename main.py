import requests
from flask import Flask, render_template

app = Flask(__name__)
numberOfQuestions = 5
low = 1200
high = 1500
minSubmissions = 10000
username = "roferrlls"


@app.route('/')
def home():
    return render_template('load.html')


@app.route('/result', methods=["GET", "POST"])
def getProblems():
    resp = requests.get('https://codeforces.com/api/problemset.problems')
    submissions = processSubmissions(getProfileSubmissions(username))
    data = resp.json()
    problems = data["result"]["problems"]
    problemStatistics = data["result"]["problemStatistics"]
    problemList = constructList(problems, problemStatistics)
    restructureProblemsList(problemList)
    problemList = cleanUp(problemList, low, high)
    recommendations = generateRecommendations(problemList, submissions, minSubmissions)
    return render_template("list.html", data=recommendations)


def getProfileSubmissions(username):
    resp = requests.get('https://codeforces.com/api/user.status?handle=' + username)
    data = resp.json()
    return data


def constructList(problems, problemStatistics):
    problemList = []
    for i in range(0, len(problems)):
        contestId = problems[i]["contestId"]
        index = problems[i]["index"]
        name = problems[i]["name"]
        rating = 0
        if "rating" in problems[i]:
            rating = problems[i]["rating"]
        solvedCount = problemStatistics[i]["solvedCount"]
        d = {"contestId": contestId, "index": index, "name": name, "solvedCount": solvedCount, "rating": rating}
        problemList.append(d)
    return problemList


def restructureProblemsList(problemList):
    problemList.sort(reverse=True, key=msort)


def msort(problem):
    return int(problem["solvedCount"])


def cleanUp(problemList, low, high):
    res = []
    for problem in problemList:
        if low <= problem["rating"] <= high:
            res.append(problem)
    return res


def processSubmissions(submissions):
    res = {"test"}
    submissions = submissions["result"]
    for sub in submissions:
        if sub["verdict"] == "OK":
            contestId = sub["problem"]["contestId"]
            index = sub["problem"]["index"]
            res.add(str(contestId) + str(index))
    return res


def generateRecommendations(problemList, submissions, solvedCountStart):
    res = []
    # TODO find starting index efficiently
    for problem in problemList:
        if problem["solvedCount"] > solvedCountStart:
            continue
        id = str(problem["contestId"]) + str(problem["index"])
        if id in submissions:
            continue
        problem["url"] = generateURL(problem["contestId"], problem["index"])
        res.append(problem)
        if len(res) >= numberOfQuestions:
            break
    return res


def generateURL(contestId, index):
    url = "https://codeforces.com/problemset/problem/" + str(contestId) + "/" + str(index)
    return url


if __name__ == "__main__":
    app.run(debug=True)

# TODO error handling, invalid response from CF
