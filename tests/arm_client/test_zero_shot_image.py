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
        description="Run zero-shot object detection on an image."
    )
    parser.add_argument("image", type=Path, help="Input image path")
    parser.add_argument(
        "--prompt",
        required=True,
        help="Object to detect, for example: bottle",
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
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path for saving the annotated image",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Do not open an OpenCV window",
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
    frame = cv2.imread(str(args.image))
    if frame is None:
        raise RuntimeError(f"Could not read image: {args.image}")

    engine = inferenceEngine(
        prompt=args.prompt,
        threshold=args.threshold,
        device=args.device,
        backbone_path=str(args.backbone),
        decoder_path=str(args.decoder),
    )
    boxes, _ = engine.predict_frame_bounding_boxes(frame, use_cached=True)
    draw_detections(frame, boxes)

    print(f"{args.prompt}: {len(boxes)} detection(s)")
    for box in boxes:
        print(f"  {box}")

    if args.output is not None and not cv2.imwrite(str(args.output), frame):
        raise RuntimeError(f"Could not write output image: {args.output}")

    if not args.no_display:
        cv2.imshow("Zero-shot image test", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())