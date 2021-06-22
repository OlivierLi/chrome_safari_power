# What is this repo?

This repo contains tools that allow you to run different browsers under specific usage scenarios and:

* Measure their impact of system ressource use.
* Profile the code that runs and/or is causing wake-ups. (chromium only)


# Setting Up

## Chromium build
If measuring of profiling Chromium it needs to be built with the following args.gn and copied to the "Applications" folder.

    use_goma = true
    is_debug = false
    is_component_build = false
    symbol_level = 0
    blink_symbol_level = 0
    is_official_build = true

## Python Virtual Environment
This project uses python [Virtual Environments](https://docs.python.org/3/tutorial/venv.html).

Create the venv. Only needs to be done once.
```
python3 -m venv ./env
```
Activate the venv.
```
source ./env/bin/activate
```
Once the venv is activated, `python` refers to python3.
Upgrade pip and install all python dependancies. 
```
python -m pip install -U pip
python -m pip install -r requirements.txt
```

To deactivate venv.
```
deactivate
```

## Getting around sudo password
To disable asking password for sudo commands (required by powermetrics).
Run `sudo visudo` and add the last line to User specification (replacing `<user>`):
```
# root and users in group wheel can run anything on any machine as any user
root ALL = (ALL) ALL
%admin ALL = (ALL) ALL
<user> ALL = (ALL) NOPASSWD:ALL
```

## dtrace
Running benchmark.py in profile mode uses `dtrace` to analyse the chromium processes. By default `dtrace` does not work well with [SIP](https://support.apple.com/en-us/HT204899). Disabling SIP as a whole is not recommended and instead should be done only for dtrace using these steps:

* Reboot in recovery mode
* Start a shell
* Execute `csrutil enable --without dtrace --without debug`
* Reboot

# Using the different tools

## benchmark.py
Use to execute different usage scenarios and measure their power use or profile them.
```
./benchmark.py ./results --measure 
./benchmark.py ./profile --profile_mode cpu_time
```

## powermetrics_compare.py
Parses and aggregates powermetrics results generated from benchmark.py --measure, generating a csv for each benchmark, and one for a high level summary.
```
./powermetrics_compare.py ./results
```

## collapse.py/
Parses and aggregates DTrace results generated from benchmark.py --profile. 
The scripts produce collapsed stack files that be opened in speedscope.app.

```
python3 ./collapse.py --mode cpu_time --stack_dir ./profile
```

# More info

## pages/
This directory contains special webpages that can be loaded from disk in a navigator to verify certain behaviors.

## driver_scripts_templates/
This directory contains templates that get converted into scripts at runtime. They can control the behaviour of Chromium based browsers or Safari to reproduce usage scenarios. The scripts will start the browsers if we want to include startup in the power capture. If not that can be done seperatly.

## check_env.sh
This file makes functions available to allow the other scripts to verify they are running in a sane environment for battery life testing.

# Signing your Chrome builds
Signing your Chromium build can make working with them easier in some cases, especially regarding os level access settings. To do that you need to follow the following instructions:

1. Create a signing certificate in Xcode.
2. Find your code signing identity using `security find-identity -v -p codesigning`
3. Follow the chrome signing [instructions](https://source.chromium.org/chromium/chromium/src/+/master:chrome/installer/mac/signing/README.md)
4. Now you have a signed build!
