"""Flag frontend code that handles only the happy path.

Usage:
    python3 state_check.py [PATH ...]    # files or folders, default: the current folder

Scans .tsx .jsx .ts .js .mjs .vue .svelte files. Skips node_modules, build output, vendor code,
hidden folders, fixtures, tests, stories and files over 300 KB. Needs only Python 3.

Each hit is a place to look, not proof. Prints nothing and exits 0 when nothing is found.
Exits 1 when an error or a warning is found. Hints never change the exit code.

To silence one hit, put a comment containing "ui-states-ignore" and the reason on that line
or the line above. To skip a whole file, put "ui-states-ignore-file" anywhere in it.
"""

import json
import os
import re
import sys
from pathlib import Path

# ---------- Files ----------

CODE_EXTENSIONS = {".tsx", ".jsx", ".ts", ".js", ".mjs", ".vue", ".svelte"}
JSX_EXTENSIONS = {".tsx", ".jsx", ".js"}
MARKUP_EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte"}
SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", "out", "coverage", ".next", ".nuxt",
    "fixtures", "__fixtures__", "vendor", "vendors",
}  # folders starting with "." are skipped too
MAX_BYTES = 300_000  # bigger files are bundles or generated code
SKIP_FILE = re.compile(  # tests, stories, types, and bundles like vendor.js, vendors~main.js, app.vendor.js
    r"\.(test|spec|stories|story)\.\w+$|\.d\.ts$|\.min\.js$"
    r"|^vendors?(?:[~.][\w~.-]*)?\.m?js$|\.vendors?\.m?js$"
)
IGNORE_LINE = "ui-states-ignore"
IGNORE_FILE = "ui-states-ignore-file"
SEVERITY_ORDER = {"error": 0, "warn": 1, "hint": 2}

# ---------- Patterns ----------

BLOCK_COMMENT = re.compile(r"/\*.*?\*/|<!--.*?-->", re.DOTALL)
LINE_COMMENT = re.compile(r"(?<![:\w\"'`\\])//[^\n]*")  # not the // in "https://"
JSX_RETURN = re.compile(r"return\s*\(?\s*<[A-Za-z]")  # markup inside a plain .js file

DATA_SOURCE = re.compile(
    r"(?<![\w.$])fetch\(\s*[^)\s]|\buse(?:Infinite)?Query\s*(?:<[^()]*>)?\(|\buseSWR\w*\(|\baxios(?:\.\w+)?\("
    r"|\bcreateResource\(|\buseFetch\(|\$fetch\(|\buseAsyncData\("
)
RAW_FETCH = re.compile(r"(?<![\w.$])fetch\(\s*[^)\s]")  # fetch() with no argument is a local function
STRING = re.compile(r"\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'|`(?:\\.|[^`\\])*`")
# Code that handles an error. Throwing is not handling: it hands the error on, and only counts
# when a boundary or a route error file catches it (ERROR_DELEGATED, has_route_error_file).
ERROR_HANDLED = re.compile(  # run on code with strings blanked
    r"\.catch\("                                         # promise.catch(
    r"|\bcatch\s*[({]"                                    # catch (e) { or catch {
    r"|\b(?:isError|isRefetchError|isLoadingError|isFetchNextPageError)\b"
    r"|\{[^{}]*\berror\b[^{}]*\}\s*=\s*use\w+\("          # const { error } = useQuery(
    r"|\.(?:error|isError)\b"                               # query.error, result.isError
    r"|\{\s*!?\w*[eE]rror\w*\s*(?:&&|\?)"                 # {error && …} or {loadError ? …}
    r"|\bif\s*\(\s*!?\w*[eE]rror\w*\s*\)"                # if (error)
    r"|\bset\w*(?:Error|Fail)\w*\("                       # setError(…), setFailed(…)
    r"|\bonError\s*:"                                      # an onError option, not an onError= prop
    r"|\{:catch|onErrorCaptured"
)
ERROR_STATUS = re.compile(  # status === 'error' or request: 'error' in a state model
    r"\b(?:status|request|state|kind|phase)\s*(?:===?|!==?|:)\s*[\"']error[\"']"
)
ERROR_DELEGATED = re.compile(  # a boundary or a suspense hook owns the error state
    r"ErrorBoundary|useSuspense\w*Query|throwOnError|catchError|svelte:boundary"
)
LOADING = re.compile(r"loading|pending|isFetching", re.IGNORECASE)

