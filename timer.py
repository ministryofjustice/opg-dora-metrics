import argparse
from timer.stopwatch import start, stop, durations


def main() :
    # handle args
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", help="Start timestamp (format: 2024-03-26T08:47:21.029473+00:00)", required=False, type=str)
    parser.add_argument("--stop", help="End timestamp (format: 2024-03-26T08:47:21.029473+00:00)", required=False, type=str)
    args = parser.parse_args()

    duration_data: dict = {}
    # if start is set and we have an forced end, then work out duration
    if args.start is not None and args.stop is not None:
        duration_data = durations(str(args.start), str(args.stop))
        duration_data['start'] = args.start
        duration_data['stop'] = args.stop
    # if just the start time is set then get curret time and work out duration
    elif args.start is not None:
        end: str = stop()
        duration_data = durations(str(args.start),  end)
        duration_data['start'] = args.start
        duration_data['stop'] = end
    # otherwise, output start time
    else:
        duration_data['start'] = start()

    # output all values
    for key, value in duration_data.items():
        print(f'{key}={value}')



if __name__ == "__main__":
    main()
