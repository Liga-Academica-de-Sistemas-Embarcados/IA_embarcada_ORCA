# teste feito por IA. Verifiquei que funciojna (acvmg)

import argparse
import sys
from pathlib import Path

import cv2

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SEGMENT_IMAGE_DIR = REPOSITORY_ROOT / "src" / "arm_client" / "SegmentImage"
if str(SEGMENT_IMAGE_DIR) not in sys.path:
    sys.path.insert(0, str(SEGMENT_IMAGE_DIR))

from ZeroShotDet.InferenceEngine import inferenceEngine

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run zero-shot object detection on a webcam stream."
    )
    parser.add_argument(
        "--prompt", 
        help="Object to detect, for example: bottle")
    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="OpenCV camera index (default: 0)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.2,
        help="Segmentation threshold between 0 and 1 (default: 0.2)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Torch device, for example cpu or cuda (default: cpu)",
    )
    parser.add_argument(
        "--backbone",
        type=Path,
        default=SEGMENT_IMAGE_DIR / "weights" / "mobileclip_s0.pt",
        help="MobileCLIP checkpoint path",
    )
    parser.add_argument(
        "--decoder",
        type=Path,
        default=SEGMENT_IMAGE_DIR / "weights" / "sags_mobileclip_s0_v2.pt",
        help="SAGS decoder checkpoint path",
    )
    args = parser.parse_args()
    if not 0 <= args.threshold <= 1:
        parser.error("--threshold must be between 0 and 1")
    return args

def draw_detections(frame, boxes):
    for x1, y1, x2, y2, score in boxes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"{score:.2f}",
            (x1, max(y1 - 8, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )


def main() -> int:
    args = parse_args()

    engine = inferenceEngine(
        prompt=args.prompt,
        threshold=args.threshold,
        device=args.device,
        backbone_path=str(args.backbone),
        decoder_path=str(args.decoder),
    )

    camera = cv2.VideoCapture(args.camera)
    if not camera.isOpened():
        raise RuntimeError(f"Could not open camera {args.camera}")

    window_name = "Zero-shot webcam test"
    try:
        while True:
            success, frame = camera.read()
            if not success:
                raise RuntimeError("Could not read a frame from the webcam")

            boxes, _ = engine.predict_frame_bounding_boxes(
                frame, use_cached=True
            )
            
            draw_detections(frame, boxes)
            cv2.putText(
                frame,
                f"{args.prompt} | detections: {len(boxes)} | press q or Esc to quit",
                (10, 28),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    raise SystemExit(main())
