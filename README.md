# speedurl

speedurl is a python 2 or 3 tool for testing download speeds quickly.

The URL is downloaded partially until the speed of the download (measured once
per second) drops.  The reported speed is the average of the top two
measurements (or something like that).  This is generally the speed number
reported by speed test sites.

Output is reported in a similar way to ping, with a couple of tweaks for
processing with `cut`.

You can specify multiple URLs, and repeat the test multiple times for each.
The idea is to provide a repeatable measure of performance to diagnose subtle
packet drops and corruption, e.g. by one member of an aggregated link.

## Usage

```bash
# python speedurl.py -n 3 'https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso'
2.917Mbps	384kB	1.108s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
5.774Mbps	896kB	1.306s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
10.694Mbps	1280kB	1.007s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
18.567Mbps	2304kB	1.044s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
17.102Mbps	2048kB	1.008s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
17.835

1.853Mbps	256kB	1.163s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
6.463Mbps	896kB	1.167s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
16.134Mbps	1920kB	1.002s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
17.228Mbps	2176kB	1.063s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
19.683Mbps	2432kB	1.040s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
21.212Mbps	2560kB	1.016s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
9.544Mbps	1152kB	1.016s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
20.447

2.961Mbps	384kB	1.092s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
4.226Mbps	640kB	1.275s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
11.809Mbps	1408kB	1.004s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
11.432Mbps	1408kB	1.037s	https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso
11.620

	---  3 tests to https://download.microsoft.com/download/8/1/d/81d1f546-f951-45c5-964d-56bdbd758ba4/w2k3sp2_3959_usa_x64fre_spcd.iso on fizbox ---
	22675456 bytes over 23.018s at 2020-06-08 15:07:04 UTC
	Mbps min/avg/max/stddev = 11.620/16.634/20.447/3.702
```
There the tool did did three tests ( `-n 3` ).  The first test took 5 seconds,
and the rate reached as high as 18.567Mbps before falling back (e.g. due to
packet loss or delay).  The 2nd reached up to 21Mbps, and then fell back
sharply.  The third went up to 11.8Mbps, and fell back to 11.4.  The rates of
the tests were 17.8, 20.4 and 11.6 Mbps, which are the average of the top two
per-second readings.  It took 23 seconds to run the test, and the average of
the test resulsts was 11.634Mbps.  The standard deviation was 3.702Mbps.
```
# ./speedurl.py --help
Usage: speedurl.py [options]

Options:
  -h, --help            show this help message and exit
  -H HEADERS, --header=HEADERS
                        HTTP headers
  -q, --quiet           Don't show progress during tests
  -b, --bps             use bps as unit
  -n REPEAT, --repeat=REPEAT
                        repeat this many times per url
```

## License
[GPL](https://choosealicense.com/licenses/gpl/)

