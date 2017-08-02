#!/usr/bin/python

# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Plot the performance data"""

import argparse
import operator
import os
import sys
import math

import plotly.offline as ploff
import plotly.graph_objs as plgo
from lxml import etree


def select_files_in_subfolders(directory, ext='xml'):
    """Get all files in folder and its subfolders.

    :param dir: Input folder.
    :param ext: File extension.
    :type dir: str
    :type ext: str
    :return: List of filex matching the parameters.
    :rtype list
    """
    for _, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.%s' % ext):
                yield os.path.join(directory, file)


def select_files_in_folder(directory, ext='xml'):
    """Get all files in folder.

    :param dir: Input folder.
    :param ext: File extension.
    :type dir: str
    :type ext: str
    :return: List of filex matching the parameters.
    :rtype list
    """
    for file in os.listdir(directory):
        if file.endswith('.%s' % ext):
            yield os.path.join(directory, file)


def combine_dicts(first, second, oper=operator.add):
    """Combine two dictionaries.

    :param first: First dict.
    :param second: Second dict.
    :param oper: Operator.
    :type first: dict
    :type second: dict
    :type oper: operator
    :return: Combined dictionary.
    :rtype dict
    """

    return dict(first.items() + second.items() +\
        [(k, oper(first[k], second[k])) for k in set(second) & set(first)])


def parse_data_pps(args):
    """Get PPS data out of XML file into array.

    :param args: Command line parameters.
    :type suite: ArgumentParser
    :return: X-data and Y-data dictionaries.
    :rtype tuple of dict
    """
    xdata = []
    ydata_pps = {}

    for i, file in enumerate(sorted(select_files_in_folder(args.input))):
        xml_tree = etree.parse(file)
        sel = xml_tree.xpath(args.xpath)
        if sel:
            ydata_pps = combine_dicts(ydata_pps, dict((elem.attrib['name'],\
                (i, float(elem.text))) for elem in sel))
            xdata.append(xml_tree.getroot().attrib['vdevice'])
    return xdata, ydata_pps


def parse_data_lat(args):
    """Get latency data out of XML file into array.

    :param args: Command line parameters.
    :type suite: ArgumentParser
    :return: X-data and Y-data dictionaries.
    :rtype tuple of dict
    """
    xdata = []
    ydata_lat = {}

    for i, file in enumerate(sorted(select_files_in_folder(args.input))):
        xml_tree = etree.parse(file)
        sel = xml_tree.xpath(args.xpath)
        if sel:
            try:
                ydata_lat = combine_dicts(ydata_lat, dict((elem.attrib['name'],\
                    (i, elem.attrib[args.latency])) for elem in sel))
            except KeyError:
                raise RuntimeError('Retrieving latency data error (PDR?)')
            xdata.append(xml_tree.getroot().attrib['vdevice'])
    return xdata, ydata_lat


