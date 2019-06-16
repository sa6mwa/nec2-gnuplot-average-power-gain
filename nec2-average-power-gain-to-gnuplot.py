#!/usr/bin/python
#
# nec2-average-power-gain-to-gnuplot.py
# by SA6MWA Michel <sa6mwa@radiohorisont.se>
# https://github.com/sa6mwa/nec2-gnuplot-average-power-gain
#
# This is free and unencumbered software released into the public domain.
# 
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
# 
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# 
# For more information, please refer to <http://unlicense.org/>
#
import os
import sys
import getopt
import re
import subprocess

nec2c = "/usr/bin/nec2c"
gpifile = "apg2.gpi"
intype = "auto"
frcard = "no" # no = do not change the FR cards
frcards = { "hf": "FR 0 541 0 0 3.0 0.05 30.0",
            "nvis": "FR 0 181 0 0 2.0 0.05 11.0",
            "vhf": "FR 0 541 0 0 30.0 0.5 300.0",
          }
valid_in_types = ("nec2", "out", "auto")
gnuplot_extension = "gpi" # .gpi is syntax highlighted in vim :)
force = False

gnuplot_header = """set title 'AVERAGE POWER GAIN divided by 2 (APG/2) AKA RADIATION EFFICIENCY'
set xlabel 'MHz'
set ylabel 'Radiation Efficiency APG/2'
set grid
set yrange [0:1]
set ytics 0.05
set xtics 1.0
set style rect fc lt -1 fs solid 0.2 noborder
set obj rect from 1.81, graph 0 to 2.0, graph 1
set obj rect from 3.5, graph 0 to 3.8, graph 1
set obj rect from 5.3515, graph 0 to 5.3665, graph 1
set obj rect from 7.0, graph 0 to 7.2, graph 1
set style rect fc rgb "red" fs solid 0.3 noborder
set obj rect from 10.1, graph 0 to 10.15, graph 1
set style rect fc lt -1 fs solid 0.2 noborder
set obj rect from 14.0, graph 0 to 14.35, graph 1
set style rect fc rgb "red" fs solid 0.3 noborder
set obj rect from 18.068, graph 0 to 18.168, graph 1
set style rect fc lt -1 fs solid 0.2 noborder
set obj rect from 21.0, graph 0 to 21.45, graph 1
set style rect fc rgb "red" fs solid 0.3 noborder
set obj rect from 24.89, graph 0 to 24.99, graph 1
set style rect fc lt -1 fs solid 0.2 noborder
set obj rect from 28.0, graph 0 to 29.7, graph 1
"""

def usage():
  global nec2c
  global frcard
  global gpifile
  global frcards
  print """usage: {prog} [-i input_type] [-n nec2c_path] [-f FRcard] [-g gnuplot_output] [-F] inputfile.nec|inputfile.out [input2.nec|input2.out...]
  -i, --input-type nec2|out|auto  type of input file, default is auto
  -n, --nec2c <path>              path to nec2c, default is {nec2c}
  -f, --fr no|hf|nvis|vhf         unless -fno, replace all nec2 file's FR
                                  card with a predefined FR card, currently
                                  one of hf, nvis or vhf. default is {frcard}
  -g, --gnuplot-file <file>       gnuplot output file, default is {gpi}
  -F, --force                     force overwriting {gpi} if exists

If input file type is "nec2" (whether decided by -i nec2 or -i auto) the script
will replace all FR cards with a predefined FR card:
{frcards}

Also (if input file is "nec2") script will attempt to modify the 4th field in
all RP cards to ensure the last digit is 1 (which will generate AVERAGE POWER
GAIN) and then run nec2c to generate the output by executing:
{nec2c} -i input.nec -o input.out

Finally, the script will parse the output file and produce a Gnuplot .gpi file
(-g {gpi}) that can be rendered with Gnuplot, for example:
gnuplot -p {gpi}

Example:
{prog} -f hf -n /usr/local/bin/nec2c comparison-endfed-10m.nec comparison-centerfed-10m.nec
{prog} -f nvis longwire-22m.nec doublet-22m.nec sloper-22m.nec
""".format(prog=sys.argv[0], nec2c=nec2c, frcard=frcard, gpi=gpifile, frcards=frcards)


def getDataViaOutputFile(filename):
  qrgregexp = re.compile(r'^\s*FREQUENCY\s+:\s+([+-]?\d+(?:\.\d*(?:[eE][+-]?\d+)?))?\sMHz\s*$')
  apgregexp = re.compile(r'^\s*AVERAGE POWER GAIN:\s+([+-]?\d+(?:\.\d*(?:[eE][+-]?\d+)?))?\s+')
  data = list()
  with open(filename) as fp:
    got_frequency = False
    qrg = float(0)
    got_apg = False
    apg = float(0)
    for line in fp:
      if re.match(qrgregexp, line):
        if got_frequency and not got_apg:
          assert False, "unable to parse nec2 output file %s, does not seem to contain AVERAGE POWER GAIN" % filename
        groups = re.search(qrgregexp, line).groups()
        if len(groups) > 0:
          qrg = groups[0]
          got_frequency = True
      if re.match(apgregexp, line):
        assert got_frequency, "unable to parse nec2 output file %s, got AVERAGE POWER GAIN before frequency" % filename
        groups = re.search(apgregexp, line).groups()
        if len(groups) > 0:
          apg = groups[0]
          got_apg = True
        assert got_frequency and got_apg, "unable to parse nec2 output file %s, regexp search problem" % filename
        data.append([ float(qrg), float(float(apg) / 2.0)])
        qrg = float(0)
        apg = float(0)
        got_frequency = False
        got_apg = False
  return data


