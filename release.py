#!/usr/bin/env python3
import locale
import os
import pathlib
import shutil
import subprocess
from subprocess import getoutput as run
import sys
import time

# Make sure working directory is base directory
os.chdir(pathlib.Path(__file__).parent)

def run(*cmd):
	result = subprocess.run(cmd, capture_output=True, check=True)
	return result.stdout.decode(locale.getpreferredencoding()).removesuffix("\n").removesuffix("\r")

# Read version number
VERSION = run("sh", "-c", "grep '#define VERSION_PACKAGE' pgadmin/include/version.h | awk '{print $3}'")

# Check that tag doesn’t already exist
if run("git", "tag", "-l", f"v{VERSION}"):
	print(f"Version “{VERSION}” has already been released to GIT!", file=sys.stderr)
	print("Please bump the version information in “pgadmin/include/version.h” (but do not commit) and try again!", file=sys.stderr)
	sys.exit(1)

# Write Debian changelog entry
changelog_path = pathlib.Path("debian") / "changelog"
with changelog_path.with_suffix(".new").open("w") as dst, changelog_path.open("r") as src:
	print(f"pgadmin3-lts ({VERSION}) UNRELEASED; urgency=medium", file=dst)
	print("", file=dst)
	print("  * New upstream release.", file=dst)
	print("", file=dst)
	print(f" -- {run('git', 'config', 'user.name')} <{run('git', 'config', 'user.email')}>  {time.strftime('%a, %e %b %Y %T %z')}", file=dst)
	print("", file=dst)
	shutil.copyfileobj(src, dst)
changelog_path.with_suffix(".new").replace(changelog_path)

# Commit changes
run("git", "commit", "-m", f"Release version {VERSION}", "pgadmin/include/version.h", "debian/changelog")

# Tag changes
run("git", "tag", f"v{VERSION}")

# Push changes
run("git", "push", "origin", "main", f"v{VERSION}")
