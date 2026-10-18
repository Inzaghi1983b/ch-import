import json
import os
import sys

fx = os.environ["FIXDIR"]
a = sys.argv[1:]


def load(n):
    return open(os.path.join(fx, n), encoding="utf-8").read()


def log(t):
    open(os.path.join(fx, "writes.log"), "a").write(t + "\n")


if a[0] == "api":
    path = [x for x in a[1:] if x.startswith("repos/")][0]
    if "-X" in a and "check-runs" in path:
        concl = [x.split("=", 1)[1] for x in a if x.startswith("conclusion=")][0]
        log(("check-patch " if a[a.index("-X") + 1] == "PATCH" else "check ") + concl)
    elif "/actions/runs/" in path:
        print(load("run.json"))
    elif "/check-runs" in path:
        print(load("checks.json"))
    elif path.endswith("/files"):
        d = json.loads(load("files.json"))
        for i in range(0, max(len(d), 1), 30):
            print(json.dumps(d[i : i + 30]))
    elif "/pulls/" in path:
        print(load("pr.json"))
    elif path.count("/") == 2:
        print(load("repo.json"))
    else:
        print("unbekannt", a, file=sys.stderr)
        sys.exit(2)
elif a[:2] == ["pr", "ready"]:
    log("ready")
elif a[:2] == ["pr", "merge"] and "--disable-auto" in a:
    log("disable-auto")
elif a[:2] == ["pr", "merge"] and "--auto" in a:
    log("auto " + a[a.index("--match-head-commit") + 1])
else:
    print("unbekannter Aufruf", a, file=sys.stderr)
    sys.exit(2)
