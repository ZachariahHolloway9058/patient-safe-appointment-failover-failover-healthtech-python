"""Set the account routing preference used by the appointment service."""

import argparse

from infrai_gateway import RoutingControl


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Vendor to exclude; repeat the option for more than one",
    )
    args = parser.parse_args()
    configured = RoutingControl().set_chat_routing(exclude=args.exclude)
    print("Routing configured:", configured)


if __name__ == "__main__":
    main()