LEAKED_ZERO = re.compile(r"\{\s*[\w$?.\[\]]+\.(?:length|size)\s*&&")  # a bare {count && …} is left to jsx-no-leaked-render
EMPTY_CATCH = re.compile(  # catch {} or catch (e) { console.error(e) }
    r"\bcatch\s*(?:\([^)]*\))?\s*\{\s*"
    r"(?:console\.\w+\([^()]*(?:\([^()]*\)[^()]*)*\)\s*;?\s*)?\}"
)
SWALLOWING_THEN_CATCH = re.compile(  # .catch(() => {}) .catch(() => null) .catch(console.error)
    r"\.catch\(\s*(?:console\.\w+"
    r"|(?:\(\s*\w*\s*\)|\w+)\s*=>\s*(?:\{\s*\}|null|undefined"
    r"|\{\s*console\.\w+\([^()]*\)\s*;?\s*\}|console\.\w+\([^()]*\)))\s*\)"
)
CATCH_TO_EMPTY = re.compile(r"\.catch\(\s*(?:\(\s*\w*\s*\)|\w+)\s*=>\s*(?:\[\s*\]|\(\s*\{\s*\}\s*\))")
EMPTY_DEFAULT = re.compile(
    r"\{[^{}]*\bdata\s*(?::\s*\w+\s*)?=\s*\[\s*\][^{}]*\}\s*=\s*(use\w*(?:Query|SWR)\w*)\("
)
STATEMENT_AHEAD = re.compile(r"[^<{};]*;")  # { arr.length && doIt(arr); } is a statement, not a render
TERNARY_AHEAD = re.compile(r"(?:[^<{}?]|\?[.?])*\?(?![.?])")  # a ? before any markup: the && is a ternary test
FALLBACK_TRY = re.compile(r"JSON\.parse|localStorage|sessionStorage|decodeURI|new URL\(")
BODY_PARSE = re.compile(r"\.(?:json|text)\(\)\s*$")  # res.json().catch(): parsing an error body
WHOLE_RESULT = re.compile(  # the whole query result is passed on, and its error goes with it
    r"\b(?:const|let)\s+\w+\s*=\s*use\w*(?:Query|SWR)\w*\s*(?:<[^()]*>)?\("
    r"|\bUse\w*QueryResult\b|\bSWRResponse\b|\.\.\.\w*(?:[qQ]uery|[rR]esult)\b"
)
CHECKS_OK = re.compile(r"\.ok\b|\.status\b")
JSON_CALL = re.compile(r"\.json\(\)")
HTML_TAG = re.compile(r"<[A-Za-z][^<>]*>")
ROLE_ALERT = re.compile(r"\brole=[\"']alert[\"']")
ARIA_LIVE = re.compile(r"\baria-live=")
CONDITIONAL_STATUS = re.compile(
    r"(?:&&|\?)\s*\(?\s*<\w+[^<>]*(?:\brole=[\"']status[\"']|\baria-live=[\"']polite[\"'])"
)
ASYNC_HANDLER = re.compile(r"\bon[A-Z]\w*=\{\s*async\b")
TRY = re.compile(r"\btry\b|\.catch\(")
LOADING_ON = re.compile(r"\bset(?:Is)?Loading\(\s*true\s*\)")
LOADING_OFF = re.compile(r"\bset(?:Is)?Loading\(\s*false\s*\)")
FINALLY = re.compile(r"\bfinally\b")
USE_CLIENT = re.compile(r"\A\s*(?:(?:/\*.*?\*/|//[^\n]*)\s*)*[\"']use client[\"']", re.DOTALL)
NEXT_ERROR_FILE = re.compile(r"^(global-)?error\.(tsx|jsx|js|ts)$")
DEFAULT_EXPORT = re.compile(r"\bexport\s+default\b")
ROUTE_EXTENSIONS = (".tsx", ".jsx", ".js", ".ts")
TANSTACK_V4 = [  # (pattern, what to use in v5)
    (re.compile(r"\bcacheTime\s*:"), "cacheTime was renamed to gcTime in v5"),
    (re.compile(r"\buseErrorBoundary\s*:"), "useErrorBoundary was renamed to throwOnError in v5"),
    (re.compile(r"\bisInitialLoading\b"), "isInitialLoading is deprecated in v5: use isLoading"),
    (re.compile(r"\bkeepPreviousData\s*:\s*true"), "use placeholderData: keepPreviousData in v5"),
]

