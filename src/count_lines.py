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


#Path to repository should be the argument to script
print("Args: " + str(sys.argv))

#The script itself is the first argument, the path is the second, and extensions is the third
path_to_repo = sys.argv[1] 
print('Repo: ' + path_to_repo)

extensions = [x.strip() for x in sys.argv[2].split(',')]
print('Extensions: ' + str(extensions))

repo = Repo(path_to_repo)
git = repo.git
git.checkout('master')
git.pull()
commits = list(repo.iter_commits())

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
        dates.append(datetime.datetime.fromtimestamp(date))
        result = count_lines(extensions)
        for i in range(len(result)):
            results[i].append(result[i][1])

        print(datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d %H:%M') + ': ' + str(result))

f, ax = plt.subplots(1, sharex='all', sharey='all')
xfmt = md.DateFormatter('%Y-%m-%d')

for result in results:
    ax.plot(dates, result)

ax.xaxis.set_major_formatter(xfmt)
f.autofmt_xdate()
plt.savefig("results.jpg")
plt.show()