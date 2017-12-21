import sys
import datetime
import glob
from matplotlib import pyplot as plt
import matplotlib.dates as md
from git import Repo

def count_lines(extensions):
    results = []
    for ext in extensions:
        count = 0
        files = glob.glob(path_to_repo + '/**/*' + ext, recursive=True)
        for filename in files:
            try:
                with open(filename) as f:
                    for l in f:
                        if not l.isspace():
                            count += 1
            except:
                pass
    
        results.append((ext,count))
    return results

def plot_results(dates, results):
    f, ax = plt.subplots(1, sharex='all', sharey='all')
    xfmt = md.DateFormatter('%Y-%m-%d')

    formatted_dates = [datetime.datetime.fromtimestamp(date) for date in dates]
    for result in results:
        ax.plot(formatted_dates, result)

    ax.xaxis.set_major_formatter(xfmt)
    f.autofmt_xdate()
    plt.savefig("results.jpg")
    plt.show()

def save_results(dates, results):
    with open('results.txt', 'w') as f:
        f.write(','.join([str(date) for date in dates]) + '\n')
        for result in results:
            f.write(','.join([str(count) for count in result]) + '\n')

#Path to repository should be the argument to script
print("Args: " + str(sys.argv))

#The script itself is the first argument, "full or increment is the second", the path is the next, and extensions is the last
type = sys.argv[1]

path_to_repo = sys.argv[2] 
print('Repo: ' + path_to_repo)

extensions = [x.strip() for x in sys.argv[3].split(',')]
print('Extensions: ' + str(extensions))

repo = Repo(path_to_repo)
git = repo.git
git.checkout('master')
git.pull()
commits = list(repo.iter_commits())

if type == 'full':
    max_interval_seconds = 3600 * 24 * 30
    interval_seconds = 3600 * 24
    date = None
    filtered_commits = []
    print("Filtered commit dates:")

    results = [[] for ext in extensions]
    dates = []
    for commit in commits:
        if date == None or commit.committed_date < (date - interval_seconds) or commits[-1] == commit:
            date = commit.committed_date

            #Increase interval between commits
            interval_seconds = min(max_interval_seconds, interval_seconds * 2) 

            filtered_commits.append(commit)
            git.checkout(commit.hexsha, force=True)
            dates.append(date)
            result = count_lines(extensions)
            for i in range(len(result)):
                results[i].append(result[i][1])

            print(datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M') + ': ' + str(result))
    save_results(dates, results)
    plot_results(dates, results)

elif type == 'increment':
    with open('results.txt', 'r') as f:
        lines = list(f)
    dates = [int(s) for s in lines[0].split(',')]
    results = [[int(s) for s in l.split(',')] for l in lines[1:]]
    dates.insert(0,commits[0].committed_date)
    current_count = count_lines(extensions)
    for i in range(len(results)):
        results[i].insert(0,current_count[i][1])

    save_results(dates, results)
    plot_results(dates, results)

else:
    print("Unknown command: " + type + " Allowed commands: full, increment")