_manifest_cache = {}


# ---------- Helpers ----------

def blank(match):
    """The matched text with every character but newlines turned into spaces."""
    return re.sub(r"[^\n]", " ", match.group())


def strip_comments(text):
    """Comments replaced by spaces, so offsets and line numbers stay the same."""
    return LINE_COMMENT.sub(blank, BLOCK_COMMENT.sub(blank, text))


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def svelte_blocks(text, name):
    """(start offset, block text) for each {#name}...{/name} block, nested ones included."""
    tags = re.compile(r"\{#" + name + r"\b|\{/" + name + r"\}")
    stack, found = [], []
    for match in tags.finditer(text):
        if match.group().startswith("{#"):
            stack.append(match.start())
        elif stack:
            start = stack.pop()
            found.append((start, text[start:match.end()]))
    return found


def manifest_deps(folder):
    """The dependencies in folder/package.json, or None if there is no readable one."""
    if folder not in _manifest_cache:
        deps = None
        manifest = folder / "package.json"
        if manifest.is_file():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            except (ValueError, OSError, AttributeError):
                deps = {}
        _manifest_cache[folder] = deps
    return _manifest_cache[folder]


def dependency_spec(path, name_pattern):
    """The version spec of a matching package, from the nearest package.json that lists one.

    Keeps walking up past manifests that don't list it, so hoisted monorepo dependencies count.
    Stops at the repository root (the folder holding .git).
    """
    for folder in path.resolve().parents:
        deps = manifest_deps(folder)
        if deps:
            spec = next((v for k, v in deps.items() if re.fullmatch(name_pattern, k)), None)
            if spec is not None:
                return spec
        if (folder / ".git").exists():
            break
    return None


def tanstack_major(path):
    """The major version of TanStack Query the file's project uses, or None."""
    digits = re.search(r"\d+", dependency_spec(path, r"@tanstack/\w+-query") or "")
    return int(digits.group()) if digits else None


def app_router_dir(path):
    """The app/ folder of a Next.js project that holds this file, or None."""
    parts = path.resolve().parts
    if "app" not in parts[:-1] or dependency_spec(path, r"next") is None:
        return None
    app_index = len(parts) - 2 - parts[-2::-1].index("app")
    if any(part.startswith("_") for part in parts[app_index + 1:-1]):
        return None  # a _private folder is not a route segment
    return Path(*parts[: app_index + 1])


def has_route_error_file(path):
    """True if a Next.js error file covers this file.

    An error file covers its own folder and the folders below it, but not the layout beside it.
    """
    app_dir = app_router_dir(path)
    if app_dir is None:
        return False
    if any((app_dir / f"global-error{ext}").is_file() for ext in ROUTE_EXTENSIONS):
        return True
    folder = path.resolve().parent
    if path.stem == "layout":
        folder = folder.parent
    while len(folder.parts) >= len(app_dir.parts):
        if any((folder / f"error{ext}").is_file() for ext in ROUTE_EXTENSIONS):
            return True
        folder = folder.parent
    return False


# ---------- Checks ----------

