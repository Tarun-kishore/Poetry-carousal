import math
import random

from PIL import Image, ImageDraw, ImageFilter


class Atmosphere:
    """
    Frame-by-frame atmospheric animation.

    The background itself stays stable. Motion comes from actual
    objects/effects moving across the frame:
      - rain
      - clouds
      - fog
      - floating particles
      - subtle wind movement
      - occasional lightning during storms
    """

    def __init__(self, mood, mode="auto", seed=42):
        self.mood = (mood or "dark").lower()
        self.mode = mode
        self.random = random.Random(seed)

        self.particles = []
        self.rain = []
        self.clouds = []

        self._create_particles()
        self._create_rain()
        self._create_clouds()

    def _multiplier(self):
        if self.mode == "minimal":
            return 0.0
        if self.mode == "cinematic":
            return 1.25
        if self.mode == "atmospheric":
            return 2.25
        return 1.7

    def _create_particles(self):
        counts = {
            "horror": 240,
            "melancholy": 100,
            "ocean": 120,
            "dream": 130,
            "dark": 90,
            "calm": 55,
            "mystery": 110,
        }

        count = int(
            counts.get(self.mood, 35) *
            self._multiplier()
        )

        for _ in range(count):
            self.particles.append({
                "x": self.random.random(),
                "y": self.random.random(),
                "speed": self.random.uniform(0.10, 0.24) if self.mood == "horror" else self.random.uniform(0.045, 0.12),
                "size": self.random.uniform(2, 5) if self.mood in {"horror", "ocean", "dream", "mystery"} else self.random.uniform(1.5, 4),
                "phase": self.random.random() * math.pi * 2,
            })

    def _create_rain(self):
        if self.mood != "storm":
            return

        counts = {
            "minimal": 0,
            "cinematic": 150,
            "atmospheric": 300,
            "auto": 220,
        }

        count = counts.get(self.mode, 145)

        for _ in range(count):
            self.rain.append({
                # Positions are normalized so the same rain system
                # works at any render resolution.
                "x": self.random.uniform(-0.15, 1.15),
                "y": self.random.uniform(-0.15, 1.15),

                # Base speed is normalized screen-height per second.
                "speed": self.random.uniform(0.65, 1.35),

                "length": self.random.uniform(24, 60),
                "width": self.random.choice([1, 1, 2]),

                "alpha": self.random.randint(80, 155),

                # Individual drops are slightly different in angle.
                "angle": self.random.uniform(
                    math.radians(-13),
                    math.radians(-5)
                ),
            })

    def _create_clouds(self):
        if self.mood not in {"storm", "horror", "mystery", "melancholy"}:
            return

        count = {
            "minimal": 0,
            "cinematic": 8,
            "atmospheric": 14,
            "auto": 11,
        }.get(self.mode, 6)

        for _ in range(count):
            self.clouds.append({
                "x": self.random.uniform(-0.35, 1.0),
                "y": self.random.uniform(0.03, 0.38),
                "width": self.random.uniform(0.30, 0.62),
                "height": self.random.uniform(0.08, 0.19),
                "speed": self.random.uniform(0.035, 0.085) if self.mood == "horror" else self.random.uniform(0.008, 0.025),
                "alpha": self.random.randint(65, 105) if self.mood == "horror" else self.random.randint(28, 55),
                "phase": self.random.random() * math.pi * 2,
            })

    def intensity_for_mood(self, progress):
        progress = max(0.0, min(1.0, progress))

        if self.mode == "minimal":
            return 0.0

        if self.mood == "storm":
            # Build toward the middle/late-middle of the poem,
            # then noticeably calm down after the storm passes.
            if progress < 0.18:
                return progress / 0.18 * 0.12

            if progress < 0.62:
                return 0.12 + (
                    (progress - 0.18) / 0.44
                ) * 0.88

            return max(
                0.0,
                1.0 - (
                    (progress - 0.62) / 0.38
                )
            )

        if self.mood == "horror":
            return 1.35 + progress * 0.45

        if self.mood == "melancholy":
            return 0.65 + progress * 0.35

        if self.mood == "ocean":
            return (
                0.75 +
                math.sin(progress * math.pi * 4) * 0.25
            )

        if self.mood == "dream":
            return (
                0.70 +
                math.sin(progress * math.pi * 2) * 0.25
            )

        return 0.65

    def _storm_wind(self, progress):
        """
        Returns wind strength in pixels of horizontal movement
        for a normalized vertical movement.

        The wind increases as the storm builds.
        """
        intensity = self.intensity_for_mood(progress)

        # A slight natural oscillation prevents perfectly mechanical rain.
        gust = (
            0.78 +
            0.22 *
            math.sin(progress * math.pi * 8)
        )

        return 0.22 * intensity * gust

    def draw_clouds(self, image, progress):
        if not self.clouds:
            return image

        intensity = self.intensity_for_mood(progress)

        if intensity <= 0:
            return image

        overlay = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )

        draw = ImageDraw.Draw(overlay)
        width, height = image.size

        for cloud in self.clouds:
            # Slow horizontal movement.
            x_norm = (
                cloud["x"] +
                progress * cloud["speed"]
            ) % 1.55 - 0.35

            y_norm = cloud["y"]

            cx = x_norm * width
            cy = y_norm * height

            cloud_width = cloud["width"] * width
            cloud_height = cloud["height"] * height

            # A few overlapping soft ellipses form a cloud mass.
            wobble = math.sin(
                progress * math.pi * 2 +
                cloud["phase"]
            ) * 4

            for offset in (-0.25, 0.0, 0.25):
                ellipse_x = (
                    cx +
                    offset * cloud_width
                )

                draw.ellipse(
                    (
                        ellipse_x - cloud_width * 0.42,
                        cy - cloud_height * 0.5 + wobble,
                        ellipse_x + cloud_width * 0.42,
                        cy + cloud_height * 0.5 + wobble,
                    ),
                    fill=(
                        12,
                        15,
                        22,
                        int(cloud["alpha"] * intensity)
                    )
                )

        overlay = overlay.filter(
            ImageFilter.GaussianBlur(24)
        )

        return Image.alpha_composite(
            image.convert("RGBA"),
            overlay
        ).convert("RGB")

    def draw_rain(self, image, progress):
        if not self.rain:
            return image

        intensity = self.intensity_for_mood(progress)

        if intensity <= 0:
            return image

        overlay = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )

        draw = ImageDraw.Draw(overlay)
        width, height = image.size

        wind = self._storm_wind(progress)

        for drop in self.rain:
            # Continuous frame-by-frame movement.
            # The modulo keeps drops cycling seamlessly.
            y_norm = (
                drop["y"] +
                progress * drop["speed"]
            ) % 1.30 - 0.15

            # Stronger storm = stronger sideways movement.
            x_norm = (
                drop["x"] +
                progress *
                drop["speed"] *
                wind
            ) % 1.40 - 0.20

            x = x_norm * width
            y = y_norm * height

            length = drop["length"] * (
                0.8 + 0.5 * intensity
            )

            # Rain falls down and slightly sideways.
            dx = (
                math.tan(drop["angle"]) *
                length
            )

            dy = length

            alpha = int(
                drop["alpha"] *
                (0.35 + 0.65 * intensity)
            )

            draw.line(
                (
                    x,
                    y,
                    x + dx + wind * 80,
                    y + dy,
                ),
                fill=(205, 220, 235, alpha),
                width=drop["width"]
            )

        return Image.alpha_composite(
            image.convert("RGBA"),
            overlay
        ).convert("RGB")

    def draw_particles(self, image, progress):
        intensity = self.intensity_for_mood(progress)

        if intensity <= 0:
            return image

        overlay = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )

        draw = ImageDraw.Draw(overlay)
        width, height = image.size

        for particle in self.particles:
            x = particle["x"] * width

            y = (
                particle["y"] +
                progress * particle["speed"]
            ) % 1.0

            y *= height

            sway = math.sin(
                progress * math.pi * 4 +
                particle["phase"]
            )

            x += sway * (85 if self.mood in {"horror", "mystery"} else 38)

            size = particle["size"] * intensity

            if self.mood in {
                "horror",
                "melancholy",
                "dark",
                "mystery",
            }:
                draw.ellipse(
                    (
                        x - size,
                        y - size,
                        x + size,
                        y + size
                    ),
                    fill=(
                        210,
                        210,
                        210,
                        int((155 if self.mood == "horror" else 75) * intensity)
                    )
                )

            elif self.mood == "ocean":
                draw.ellipse(
                    (
                        x - size,
                        y - size,
                        x + size,
                        y + size
                    ),
                    fill=(
                        220,
                        225,
                        235,
                        int(90 * intensity)
                    )
                )

            elif self.mood == "dream":
                draw.ellipse(
                    (
                        x - size * 2,
                        y - size * 2,
                        x + size * 2,
                        y + size * 2
                    ),
                    fill=(
                        235,
                        230,
                        245,
                        int(75 * intensity)
                    )
                )

        return Image.alpha_composite(
            image.convert("RGBA"),
            overlay
        ).convert("RGB")

    def draw_fog(self, image, progress):
        if self.mood not in {
            "horror",
            "melancholy",
            "mystery",
        }:
            return image

        if self.mode == "minimal":
            return image

        intensity = self.intensity_for_mood(progress)

        if intensity <= 0:
            return image

        overlay = Image.new(
            "RGBA",
            image.size,
            (0, 0, 0, 0)
        )

        draw = ImageDraw.Draw(overlay)
        width, height = image.size

        for i in range(14 if self.mood == "horror" else 9):
            phase = (
                progress * math.pi * 2 +
                i
            )

            x = (
                width * 0.5 +
                math.sin(phase) *
                width *
                (0.82 if self.mood == "horror" else 0.58)
            )

            y = (
                height * 0.25 +
                i * height * 0.16
            )

            radius = width * (0.55 if self.mood == "horror" else 0.38)
            alpha = int((105 if self.mood == "horror" else 48) * intensity)

            draw.ellipse(
                (
                    x - radius,
                    y - radius * 0.3,
                    x + radius,
                    y + radius * 0.3
                ),
                fill=(
                    210,
                    210,
                    215,
                    alpha
                )
            )

        overlay = overlay.filter(
            ImageFilter.GaussianBlur(58 if self.mood == "horror" else 42)
        )

        return Image.alpha_composite(
            image.convert("RGBA"),
            overlay
        ).convert("RGB")

    def lightning_flash(self, progress):
        """
        Returns a subtle lightning brightness value.
        Most frames return 0. A few narrow windows return a flash.
        """
        if self.mood != "storm":
            return 0.0

        if self.mode == "minimal":
            return 0.0

        intensity = self.intensity_for_mood(progress)

        # Deterministic flash points. Keeping them fixed means
        # rendering the same poem twice produces the same Reel.
        flash_points = (
            0.47,
            0.54,
            0.69,
        )

        strength = 0.0

        for point in flash_points:
            distance = abs(progress - point)

            # Extremely short flash.
            if distance < 0.006:
                strength = max(
                    strength,
                    (1.0 - distance / 0.006) *
                    0.42 *
                    intensity
                )

        return strength

    def apply(self, image, progress):
        # Clouds are behind the rain.
        image = self.draw_clouds(
            image,
            progress
        )

        image = self.draw_rain(
            image,
            progress
        )

        image = self.draw_particles(
            image,
            progress
        )

        image = self.draw_fog(
            image,
            progress
        )

        flash = self.lightning_flash(progress)

        if flash > 0:
            overlay = Image.new(
                "RGBA",
                image.size,
                (
                    225,
                    230,
                    240,
                    int(255 * flash)
                )
            )

            image = Image.alpha_composite(
                image.convert("RGBA"),
                overlay
            ).convert("RGB")

        return image
