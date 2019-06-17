import argparse

from collector import WORKER


def run(args):
    acc = {"x-rh-identity": args.b64_identity, 'account_id': args.account_id}
    WORKER(None, args.job_id or 'N/A', args.output_path, acc)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # arguments
  parser.add_argument(
      '--account_id', type=str, required=True, help='Account ID'
  )
  parser.add_argument(
      '--b64_identity', type=str, required=True, help='b64_identity'
  )
  parser.add_argument(
      '--output_path', type=str, required=True, help='output path'
  )
  parser.add_argument(
      '--job_id', type=str, required=True, help='Job ID'
  )

  # Parse all arguments
  args = parser.parse_args()
  
run(args)