def parse_args():
    """Parse arguments from cmd line.

    :return: Parsed arguments.
    :rtype ArgumentParser
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-x", "--xpath", required=True,
                        help="Xpath filter")
    parser.add_argument("-t", "--title", required=True,
                        help="Plot title")
    parser.add_argument("-l", "--lower",
                        default=False,
                        help="Lower boudary of Y-axis")
    parser.add_argument("-u", "--upper",
                        default=False,
                        help="Upper boudary of Y-axis")
    parser.add_argument("-e", "--errorbar",
                        default=False,
                        help="Errorbar for Y-axis")
    parser.add_argument("-d", "--latency",
                        choices=['lat_10', 'lat_50', 'lat_100'],
                        help="Latency to draw")
    parser.add_argument("-p", "--plot",
                        choices=['box', 'scatter'],
                        default='box',
                        help="Throughput plot type")
    parser.add_argument("-i", "--input",
                        help="Input folder")
    parser.add_argument("-o", "--output", required=True,
                        help="Output image file name")
    return parser.parse_args()


def main():
    """Main function."""

    args = parse_args()
    if args.latency:
        xdata, ydata = parse_data_lat(args)
    else:
        xdata, ydata = parse_data_pps(args)

    # Print data into console for debug
    print args.title
    for data in ydata:
        print data + ";" + ";".join(str(val) for val in ydata[data][1::2])

    if xdata and ydata:
        traces = []
        # Add plot traces
        for i, suite in enumerate(ydata):
            if args.latency:
                y_extract = []
                _ = [y_extract.extend([l, l]) for l in ydata[suite][1::2][0].split('/')]
                traces.append(plgo.Box(
                    x=['TGint1-to-SUT1-to-SUT2-to-TGint2',
                       'TGint1-to-SUT1-to-SUT2-to-TGint2',
                       'TGint1-to-SUT1-to-SUT2-to-TGint2',
                       'TGint1-to-SUT1-to-SUT2-to-TGint2',
                       'TGint1-to-SUT1-to-SUT2-to-TGint2',
                       'TGint1-to-SUT1-to-SUT2-to-TGint2',
                       'TGint2-to-SUT2-to-SUT1-to-TGint1',
                       'TGint2-to-SUT2-to-SUT1-to-TGint1',
                       'TGint2-to-SUT2-to-SUT1-to-TGint1',
                       'TGint2-to-SUT2-to-SUT1-to-TGint1',
                       'TGint2-to-SUT2-to-SUT1-to-TGint1',
                       'TGint2-to-SUT2-to-SUT1-to-TGint1'],
                    y=y_extract,
                    name=str(i+1)+'. '+suite.lower().replace('-ndrdisc',''),
                    boxmean=False,
                ))
            else:
                if args.plot == 'box':
                    traces.append(plgo.Box(
                        x=[str(i+1)+'.'] * len(ydata[suite][1::2]),
                        y=ydata[suite][1::2],
                        name=str(i+1)+'. '+suite.lower().replace('-ndrdisc',''),
                        hoverinfo='x+y',
                        boxpoints='outliers',
                        whiskerwidth=0,
                    ))
                elif args.plot == 'scatter':
                    traces.append(plgo.Scatter(
                        x=ydata[suite][0::2],
                        y=ydata[suite][1::2],
                        mode='lines+markers',
                        name=str(i+1)+'. '+suite.lower().replace('-ndrdisc',''),
                    ))
                else:
                    pass

        # Add plot layout
        layout = plgo.Layout(
            title='{0}'.format(args.title),
            xaxis=dict(
                autorange=True,
                autotick=False,
                fixedrange=False,
                gridcolor='rgb(238, 238, 238)',
                linecolor='rgb(238, 238, 238)',
                linewidth=1,
                showgrid=True,
                showline=True,
                showticklabels=True,
                tickcolor='rgb(238, 238, 238)',
                tickmode='linear',
                title='Indexed Test Cases' if args.plot == 'box'\
                    else '',
                zeroline=False,
            ),
            yaxis=dict(
                gridcolor='rgb(238, 238, 238)',
                hoverformat='' if args.latency else '.4s',
                linecolor='rgb(238, 238, 238)',
                linewidth=1,
                range=[args.lower, args.upper] if args.lower and args.upper\
                    else [],
                showgrid=True,
                showline=True,
                showticklabels=True,
                tickcolor='rgb(238, 238, 238)',
                title='Latency min/avg/max [uSec]' if args.latency\
                    else 'Packets Per Second [pps]',
                zeroline=False,
            ),
            boxmode='group',
            boxgroupgap=0.5,
            autosize=False,
            margin=dict(
                t=50,
                b=20,
                l=50,
                r=20,
            ),
            showlegend=True,
            legend=dict(
                orientation='h',
            ),
            width=700,
            height=1000,
        )
        # Create plot
        plpl = plgo.Figure(data=traces, layout=layout)
        # Export Plot
        ploff.plot(plpl,
                   show_link=False, auto_open=False,
                   filename='{0}.html'.format(args.output))
    else:
        sys.stderr.write('No data found!\n')


if __name__ == "__main__":
    sys.exit(main())
