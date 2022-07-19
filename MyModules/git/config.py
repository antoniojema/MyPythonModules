from pathlib import Path

class Config:
    idx = {"repos" : 0, "search": 1, "ignore": 2}
    
    def __init__(self, repos = [], search = [], ignore = []):
        self.repos  = {Path(d) for d in repos}
        self.search = {Path(d) for d in search}
        self.ignore = {Path(d) for d in ignore}
        self.all = [self.repos, self.search, self.ignore]
    
    def isEmpty(self) -> bool:
        return (len(self.repos) == 0 and len(self.search) == 0 and len(self.ignore) == 0)
    
    def add(self, which, d):
        if type(which) is str:
            which = Config.idx[which]
        self.all[which].add(Path(d))
    
    def remove(self, which, d):
        if type(which) == str:
            which = Config.idx[which]
        self.all[which].remove(Path(d))

    def addRepo(self, d):
        self.add(0, Path(d))
    
    def addSearch(self, d):
        self.add(1, Path(d))
    
    def addIgnore(self, d):
        self.add(2, Path(d))

    def removeRepo(self, d):
        self.remove(0, Path(d))
    
    def removeSearch(self, d):
        self.remove(1, Path(d))
    
    def removeIgnore(self, d):
        self.remove(2, Path(d))
    
    def reset(self):
        self.repos.clear()
        self.search.clear()
        self.ignore.clear()
