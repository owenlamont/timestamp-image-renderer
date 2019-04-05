import argparse
import datetime
import iso8601
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pytz

from pathlib import Path
from matplotlib.animation import FFMpegFileWriter
from typing import List

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 1024


def main(
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    sample_freq: str,
    image_file_path: Path,
    output_file_name: str,
):

    # Read all the satellite images (that are named with a date time) and create a new data series that selects
    # the closest time for the specified frame interval
    image_list: List[Path] = list(image_file_path.glob("*.jpg"))
    image_index: List[pd.Timestamp] = []
    for filepath in image_list:
        file_name: str = os.path.basename(filepath)
        timestamp: pd.Timestamp = pd.Timestamp(
            year=int(file_name[:4]),
            month=int(file_name[4:6]),
            day=int(file_name[6:8]),
            hour=int(file_name[8:10]),
            minute=int(file_name[10:12]),
            tz=pytz.utc,
        )
        image_index.append(timestamp)

    image_df: pd.DataFrame = pd.DataFrame(
        columns=["path"], data=[str(file) for file in image_list], index=image_index
    )

    image_df.sort_index(inplace=True)

    figure = plt.figure(figsize=(10.24, 10.24))
    img_axes = figure.add_axes([0.0, 0.0, 1.0, 1.0])
    clock_axes = figure.add_axes([0.47, 0.055, 0.1, 0.1])

    time_range = pd.date_range(start=start_time, end=end_time, freq=sample_freq)
    file_writer = FFMpegFileWriter(fps=12)
    with file_writer.saving(figure, output_file_name, dpi=100):
        for index, time_stamp in enumerate(time_range):
            img_axes.cla()
            clock_axes.cla()

            # Remove axes from image plots
            img_axes.set_axis_off()
            clock_axes.set_axis_off()

            # Render the image
            image_index = image_df.index.get_loc(time_stamp, method="nearest")
            satellite_image: np.ndarray = plt.imread(image_df.iloc[image_index, 0])
            img_axes.imshow(satellite_image)

            # Render the time of day text
            clock_axes.text(
                0.0,
                0.0,
                f"Datetime\n{time_stamp}",
                fontsize=32,
                horizontalalignment="center",
                color="tomato",
            )

            file_writer.grab_frame()


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "start_time", help="The time to start rendering from as an ISO 8601 string"
    )
    parser.add_argument(
        "end_time", help="The time to stop rendering as an ISO 8601 string"
    )
    parser.add_argument(
        "sample_freq", help="The sample frequency as a Pandas time interval string"
    )
    parser.add_argument("image_file_path", help="The name of the path with the timestamped images")
    parser.add_argument("output_file_name", help="The name of the movie file to output")
    args = parser.parse_args()
    main(
        iso8601.parse_date(args.start_time),
        iso8601.parse_date(args.end_time),
        args.sample_freq,
        Path(args.image_file_path),
        args.output_file_name,
    )
