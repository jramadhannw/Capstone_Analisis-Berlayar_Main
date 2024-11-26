"""Near-shore Wave Tracking module.

A module for recognition and tracking of multiple nearshore waves
from input videos.

Performance:
mwt.py achieves realtime inference in the presence of multiple tracked
objects for input videos of 1280x720 that are downscaled by a factor of
four at runtime on consumer hardware.

System                       | Step Time (sec/frame)  | Performance
--------------------------------------------------------------------
1 CPU 2.6 GHz Intel Core i5  | 0.015 - 0.030          | 30Hz - 60Hz

Usage:
    Please see the README for how to compile the program and run the model.

Created by Justin Fung on 9/1/17.

Copyright 2017 justin fung. All rights reserved.
"""
from __future__ import division
import argparse
import sys
import time
import cv2
import mwt_detection
import mwt_preprocessing
import mwt_tracking
import mwt_io

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    "--camera", action="store_true", help="use webcam as video input"
)
arg_parser.add_argument(
    "--ip", type=str, help="IP address of the camera (e.g., http://192.168.1.64/video)"
)

def status_update(frame_number, tot_frames):
    """Update status to stdout."""
    if frame_number == 1:
        sys.stdout.write("Starting analysis of %d frames...\n" % tot_frames)
        sys.stdout.flush()

    if frame_number % 100 == 0:
        sys.stdout.write("%d" % frame_number)
        sys.stdout.flush()
    elif frame_number % 10 == 0:
        sys.stdout.write(".")
        sys.stdout.flush()

    if frame_number == tot_frames:
        print("End of video reached successfully.")

    return

def analyze(video, write_output=True):
    """Analyze the video."""
    tracked_waves = []
    recognized_waves = []
    wave_log = []
    frame_num = 1
    last_frame = None  # Store the previous frame
    num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) if video.isOpened() else float('inf')

    if write_output:
        out = mwt_io.create_video_writer(video)

    time_start = time.time()

    while True:
        # Update status with current frame number
        status_update(frame_num, num_frames)

        successful_read, original_frame = video.read()
        if not successful_read:
            break

        # Preprocess the original frame for analysis
        analysis_frame = mwt_preprocessing.preprocess(original_frame)

        # Detect sections in the analysis frame
        sections = mwt_detection.detect_sections(analysis_frame, frame_num)

        # Track the waves using the analysis frame, last frame, and current frame number
        mwt_tracking.track(tracked_waves, analysis_frame, frame_num, last_frame)

        # Log wave data for recognized waves
        for wave in tracked_waves:
            wave_log.append(
                (
                    frame_num,
                    wave.name,
                    wave.mass,
                    wave.max_mass,
                    wave.displacement,
                    wave.max_displacement,
                    wave.birth,
                    wave.death,
                    wave.recognized,
                    wave.centroid,
                )
            )

        # Update last_frame for next iteration
        last_frame = analysis_frame.copy()

        # Process waves that have died
        dead_recognized_waves = [
            wave for wave in tracked_waves if wave.death is not None and wave.recognized is True
        ]
        recognized_waves.extend(dead_recognized_waves)
        tracked_waves = [wave for wave in tracked_waves if wave.death is None]

        # Sort and handle merging of waves
        tracked_waves.sort(key=lambda x: x.birth, reverse=True)
        for wave in tracked_waves:
            other_waves = [wav for wav in tracked_waves if wav != wave]
            if mwt_tracking.will_be_merged(wave, other_waves):
                wave.death = frame_num
        tracked_waves = [wave for wave in tracked_waves if wave.death is None]
        tracked_waves.sort(key=lambda x: x.birth, reverse=False)

        # Add new sections to tracked waves if they are not merging
        for section in sections:
            if not mwt_tracking.will_be_merged(section, tracked_waves):
                tracked_waves.append(section)

        # Optionally write output video
        if write_output:
            original_frame = mwt_io.draw(
                tracked_waves,
                original_frame,
                1 / mwt_preprocessing.RESIZE_FACTOR,
            )
            cv2.imshow("Wave Detection", original_frame)

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        frame_num += 1

    # Calculate performance metrics
    time_elapsed = time.time() - time_start
    performance = num_frames / time_elapsed

    # Print recognized waves and performance
    if recognized_waves:
        print(f"{len(recognized_waves)} wave(s) recognized.")
        print("Program performance: %0.1f frames per second." % performance)
        for i, wave in enumerate(recognized_waves):
            print(
                f"[Wave #{i + 1}] "
                f"ID: {wave.name}, "
                f"Birth: {wave.birth}, "
                f"Death: {wave.death}, "
                f"Max Displacement: {wave.max_displacement}, "
                f"Max Mass: {wave.max_mass}"
            )
    else:
        print("No waves recognized.")

    # Release output video if writing
    if write_output:
        out.release()

    return recognized_waves, wave_log, performance

def main():
    """Define main."""
    args = arg_parser.parse_args()

    if args.camera:
        print("Using webcam as video input.")
        inputvideo = cv2.VideoCapture(0)  # Use 0 for default webcam
    elif args.ip:
        print(f"Using IP camera at {args.ip}.")
        inputvideo = cv2.VideoCapture(args.ip)
    else:
        sys.exit("No input source specified. Use --camera or --ip <ip_address>.")

    print("Checking video input...")
    if not inputvideo.isOpened():
        sys.exit("Could not open video. Exiting.")

    recognized_waves, wave_log, program_speed = analyze(inputvideo, write_output=True)

    mwt_io.write_log(wave_log, output_format="json")
    mwt_io.write_report(recognized_waves, program_speed)

    inputvideo.release()
    cv2.destroyAllWindows()  # Close all OpenCV windows

if __name__ == "__main__":
    main()
