import torch
import torch.nn as nn
import torch.nn.functional as F

from .config import BACKBONE_CHANNELS, TEXT_DIMS, SAGSConfig

class ConvBlock(nn.Sequential):
    def __init__(self, channels):
        super().__init__(
            nn.Conv2d(channels, channels, 3, padding=1, bias=False),
            nn.GroupNorm(8, channels),
            nn.GELU(),
        )

class PromptMaskDecoder(nn.Module):
    def __init__(self, config: SAGSConfig):
        super().__init__()
        width = config.decoder_dim
        self.lateral = nn.ModuleList([
            nn.Sequential(nn.Conv2d(ch, width, 1, bias=False), nn.GroupNorm(8, width))
            for ch in BACKBONE_CHANNELS[config.model_arch]
        ])
        self.smooth = nn.ModuleList([ConvBlock(width) for _ in range(4)])
        self.text_projection = nn.Sequential(
            nn.Linear(TEXT_DIMS[config.model_arch], width), nn.GELU(), nn.Linear(width, width)
        )
        self.fusion = nn.Sequential(
            nn.Conv2d(width * 2, width, 3, padding=1, bias=False),
            nn.GroupNorm(8, width), nn.GELU(), ConvBlock(width),
            nn.Conv2d(width, 1, 1),
        )

    def forward(self, image_features, text_features, output_size=None):
        if len(image_features) != 4:
            raise ValueError("PromptMaskDecoder requere 4 mapas de feature")
        pyramid = [layer(feature) for layer, feature in zip(self.lateral, image_features)]
        fused = pyramid[-1]
        for level in range(2, -1, -1):
            fused = F.interpolate(fused, size=pyramid[level].shape[-2:], mode="bilinear", align_corners=False)
            fused = self.smooth[level](fused + pyramid[level])
        prompt = self.text_projection(text_features).unsqueeze(-1).unsqueeze(-1)
        prompt = prompt.expand(-1, -1, fused.shape[-2], fused.shape[-1])
        logits = self.fusion(torch.cat((fused, prompt), dim=1))
        if output_size is not None:
            logits = F.interpolate(logits, size=output_size, mode="bilinear", align_corners=False)
        return logits
