import torch
import torch.nn as nn

import mobileclip
from .config import SAGSConfig

class FrozenMobileCLIP(nn.Module):
    def __init__(self, checkpoint, config: SAGSConfig, device="cpu"):
        super().__init__()
        self.config = config
        self.clip, _, self.preprocess = mobileclip.create_model_and_transforms(
            config.model_arch, pretrained=checkpoint, reparameterize=True, device=device
        )
        self.tokenizer = mobileclip.get_tokenizer(config.model_arch)
        self.clip.eval()
        self.clip.requires_grad_(False)

    @property
    def device(self):
        return next(self.clip.parameters()).device

    def encode_text(self, prompts):
        tokens = self.tokenizer(prompts).to(self.device)
        with torch.no_grad():
            return self.clip.encode_text(tokens, normalize=True)

    def encode_image(self, images):
        backbone = self.clip.image_encoder.model
        features = backbone.forward_embeddings(images)
        maps = []
        for index, block in enumerate(backbone.network):
            features = block(features)
            next_is_downsample = (
                index + 1 < len(backbone.network)
                and backbone.network[index + 1].__class__.__name__ == "PatchEmbed"
            )
            if next_is_downsample or index == len(backbone.network) - 1:
                maps.append(features)
        if len(maps) != 4:
            raise RuntimeError(f"faaaaaaaahhhhhhhhhhhhhhhhhhhhhhh")
        return maps

def load_frozen_backbone(checkpoint, config, device):
    return FrozenMobileCLIP(checkpoint, config, device=device).to(device)
