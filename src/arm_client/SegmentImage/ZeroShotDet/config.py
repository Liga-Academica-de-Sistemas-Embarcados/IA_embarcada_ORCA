from dataclasses import asdict, dataclass

BACKBONE_CHANNELS = {
    "mobileclip_s0": (64, 128, 256, 512),
    "mobileclip_s1": (64, 128, 256, 512),
    "mobileclip_s2": (80, 160, 320, 640),
}

TEXT_DIMS = {"mobileclip_s0": 512, "mobileclip_s1": 512, "mobileclip_s2": 512}

@dataclass
class SAGSConfig:
    model_arch: str = "mobileclip_s0"
    image_size: int = 256
    decoder_dim: int = 128

    def __post_init__(self):
        if self.model_arch not in BACKBONE_CHANNELS:
            raise ValueError()
        if self.image_size < 32 or self.decoder_dim < 16 or self.decoder_dim % 8:
            raise ValueError()

    def to_dict(self):
        return asdict(self)
