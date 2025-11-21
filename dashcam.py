from datetime import datetime
import logging
import cv2
import sys
from nmea import input_stream, nmea_message, data_frame
import config


RECORD_VIDEO = True
DEBUG_MODE = True


def get_location():
    la = None
    lo = None
    vel = 0
    try:
        gps_stream = input_stream.GenericInputStream.open_stream(path=config.gps_port, baud=config.gps_baudrate)
        gps_frame = data_frame.DataFrame.get_next_frame(gps_stream)
        la = gps_frame.latitude
        lo = gps_frame.longitude
        vel = gps_frame.velocity
        gps_stream.ensure_closed()
    except Exception as ex:
        print(f'Error opening GPS stream: {ex}')
        la = None
        lo = None
        vel = 0
    return la, lo, vel

def create_video_file(width=640, height=480, fps=30):
    logging.debug('Recording is enabled')
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    stamp = datetime.now()
    out = cv2.VideoWriter(f'{config.video_path}/{stamp.strftime("%Y%m%d%H%M%S")}.avi',
                          fourcc,
                          fps,
                          (int(width), int(height)))
    if out is None:
        logging.error('Storage open failed.  Skipping save')
    return out


if __name__ == "__main__":
    if DEBUG_MODE:
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARN)
    logging.debug('Starting up')
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error('Cannot access camera device')
        exit()
    font = cv2.FONT_HERSHEY_SIMPLEX
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    lat,lon, vel = get_location()
    logging.debug(f'Width={width}, Height={height}, FPS={fps}')
    vpos = int(height) - 10
    if RECORD_VIDEO:
        """
        logging.debug('Recording is enabled')
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        stamp = datetime.now()
        out = cv2.VideoWriter(f'{config.video_path}/{stamp.strftime("%Y%m%d%H%M%S")}.avi',
                              fourcc,
                              fps,
                              (int(width), int(height)))
        if out is None:
            logging.error('Storage open failed.  Skipping save')
            RECORD_VIDEO = False
        """
        out = create_video_file(width=width, height=height, fps=fps)
        if out is None:
            RECORD_VIDEO = False
    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error('Error getting frame from camera')
            break
        else:
            dt = datetime.now()
            cv2.line(frame,
                     (0, int(height - 15)),
                     (int(width), int(height-15)),
                     (255, 255, 255),
                     15)
            if lat is None:
                strText = f'{dt.strftime("%d-%b-%Y %H:%M:%S")} - GPS Error?'
            else:
                strText = f'{dt.strftime("%d-%b-%Y %H:%M:%S")} | {lat:.3f}, {lon:.3f} | {(vel/1.582):.1f}Km/h'
            cv2.putText(frame,
                        strText,
                        (25, vpos),
                        font,
                        0.5,
                        (0, 0, 0),
                        1,
                        cv2.LINE_4
            )
            cv2.imshow('frame', frame)
            if RECORD_VIDEO:
                out.write(frame)
            if cv2.waitKey(1) == ord('q'):
                logging.debug('Shutdown requested from console')
                break
    cap.release()
    if RECORD_VIDEO:
        out.release()
    cv2.destroyAllWindows()
    logging.debug('Shutdown completed')