def check_text(path, raw):
    """(line, severity, check id, message) for each problem in one file's text."""
    text = strip_comments(raw)
    ext = path.suffix
    markup = ext in MARKUP_EXTENSIONS or (ext in {".js", ".mjs"} and JSX_RETURN.search(text))
    found = []

    def add(offset, severity, check, message):
        found.append((line_of(text, offset), severity, check, message))

    if ext in JSX_EXTENSIONS and markup:
        for m in LEAKED_ZERO.finditer(text):
            if TERNARY_AHEAD.match(text, m.end()) or STATEMENT_AHEAD.match(text, m.end()):
                continue
            add(m.start(), "error", "leaked-zero", "a length or size left of && renders 0: use > 0 && or a ternary")

    if markup:  # in server code and utilities, a quiet catch is not a UI state problem
        # raw text: a catch with a comment explaining why it is empty is a decision, not a slip
        for m in EMPTY_CATCH.finditer(raw):
            if not FALLBACK_TRY.search(raw, max(0, m.start() - 300), m.start()):
                add(m.start(), "hint", "swallowed-error", "the error is swallowed: show it, rethrow it or set an error state")
        for m in SWALLOWING_THEN_CATCH.finditer(raw):
            add(m.start(), "hint", "swallowed-error", "the error is swallowed: show it, rethrow it or set an error state")
        for m in CATCH_TO_EMPTY.finditer(text):
            if BODY_PARSE.search(text, max(0, m.start() - 40), m.start()):
                continue
            add(m.start(), "warn", "failure-as-empty", "a failure becomes empty data: the user sees 'none' instead of 'couldn't load'")

    for m in EMPTY_DEFAULT.finditer(text):
        if "Suspense" not in m.group(1):
            add(m.start(), "warn", "empty-default", "data = [] hides loading and error: they look like an empty list")

    source = DATA_SOURCE.search(text)
    code = STRING.sub(blank, text)  # class names and copy don't count as error handling
    if (markup and source and not ERROR_HANDLED.search(code) and not ERROR_STATUS.search(text)
            and not ERROR_DELEGATED.search(text) and not WHOLE_RESULT.search(text)
            and not has_route_error_file(path)):
        detail = "loading is handled but errors are not" if LOADING.search(text) else "no error state"
        add(source.start(), "warn", "no-error-state", f"data is fetched here, {detail}")

    fetch_call = RAW_FETCH.search(text)
    if markup and fetch_call and JSON_CALL.search(text) and not CHECKS_OK.search(text) and "axios" not in text:
        add(fetch_call.start(), "warn", "fetch-no-ok", "fetch resolves on 404 and 500: check res.ok before res.json()")

    if markup:
        for m in HTML_TAG.finditer(text):
            if ROLE_ALERT.search(m.group()) and ARIA_LIVE.search(m.group()):
                add(m.start(), "warn", "alert-plus-live", "role=\"alert\" plus aria-live is read twice by VoiceOver on iOS")
        for m in CONDITIONAL_STATUS.finditer(text):
            add(m.start(), "warn", "conditional-status-region",
                "a status region mounted with its text announces nothing: keep it mounted, change its text")

    if (NEXT_ERROR_FILE.match(path.name) and DEFAULT_EXPORT.search(text)
            and app_router_dir(path) and not USE_CLIENT.search(raw)):
        add(0, "error", "next-error-client", "Next.js error files must start with 'use client'")

    if ext == ".svelte":
        for start, block in svelte_blocks(text, "await"):
            head = block[: block.find("}") + 1]
            if "{:catch" not in block and not re.search(r"\bcatch\b", head):
                add(start, "error", "await-no-catch", "{#await} without {:catch}: a failed promise renders nothing")
        for start, block in svelte_blocks(text, "each"):
            if "{:else}" not in block:
                add(start, "hint", "each-no-else", "{#each} without {:else}: is an empty list possible here?")

    if (major := tanstack_major(path)) and major >= 5:
        for pattern, message in TANSTACK_V4:
            for m in pattern.finditer(text):
                add(m.start(), "warn", "tanstack-v4-api", message)

    if markup and ASYNC_HANDLER.search(text) and not TRY.search(text):
        m = ASYNC_HANDLER.search(text)
        add(m.start(), "hint", "async-handler-no-try", "an async handler with no try or .catch: where does a failure show?")

    if LOADING_ON.search(text) and not FINALLY.search(text) and len(LOADING_OFF.findall(text)) < 2:
        m = LOADING_ON.search(text)
        add(m.start(), "hint", "loading-no-finally", "loading is set to false on one path only: reset it in finally")

    return found


def check_file(path):
    """Problems in one file, minus the ones a ui-states-ignore comment silences."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    if IGNORE_FILE in raw:
        return []
    lines = raw.splitlines()

    def silenced(number):
        nearby = lines[max(0, number - 2): number]
        return any(IGNORE_LINE in line for line in nearby)

    kept = {f for f in check_text(path, raw) if not silenced(f[0])}
    return sorted(kept, key=lambda f: (f[0], SEVERITY_ORDER[f[1]], f[2]))


def code_files(paths):
    """Every code file under the given files and folders, skipping build output and tests."""
    for given in map(Path, paths or ["."]):
        if given.is_file():
            if given.suffix in CODE_EXTENSIONS:
                yield given
            continue
        for root, dirs, files in os.walk(given):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
            for name in sorted(files):
                path = Path(root) / name
                if (path.suffix in CODE_EXTENSIONS and not SKIP_FILE.search(name)
                        and path.stat().st_size <= MAX_BYTES):
                    yield path


def main(paths):
    failing = 0
    for path in code_files(paths):
        for number, severity, check, message in check_file(path):
            print(f"{path}:{number}: {severity} {check}: {message}")
            failing += severity != "hint"
    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
