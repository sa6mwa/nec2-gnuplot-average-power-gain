# nec2-gnuplot-average-power-gain
Python script that parses nec2c output and generates plots using Gnuplot of
Radiation Efficiency.

## Example
```
$ ./nec2-average-power-gain-to-gnuplot.py -h

$ ./nec2-average-power-gain-to-gnuplot.py -f hf longwire-22m.nec doublet-22m.nec sloper-22m.nec
Treating longwire-22m.nec as a nec2 input file
Using FR card "hf": FR 0 541 0 0 3.0 0.05 30.0
Replacing RP card with: RP  0  37  37  1001  0.00000E+00  0.00000E+00  2.50000E+00  1.00000E+01  0.00000E+00  0.00000E+00
Executing: /usr/bin/nec2c -i longwire-22m.nec -o longwire-22m.out
Treating doublet-22m.nec as a nec2 input file
Using FR card "hf": FR 0 541 0 0 3.0 0.05 30.0
Replacing RP card with: RP  0  37  37  1001  0.00000E+00  0.00000E+00  2.50000E+00  1.00000E+01  0.00000E+00  0.00000E+00
Executing: /usr/bin/nec2c -i doublet-22m.nec -o doublet-22m.out
Treating sloper-22m.nec as a nec2 input file
Using FR card "hf": FR 0 541 0 0 3.0 0.05 30.0
Replacing RP card with: RP  0  37  37  1001  0.00000E+00  0.00000E+00  2.50000E+00  1.00000E+01  0.00000E+00  0.00000E+00
Executing: /usr/bin/nec2c -i sloper-22m.nec -o sloper-22m.out
Writing apg2.gpi
View plot by executing: gnuplot -p apg2.gpi
```
