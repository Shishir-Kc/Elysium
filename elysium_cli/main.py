#!/usr/bin/env python3
""" This file will be the reason for the Cli commands ! """

import argparse

from elysium_cli.commands.elysium_info import (
    cache_info,
    check_version,
    elysium_info,
    is_stable,
    last_development_changes,
    ram_info,
    remove_cache,
    status,
    update,
    version,
    version_name,
)


def build_parser(): 
    parser = argparse.ArgumentParser(prog="romeo")
    subparser = parser.add_subparsers(dest="command")

    version_parser = subparser.add_parser("version",help="gets the current version of E.L.Y.S.I.U.M")
    version_parser.set_defaults(func=version)
   
    status_parser = subparser.add_parser("status",help="gets the current Status of E.L.Y.S.I.U.M")
    status_parser.set_defaults(func=status)

    dev_parser =  subparser.add_parser("dev",help="gets the last development update ")
    dev_parser.set_defaults(func=last_development_changes)
    
    version_name_parser = subparser.add_parser("version-name",help="gets the current version name of E.L.Y.S.I.U.M")
    version_name_parser.set_defaults(func=version_name)

    stable_parser = subparser.add_parser("is-stable",help="checks if current E.L.Y.S.I.U.M is stable or not")
    stable_parser.set_defaults(func=is_stable)

    el_parser = subparser.add_parser("info",help="gets overall info of E.L.Y.S.I.U.M")
    el_parser.set_defaults(func=elysium_info)

    version_checker_parser = subparser.add_parser("check-version",help="Checks if new version is available or not ")
    version_checker_parser.set_defaults(func=check_version)

    update_parser = subparser.add_parser("update",help="Updates E.L.Y.S.I.U.M with the latest relaease")
    update_parser.set_defaults(func=update)
        
    ram_info_parser = subparser.add_parser("ram-info",help="This will show the current system ram and its usages plus swap ")
    ram_info_parser.set_defaults(func=ram_info)

    cache_info_parser = subparser.add_parser("cache-info",help="This will show your curent cache usage ")
    cache_info_parser.set_defaults(func=cache_info)

    remove_cache_parser = subparser.add_parser("rm-cache",help="This will reomve the cache , Needs sudo access")
    remove_cache_parser.set_defaults(func=remove_cache)
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)

if __name__ == "__main__":
    main()
