from __future__ import annotations

import argparse

import uvicorn
from edge_platform.control_plane import create_cloud_fixture, create_control_plane


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("service",choices=["control-plane","cloud"]); parser.add_argument("--port",type=int,required=True); args=parser.parse_args()
    uvicorn.run(create_control_plane() if args.service=="control-plane" else create_cloud_fixture(),host="127.0.0.1",port=args.port)
if __name__=="__main__": main()
