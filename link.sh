set -eux

CHROME_DIR=$1

ln -s $CHROME_DIR/tools/mac/power/driver_scripts_templates .
ln -s $CHROME_DIR/tools/mac/power/utils.py .
ln -s $CHROME_DIR/tools/mac/power/generate_scripts.py .
ln -s $CHROME_DIR/tools/mac/power/macros .
ln -s $CHROME_DIR/tools/mac/power/pages .
