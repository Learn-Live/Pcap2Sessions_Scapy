# -*- coding:utf-8 -*-
r"""
    plot the packet's payload to image

"""

import errno
import os
import sys

# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.abspath('../'))  # add 'parent path' to system path
print(sys.path)

from pcap_parser.pcap2sessions_scapy import *


def mkdir_p(path):
    """

    :param path:
    :return:
    """
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def save_payload_to_image(payload_1d, image_width=28, output_name='demo.png'):
    """

    :param payload_1d:
    :param image_width:
    :param output_name:
    :return:
    """
    if len(payload_1d) < image_width * image_width:
        print(payload_1d)
        payload_1d += b'\x00' * (image_width * image_width - len(payload_1d))
    if len(payload_1d) > image_width * image_width:
        payload_1d = payload_1d[:image_width * image_width]
    hexst = binascii.hexlify(payload_1d)
    payload_1d = numpy.array([int(hexst[i:i + 2], 16) for i in range(0, len(hexst), 2)])

    rn = len(payload_1d) // image_width
    fh = numpy.reshape(payload_1d[:rn * image_width], (-1, image_width))
    fh = numpy.uint8(fh)

    im = Image.fromarray(fh)
    im.save(output_name)

    return output_name


def getMatrixfrom_pcap(filename, width):
    """

    :param filename:
    :param width:
    :return:
    """
    with open(filename, 'rb') as f:
        content = f.read()
    hexst = binascii.hexlify(content)
    fh = numpy.array([int(hexst[i:i + 2], 16) for i in range(0, len(hexst), 2)])
    rn = len(fh) // width
    fh = numpy.reshape(fh[:rn * width], (-1, width))
    fh = numpy.uint8(fh)
    return fh

def is_filter(k, filter={'IPs':[],'ports':[]}):
    """

    :param k:
    :param filter:
    :return:
    """
    IPs = filter['IPs']
    for ip in filter['IPs']:
        if ip+':' in k:
            return True

    for port in filter['ports']:
        # if port in k:
        if ':'+str(port)+'-' in k:  # 10.152.152.11:24007-5.34.22.172:25806-UDP-(3x28).png
            return True

    return False


def process_pcap(input_file='.pcap', image_width=28, output_dir='./input_data',
                 filter={'IPs': ['0.0.0.0', '255.255.255.255', '224.0.0.252', '131.202.243.255'],
                         'ports': [53, 5355, 5353, 1900, 161, 137, 138, 123, 67, 68, 3478]}):
    """

    :param input_file:
    :param image_width:
    :param output_dir:
    :param filter:
    :return:
    """
    if not input_file.endswith('.pcap') and not input_file.endswith('.pcapng'):
        print(f'Wrong input file type: {input_file}, input must be \'pcap or pcapng\'.')
        return 0
    all_stats_dict, full_sess_dict = pcap2sessions_statistic_with_pcapreader_scapy_improved(input_file)
    print(f"all_stats_dict:{all_stats_dict}")
    # print(f"sess_dict:{sess_dict}")   # there will be huge information, please do print it out.

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for idx, (k, v) in enumerate(full_sess_dict.items()):
        if is_filter(k,filter):
            continue
        line_bytes = b''
        if k == '131.202.240.87:49242-173.194.123.96:443-UDP':
            print(f'k={k}, line_bytes={line_bytes}')
        for pkt in v:  # pkt is IP pakcet, no ethernet header
            line_bytes += pkt.payload.payload.original
        # payload_1d = list(map(lambda x:int(x,16), line_str.split('\\x')))  # change hex to decimal
        output_name = os.path.join(output_dir, k + f'-({len(line_bytes)//image_width}x{image_width}={len(line_bytes)}).png')
        print(f"idx={idx}, output_name:{output_name}")
        # print(f"len(line_bytes)={len(line_bytes)}, ((height,width)={len(line_bytes)//image_width}x{image_width}), {line_bytes}")
        # save_payload_to_image(line_bytes, image_width=image_width,output_name=output_name)
        save_payload_to_image(line_bytes, image_width=image_width, output_name=output_name.replace(':','-')) # for window


def main(input_file='', output_dir='./input_data'):
    """

    :param input_file:
    :param output_dir:
    :return:
    """
    if os.path.isdir(input_file):
        # for file in sorted(os.listdir(input_file)):
        # os.listdir(input_file).sort(key=lambda x: x.lower()) # return Nonetype
        for file in sorted(os.listdir(input_file), key=lambda x:x.lower()):  # sort file name with case-insensitive
            print(f'file={os.path.join(input_file,file)}')
            process_pcap(os.path.join(input_file,file),output_dir=os.path.join(output_dir, os.path.split(file)[1].split('.')[0]))
    else:
        process_pcap(input_file,output_dir=os.path.join(output_dir, os.path.split(input_file)[1].split('.')[0]))



def parse_params():
    """

    :return:
    """
    parser = argparse.ArgumentParser(prog='pcap2image')
    parser.add_argument('-i', '--input_dir', type=str, dest='input_dir', help='directroy includes *.pcaps or *.pcapngs',
                        default='../pcaps_data', required=True)  # '-i' short name, '--input_dir' full name
    parser.add_argument('-o', '--output_dir', dest='output_dir', help="the images",
                        default='./input_data')
    args = vars(parser.parse_args())

    return args


if __name__ == '__main__':
    # input_file = '../pcaps_data/aim_chat_3a.pcap'
    # # pcap2sessions_statistic_with_pcapreader_scapy_improved(input_file)
    # # process_pcap(input_file, output_dir='../input_data/aim_chat_3a')
    # main(input_file='../pcaps_data',output_dir='../input_data/')
    args = parse_params()
    print(args)
    main(input_file=args['input_dir'], output_dir=args['output_dir'])