def getDataViaNec2(filename, nec2binary, frcard="no", frcards=dict()):
  # filename = nec file
  # nec2binary = path to nec2c
  # frcard = key of FR card in frcards dictionary, default is no which means do
  # not change the FR card
  # returns a two dimensional list
  if frcard != "no":
    assert frcard in frcards, "%s is not a in frcards dictionary: %s" % (frcard, frcards)
    print "Using FR card \"{}\": {}".format(frcard, frcards[frcard])
  assert os.path.isfile(nec2binary) and os.access(nec2binary, os.X_OK), "%s is not executable" % nec2binary
  # ensure the RP card has average gain calculation enabled by rewriting it
  # and replace the FR cards if we should do so
  necdatain = list()
  necdataout = list()
  with open(filename, "r") as fp:
    for line in fp:
      necdatain.append(line.rstrip())
  for line in necdatain:
    if re.match("^RP\s", line):
      rp = line.split()
      assert len(rp) > 4, "unable to modify/assert that RP card sets APG in %s, too few columns" % (filename)
      xnda = abs(int(rp[4]))
      if xnda % 10 not in (1, 2):
        rp[4] = str(xnda - xnda % 10 + 1)
        newrpcard = "  ".join(rp)
        print "Replacing RP card with: {}".format(newrpcard)
        necdataout.append("# " + line)
        necdataout.append(newrpcard)
      else:
        necdataout.append(line)
    elif frcard != "no" and re.match("^FR\s", line):
      if line != frcards[frcard]:
        print "Replacing FR card with: {}".format(frcards[frcard])
        necdataout.append("# " + line)
        necdataout.append(frcards[frcard])
      else:
        necdataout.append(line)
    else:
      necdataout.append(line)
  if necdatain != necdataout:
    with open(filename, "w") as fp:
      for line in necdataout:
        line = line + "\n"
        fp.write(line)
  outputfilename = os.path.splitext(filename)[0] + ".out"
  # execute nec2c to produce .out file
  print "Executing: %s -i %s -o %s" % (nec2binary, filename, outputfilename)
  subprocess.call([nec2binary, "-i", filename, "-o", outputfilename])
  assert os.path.isfile(outputfilename), "%s failed to create output file %s" % (nec2binary, outputfilename)
  return getDataViaOutputFile(outputfilename)



def main():
  global intype
  global nec2c
  global frcard
  global frcards
  global valid_in_types
  global gnuplot_extension
  global gpifile
  global force
  try:
    opts, files = getopt.getopt(sys.argv[1:], "hi:n:f:g:F", ["help","input-type=","nec2c=","fr=","gnuplot-file=","force"])
  except getopt.GetoptError as err:
    print str(err)
    usage()
    sys.exit(2)
  for o, a in opts:
    if o in ("-h", "--help"):
      usage()
      sys.exit()
    elif o in ("-i", "--input-type"):
      assert a in valid_in_types, "invalid input type \"%s\"" % a
    elif o in ("-n", "--nec2c"):
      nec2c = a
    elif o in ("-f", "--fr"):
      frcard = a
      assert frcard in frcards, "%s is not a valid FR card, please choose from: %s" % (frcard, frcards)
    elif o in ("-g", "--gnuplot-file"):
      gpifile = a
    elif o in ("-F", "--force"):
      force = True
    else:
      usage()
      assert False, "unhandled option"

  if len(files) < 1:
    usage()
    sys.exit(2)
  for f in files:
    assert os.path.isfile(f), "%s does not exist or is not a file" % f

  if not force:
    assert not os.path.exists(gpifile), "%s already exists, force overwrite with -F or provide another name with -g (or move it)" % gpifile
  else:
    if os.path.exists(gpifile):
      assert os.path.isfile(gpifile), "%s is not a file, will only overwrite files" % gpifile

  if intype == "auto" or intype == "nec2":
    assert os.path.isfile(nec2c), "%s can not be found or is not a file, please install nec2c or provide correct path!" % nec2c

  plotTitles = list()
  plotData = list()

  for f in files:
    # data will contain a list of lists where [0] is frequency in MHz and [1]
    # is APG/2
    data = list()

    if intype == "auto":
      if re.match(".+\.(nec|nec2|nec2c)$", f, re.IGNORECASE):
        print "Treating %s as a nec2 input file" % f
        data = getDataViaNec2(f, nec2c, frcard, frcards)
      elif re.match(".+\.out$", f, re.IGNORECASE):
        print "Treating %s as an output file" % f
        data = getDataViaOutputFile(f)
      else:
        assert False, "unable to decide treatment of file %s" % f
    elif intype == "nec2":
      print "Treating %s as a nec2 input file" % f
      data = getDataViaNec2(f, nec2c, frcard, frcards)
    elif intype == "out":
      print "Treating %s as an output file" % f
      data = getDataViaOutputFile(f)
    else:
      assert False, "invalid input type %s" % intype

    if len(data) < 1:
      assert False, "empty dataset when parsing %s" % f

    plotData.append(data)
    plotTitles.append(f)

  # generate data for gnuplot and parse together a gnuplot file
  dstr = str()
  for index, data in enumerate(plotData):
    dstr += "$data{} << EOD\n".format(index)
    for d in data:
      dstr += "{} {}\n".format(d[0], d[1])
    dstr += "EOD\n"
  dstr += "plot "

  plotDataLen = len(plotData)
  for index, data in enumerate(plotData):
    dstr += "'$data{}' using 1:2 with lines linewidth 2 title '{}'".format(index, plotTitles[index])
    if plotDataLen != index + 1:
      dstr += ", \\\n"
  dstr += "\n"

  print "Writing {}".format(gpifile)
  with open(gpifile, "w") as fp:
    fp.write(gnuplot_header)
    fp.write(dstr)

  print "View plot by executing: gnuplot -p {}".format(gpifile)

if __name__ == '__main__':
  main()
