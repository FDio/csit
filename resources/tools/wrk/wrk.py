"""

"""

from wrk_traffic_profile_parser import WrkTrafficProfile
from wrk_errors import WrkError


def main():
    try:
        profile = WrkTrafficProfile("/home/tibor/ws/vpp/git/csit/resources/traffic_profiles/wrk/example.yaml")
    except WrkError as err:
        print(err)


if __name__ == '__main__':
    main()
