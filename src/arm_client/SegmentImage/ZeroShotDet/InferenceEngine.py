from .config import SAGSConfig
from .model import SAGSModel

import numpy as np
import cv2
import torch

class inferenceEngine:
    def format_prompt(self, prompt):
        prompt = prompt.strip()
        lowered = prompt.lower()
        if lowered.startswith("a photo"):
            return prompt
        if lowered.startswith(("a ", "an ", "the ")):
            return f"a photo of {prompt}"
        return f"a photo of a {prompt}"

    def __init__(self, 
                 prompt=None, 
                 threshold=0.2,
                 device="cpu",
                 backbone_path="checkpoints/mobileclip_s0.pt",
                 decoder_path="sags/checkpoints/checkpoints/sags_mobileclip_s0_v2_best.pt"
        ):
        state = torch.load(decoder_path, map_location="cpu", weights_only=False)
        self.config = SAGSConfig(**state["config"])
        self.model = SAGSModel(backbone_path, config=self.config, device=device)
        self.model.decoder.load_state_dict(state["decoder"])
        self.device = device
        self.threshold = threshold
        self.model.eval()

        self.cached_prompt = None

        if prompt is not None:
            self.cached_prompt = self.format_prompt(prompt)
        
            with torch.inference_mode():                        # isso aqui joga o prompt pra cache. Ajuda muito em aumentar o fps.
                self.cached_text_features = self.model.backbone.encode_text([self.cached_prompt])

    def predict_frame_bounding_boxes(self, frame:np.ndarray, use_cached=False, prompt=None):
        if use_cached == False and prompt is None or use_cached == True and self.cached_prompt is None:
            raise ValueError("bro ... vc precisa me dar um prompt")
        
        frame_height, frame_width = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (self.config.image_size, self.config.image_size), interpolation=cv2.INTER_CUBIC)
        image_tensor = torch.from_numpy(resized).permute(2, 0, 1).unsqueeze(0).float().div_(255.0)
        image_tensor = image_tensor.to(self.device)

        if use_cached:
            text_features = self.cached_text_features
        else:
            with torch.inference_mode():                   
                text_features = self.model.backbone.encode_text([prompt])

        with torch.inference_mode():
            image_features = self.model.backbone.encode_image(image_tensor)
            logits = self.model.decoder(image_features, text_features,
                                    output_size=(frame_height, frame_width))
            probability = logits.sigmoid()[0, 0].cpu().numpy()

        binary = probability >= self.threshold
        component_count, component_labels, stats, _ = cv2.connectedComponentsWithStats(
            binary.astype(np.uint8), connectivity=8
        )

        boxes = []
        for component in range(1, component_count):
            x, y, width, height, area = stats[component]
            if area >= 8:
                component_mask = component_labels[y:y + height, x:x + width] == component
                component_score = float(probability[y:y + height, x:x + width][component_mask].mean())
                boxes.append((int(x), int(y), int(x + width), int(y + height), component_score))

        boxes.sort(key=lambda box: (box[2] - box[0]) * (box[3] - box[1]), reverse=True)

        return boxes, probability