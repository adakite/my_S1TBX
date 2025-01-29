import os
import sys
import subprocess
import fnmatch

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Metadata
__author__ = "Antoine Lucas"
__copyright__ = "Copyright 2016, Antoine Lucas"
__license__ = "CeCILL"
__version__ = "0.0.2"
__email__ = "dralucas@astrogeophysx.net"
__status__ = "Prototype"

# Constants
ALIGN_TOPS = "/usr/local/GMT5SAR/bin/align_tops.csh"
DEBUG = True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def print_debug(message):
    if DEBUG:
        print(f"DEBUG: {message}")


def run_command(cmd):
    """Run a shell command with error handling."""
    try:
        if DEBUG:
            print_debug(f"Command: {cmd}")
        else:
            subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(f"ERROR: Command failed - {e}")


# Main execution
if __name__ == "__main__":
    os.system("clear")

    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print(f"Usage: {sys.argv[0]} demfile.grd s1afile1 s1afile2 [subswath_number {{1, 2, 3}}]")
        print("   If no subswath number is given, all three will be treated.")
        sys.exit()

    print("Preparing S1A data for GMTSAR package")
    print("-------------------------------------\n")

    if DEBUG:
        print("!!! WARNING: Running in debugging mode. Only potential errors/warnings will occur.\n")

    demfile = sys.argv[1]
    img_files = sys.argv[2:4]
    subswath_number = sys.argv[4] if len(sys.argv) == 5 else None

    # Create RAW directory
    print("1/ Creating RAW directory")
    run_command("mkdir -p raw")

    # Link DEM file
    run_command(f"ln -sr {demfile} ./raw/")

    # Prepare S1A data
    n_img = 2
    n_sw = 1 if subswath_number else 3

    S1Aswath = [[None] * n_sw for _ in range(n_img)]
    S1Aoef = [None] * n_img

    print("2/ Linking TIFF/XML into RAW directory for:")
    for ii, img in enumerate(img_files):
        print(f"   {img}")

        # Handle annotation files
        annotation_pattern = f"s1a-iw{subswath_number}*-vv-*.xml" if subswath_number else "s1a*-vv-*.xml"
        cmd = f"ln -sr ./{img}.SAFE/annotation/{annotation_pattern} ./raw/"
        run_command(cmd)
        S1Aswath[ii] = fnmatch.filter(os.listdir(f"./{img}.SAFE/annotation/"), annotation_pattern)

        # Handle measurement files
        measurement_pattern = f"s1a-iw{subswath_number}*-vv-*.tiff" if subswath_number else "s1a*.tiff"
        cmd = f"ln -sr ./{img}.SAFE/measurement/{measurement_pattern} ./raw/"
        run_command(cmd)

        # Find and link EOF file
        date_time = img.split("_")[-2]  # Extract date/time from filename
        date = date_time[:8]
        time_min = date_time[9:15]
        time_max = date_time[16:]

        eof_found = False
        for eoffile in os.listdir("./"):
            if eoffile.endswith(".EOF"):
                tmin = int(eoffile.split("_V")[1].split("T")[0])
                tmax = int(eoffile.split("T")[1].replace("Z", ""))
                if int(date + time_min) >= tmin and int(date + time_max) <= tmax:
                    run_command(f"ln -sr {eoffile} ./raw/")
                    S1Aoef[ii] = eoffile
                    eof_found = True
                    break

        if not eof_found:
            sys.exit(f"ERROR: EOF file is missing for {img}")

    print("3/ Preprocessing subswaths")
    for i in range(n_sw):
        subswath_id = subswath_number or i + 1
        print(f"   Subswath #: {subswath_id}")

        img1name = S1Aswath[0][i][:-4]
        img2name = S1Aswath[1][i][:-4]
        eof1name = S1Aoef[0]
        eof2name = S1Aoef[1]

        cmd = (f"{ALIGN_TOPS} ./raw/{img1name} ./raw/{eof1name} "
               f"./raw/{img2name} ./raw/{eof2name} ./raw/{demfile}")
        run_command(cmd)

        # Create F directories
        f_dir = f"F{subswath_id}"
        run_command(f"mkdir -p {f_dir}/raw")
        run_command(f"ln -sr ../config.s1a.txt ./{f_dir}/")
        run_command(f"ln -sr S*F{subswath_id}* ./{f_dir}/raw/")

    print("Processing complete!")
