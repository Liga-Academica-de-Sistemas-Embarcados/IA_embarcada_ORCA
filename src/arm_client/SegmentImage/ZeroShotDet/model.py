import torch
import torch.nn as nn

from .backbone import load_frozen_backbone
from .config import SAGSConfig
from .decoder import PromptMaskDecoder

class SAGSModel(nn.Module):
    def __init__(self, checkpoint, config=None, device="cpu"):
        super().__init__()
        self.config = config or SAGSConfig()
        self.backbone = load_frozen_backbone(checkpoint, self.config, device)
        self.decoder = PromptMaskDecoder(self.config).to(device)

    def train(self, mode=True):
        super().train(mode)
        self.backbone.eval()
        return self

    def forward(self, images, prompts):
        with torch.no_grad():
            image_features = self.backbone.encode_image(images)
            text_features = self.backbone.encode_text(prompts)
        return self.decoder(image_features, text_features, output_size=images.shape[-2:])
